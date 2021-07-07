from striplog import Lexicon, Striplog, Legend, Interval, Decor, Component
from utils.omf import striplog_legend_to_omf_legend
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from utils.omf import build_bh3d_legend_cmap
from copy import deepcopy
import re
import omfvista as ov
import pyvista as pv
import omf
from vtk import vtkX3DExporter # NOQA
from IPython.display import HTML
from utils.config import DEFAULT_ATTRIB_VALUE
from utils.utils import find_component_from_attrib, plot_from_striplog


class Borehole3D(Striplog):
    """
    Borehole object based col striplog object that can be displayed in a 3D environment
    
    Attributes
    -----------
    name : str
    intervals : list
    geometry : list of omf.lineset.LineSetGeometry objects
    legend : Striplog Legend object
    omf_legend : list of omf.data.Legend 
    omf_cmap : list of matplotlib colormap
    x_collar : float
    y_collar : float
    z_collar : float

    Methods
    --------
    get_components_indices()
    build_geometry()
    commit()
    add_components(components)
    plot3d(x3d=False)
    """

    def __init__(self, intervals=None, repr_attribute='lithology', name='BH3D',
                 diam=0.5, length=0, x_collar=0., y_collar=0., z_collar=None, legend_dict=None,
                 compute_all_legend=True, verbose=False):
        """
        build a Borehole3D object from Striplog.Intervals list
        
        Parameters
        -----------
        intervals : list
            list of Striplog.Interval objects (default = None)

        name : str
        legend : Striplog Legend object (default = None)
        x_collar : float
            X coordinate of the borehole (default = 0)
        y_collar : float
            Y coordinate of the borehole (default = 0)
        z_collar : float
            Z coordinate of the borehole (default = 0)
        diam : float
            diameter of the borehole (default = 0.5)
        length : float
            length of the borehole (default = 0)
        verbose : False or str ('geom', 'get_comp', 'build_leg', 'plot3d', 'plot2d')
        """

        self.name = name
        self.x_collar = x_collar
        self.y_collar = y_collar
        self.z_collar = z_collar
        self.diameter = diam
        self.length = length
        self.legend_dict = deepcopy(legend_dict)  # not alter given legend_dict
        self._repr_attribute = repr_attribute  # given repr_attribute
        self.geometry = None
        self._vtk = None
        self.__verbose__ = verbose  # checking outputs

        if self.__verbose__:
            print(f'\n************************ CREATION OF {self.name} *************************')

        if intervals is None:
            if length <= 0.:
                raise (ValueError("Cannot create a borehole without length and interval !"))
            else:
                lexicon = Lexicon.default()
                intervals = [Interval(top=0, base=length, lexicon=lexicon,
                                      description=DEFAULT_ATTRIB_VALUE)]
                print(f"No intervals given, default interval is used, "
                      f"with lithology ({DEFAULT_ATTRIB_VALUE})!\n")

        self.intervals = intervals

        if self.z_collar is None and self.intervals is not None:
            self.update_z_collar_from_intervals()

        if legend_dict is None or not isinstance(legend_dict[repr_attribute]['legend'], Legend):
            print("No given legend or incorrect format ! Default is used")
            self.legend_dict[repr_attribute]['legend'] = Legend.default()

        # instantiation with supers properties
        Striplog.__init__(self, list_of_Intervals=self.intervals)

        # create object legend
        build_bh3d_legend_cmap(bh3d_list=[self], legend_dict=self.legend_dict, verbose=self.__verbose__,
                               compute_all=compute_all_legend, update_bh3d_legend=True)

        self.omf_legend = striplog_legend_to_omf_legend(self.legend_dict[repr_attribute]['legend'])[0]
        self._geometry(verbose=verbose)
        self.vtk()

    # ------------------------------------ Properties ----------------------------
    @property
    def repr_attribute(self):
        return self._repr_attribute

    @repr_attribute.setter
    def repr_attribute(self, value):
        assert (isinstance(value, str))
        self._repr_attribute = value

    @property
    def attrib_components(self):
        # components according to the repr_attribute
        return self.get_attrib_components_dict(self.__verbose__)[self.repr_attribute]

    @property
    def components(self):
        # all components in each interval as a dict like {interval_number: components_list}
        return {i: intv.components for i, intv in enumerate(self.intervals)}

    # ----------------------------------- Methods ------------------------------------------
    def get_attrib_components_dict(self, verbose=False):
        # compute a dict of components for all attributes found in legend_dict

        verb = False
        if verbose:
            verb = 'get_attrib'

        comp_attrib_dict = {}
        for attr in self.legend_dict.keys():
            attr_components = []  # correct components order (not self.components)
            for i in self.intervals:
                j = find_component_from_attrib(i, attr, verbose=verb)
                if j == -1:  # add default component if none
                    attr_components.append(Component({attr: DEFAULT_ATTRIB_VALUE}))
                else:
                    attr_components.append(i.components[j])
            comp_attrib_dict.update({attr: [attr_components[i] for i in range(len(attr_components)) \
                                            if attr in attr_components[i].keys()]})

        return comp_attrib_dict

    def _geometry(self, verbose=False):
        """
        build an omf.LineSetElement geometry of the borehole

        Returns
        --------
        geometry : omf.lineset.LineSetGeometry
            Contains spatial information of a line set
        """
        verb = False
        if verbose:
            verb = 'geom'  # verbose value to output information in this function

        vertices, segments = [], []
        for i in self.intervals:
            if i.top not in vertices:
                if hasattr(i.top, 'x') and hasattr(i.top, 'y') and hasattr(i.top, 'z'):
                    x = i.top.x
                    y = i.top.y
                    z = i.top.z
                else:
                    x = self.x_collar
                    y = self.y_collar
                    z = self.z_collar - i.top.z
                vertices.append([x, y, z])
                top = len(vertices) - 1
            else:
                top = vertices.index(i.top)

            if i.base not in vertices:
                if hasattr(i.base, 'x') and hasattr(i.base, 'y') and hasattr(i.top, 'z'):
                    x = i.base.x
                    y = i.base.y
                    z = i.base.z
                else:
                    x = self.x_collar
                    y = self.y_collar
                    z = self.z_collar - i.base.z
                vertices.append([x, y, z])
                base = len(vertices) - 1
            else:
                base = vertices.index(i.base)

            segments.append([top, base])

        vertices = np.array(vertices)

        # Compute MappedData objects based on attributes in the legend dict
        data = []
        for attr in self.legend_dict.keys():
            array = omf.ScalarArray(self.get_components_indices(repr_attribute=attr, verbose=verbose))
            if verbose and verb in verbose:
                print(f"\ngeom | {attr}_legend: {self.legend_dict[attr]['legend']}")
            legend = striplog_legend_to_omf_legend(self.legend_dict[attr]['legend'])[0]
            data.append(omf.MappedData(name=attr, array=array, legends=[legend],
                                       location='segments', description=''))

        self.geometry = omf.LineSetElement(
            name=self.name, geometry=omf.LineSetGeometry(vertices=vertices, segments=segments),
            data=data)

        print("Borehole geometry created successfully !")

        # return self._geometry

    def vtk(self, radius=None, res=50):
        """ build a vtk tube of given radius based on the borehole geometry """
        if radius is None:
            radius = self.diameter/2 * 5  # multiply for visibility
            vtk_obj = ov.line_set_to_vtk(self.geometry).tube(radius=radius, n_sides=res)
            vtk_obj.set_active_scalars(self.repr_attribute.lower())
            self._vtk = vtk_obj
        return self._vtk

    def get_components_indices(self, repr_attribute=None, intervals=None, verbose=False):
        """
        retrieve components indices from borehole's intervals

        repr_repr_attribute: str
            attribute to consider when retrieving intervals components indices (e.g: 'lithology')

        intervals : List of Striplog.Interval object

        Returns
        --------
        array of indices
        """
        verb = 'get_comp'
        if repr_attribute is None:
            repr_attribute = self.repr_attribute
        if intervals is None:
            intervals = self.intervals

        if verbose and verb in verbose:
            print(f'\n~~~~~~~~~~~~~~~~~~ {repr_attribute} ~~~~~~~~~~~~~~~~~~~~~~')
        components = []  # [Component({repr_attribute: DEFAULT_ATTRIB_VALUE})]  # begin with default component
        for i in intervals:
            j = find_component_from_attrib(i, repr_attribute, verbose=verb)

            if j == -1:  # add default component if none
                print(f'\n//// {j}, {components}, {i.components}\n')
                components.append(Component({repr_attribute: DEFAULT_ATTRIB_VALUE}))
            else:
                components.append(i.components[j])
        comp_list = list(pd.unique([c[repr_attribute] for c in components]))

        indices = []
        incr = 0
        for i in intervals:
            j = find_component_from_attrib(i, repr_attribute, verbose=verb)
            indices.append(comp_list.index(i.components[j][repr_attribute]))

            if verbose and verb in verbose:
                print(f'get_comp | uniq_comp_list: {comp_list}, n_intv:{incr}, ind_val: {j}, comp: {i.components[j][repr_attribute]}')

            incr += 1

        if verbose and verb in verbose:
            print(f'\nget_comp | comp_indices: {np.array(indices)}')
        return np.array(indices)

    def update_z_collar_from_intervals(self):
        """
        updates z_collar assuming that collar is at the top elevation of the highest interval
        """
        self.z_collar = max([i.top.z for i in self.intervals])

    def plot3d(self, plotter=None, repr_legend_dict=None, repr_attribute='lithology',
               repr_cmap=None, repr_uniq_val=None, x3d=False, diam=None,
               bg_color=["royalblue", "aliceblue"], update_vtk=False,
               update_cmap=False, custom_legend=False, str_annotations=True,
               scalar_bar_args=None, verbose=False):
        """
        Returns an interactive 3D representation of all boreholes in the project

        Parameters
        -----------
        plotter : pyvista.plotter object
            Plotting object to display vtk meshes or numpy arrays (default=None)

        x3d : bool
            If True, generates a 3xd file of the 3D (default=False)

        diam: float
            Borehole representation diameter

        update_vtk : bool
            If True, updates vtk objects

        """

        if plotter is None:
            plotter = pv.Plotter()
            show = True
        else:
            show = False

        if diam is None and self.diameter == 0:
            diam = 0.5
        elif diam is None and self.diameter != 0:
            diam = self.diameter

        if update_vtk or diam is not None:
            seg = self.vtk(radius=(diam/2)*5)
        else:
            seg = self._vtk
        seg.set_active_scalars(repr_attribute.lower())

        if repr_legend_dict is None:
            repr_legend_dict = self.legend_dict
            if 'cmap' not in repr_legend_dict[repr_attribute].keys() \
                    or 'values' not in repr_legend_dict[repr_attribute].keys():
                print('Colormap computing and unique values searching ...')
                synth_legend = build_bh3d_legend_cmap(bh3d_list=[self],
                        repr_attrib_list=[repr_attribute], legend_dict=repr_legend_dict,
                        update_bh3d_legend=update_cmap)[0]
                plot_cmap = synth_legend[repr_attribute]['cmap']
                uniq_attr_val = synth_legend[repr_attribute]['values']
            else:
                plot_cmap = repr_legend_dict[repr_attribute]['cmap']
                uniq_attr_val = repr_legend_dict[repr_attribute]['values']
        else:
            plot_cmap = repr_legend_dict[repr_attribute]['cmap']
            uniq_attr_val = repr_legend_dict[repr_attribute]['values']

        if repr_cmap is not None:
            plot_cmap = repr_cmap
        if repr_uniq_val is not None:
            uniq_attr_val = repr_uniq_val

        # display attribute values (string) as a legend
        if str_annotations:
            n_col = len(plot_cmap.colors)
            if scalar_bar_args is None:  # scalar_bar properties
                scalar_bar_args = dict(title=repr_attribute.upper(), title_font_size=25,
                        label_font_size=8, n_labels=n_col, fmt='', font_family='arial',
                        color='k', italic=False, bold=False, interactive=True,
                        vertical=False, shadow=False)
            incr = (len(uniq_attr_val) - 1)/n_col  # increment
            bounds = [0]  # cmap colors limits
            next_bound = 0
            for i in range(n_col+1):
                if i < n_col:
                    next_bound += incr
                    bounds.append(bounds[0] + next_bound)
            bounds.append(n_col)  # add cmap last value (limit)
            centers = [(bounds[i] + bounds[i + 1])/2 for i in range(n_col)]
            str_annot = {k: v.capitalize() for k, v in zip(centers, uniq_attr_val)}
        else:  # numeric values plot
            scalar_bar_args = None
            str_annot = None

        if verbose:
            print(f'plot3d | n_colors: {n_col} | incr: {incr}| unique: {uniq_attr_val}'
              f'\nannotations: {str_annot}')

        plotter.add_mesh(seg, cmap=plot_cmap, scalar_bar_args=scalar_bar_args,
                         show_scalar_bar=not custom_legend, annotations=str_annot)

        if custom_legend:
            plotter.add_scalar_bar(title=repr_attribute.upper(), title_font_size=25, n_labels=0,
                        label_font_size=8, fmt='', font_family='arial', color='k', italic=False,
                        bold=False, interactive=True, vertical=True, shadow=False)

        # set background color for the render (None : pyvista default background color)
        if bg_color is not None:
            if len(bg_color) == 2:
                top_c = bg_color[1]
                btm_c = bg_color[0]
            elif len(bg_color) == 1:
                top_c = None
                btm_c = bg_color
            else:
                raise(ValueError('bg_color must be a color string or a list of 2 colors strings !'))

            plotter.set_background(color=btm_c, top=top_c)

        if show and not x3d:
            plotter.show()
        else:
            writer = vtkX3DExporter()
            writer.SetInput(plotter.renderer.GetRenderWindow())
            filename = f'tmp_files/BH_{self.name:s}.x3d'
            writer.SetFileName(filename)
            writer.Update()
            writer.Write()
            x3d_html = f'<html>\n<head>\n    <meta http-equiv="X-UA-Compatible" content="IE=edge"/>\n' \
                       '<title>X3D scene</title>\n <p>' \
                       '<script type=\'text/javascript\' src=\'http://www.x3dom.org/download/x3dom.js\'> </script>\n'\
                       '<link rel=\'stylesheet\' type=\'text/css\' href=\'http://www.x3dom.org/download/x3dom.css\'/>\n'\
                       '</head>\n<body>\n<p>\n For interaction, click in the view and press "a" or "i" to see the whole scene, ' \
                       '"d" to display info, "space" for shortcuts. For more info col interaction,' \
                       ' please read  <a href="https://doc.x3dom.org/tutorials/animationInteraction/' \
                       'navigation/index.html">the docs</a>  \n</p>\n' \
                       '<x3d width=\'968px\' height=\'600px\'>\n <scene>\n' \
                       '<viewpoint position="-3.03956 -14.95776 2.17179"' \
                       ' orientation="0.98276 -0.08411 -0.16462 1.15299">' \
                       '</viewpoint>\n <Inline nameSpaceName="Borehole" ' \
                       'mapDEFToID="true" url="' + filename + '" />' \
                                                              '\n</scene>\n</x3d>\n</body>\n</html>\n'
            return HTML(x3d_html)

    def log_plot(self, figsize=(6, 6), repr_legend=None, text_size=15, width=3, repr_attribute='lithology', verbose=False):
        """
        Plot a 2D log for the attribute
        """

        if repr_legend is None:
            repr_legend = self.legend_dict[repr_attribute]['legend']

        legend_copy = deepcopy(repr_legend)  # work with a copy to keep initial legend state
        decors = {}  # dict of decors to build a own legend for the borehole
        attrib_values = []  # list of lithologies in the borehole

        for i in self.intervals:
            j = find_component_from_attrib(i, repr_attribute, verbose=verbose)
            intv_value = i.components[j][repr_attribute]
            if verbose:
                print(f'plot2d | intv_value: {intv_value} | comp: {i.components[j]}')
            # if intv_value is None:  # attribute not found in the component
            #     i.components[j][repr_attribute] = DEFAULT_ATTRIB_VALUE
            #     i.description = ' '.join([i.components[j][k] for k in i.components[j].keys()])
            #     intv_value = DEFAULT_ATTRIB_VALUE
            if isinstance(intv_value, str):
                intv_value = intv_value.lower()
            attrib_values.append(intv_value or DEFAULT_ATTRIB_VALUE)

        attrib_values = list(pd.unique(attrib_values))  # to treat duplicate values
        for i in range(len(legend_copy)):
            leg_value = legend_copy[i].component[repr_attribute]
            if verbose:
                print('plot2d | legend_val:', leg_value)
            if leg_value is None:  # attribute not found in legend component
                legend_copy[i].component[repr_attribute] = DEFAULT_ATTRIB_VALUE
                leg_value = DEFAULT_ATTRIB_VALUE
            reg = re.compile("^{:s}$".format(leg_value), flags=re.I)
            reg_value = list(filter(reg.match, attrib_values))  # find value that matches

            if len(reg_value) > 0:
                # force matching to plot
                legend_copy[i].component = Component({repr_attribute: reg_value[0]})
                legend_copy[i].width = width
                # use interval order to obtain correct plot legend order
                decors.update({attrib_values.index(reg_value[0]): legend_copy[i]})

        if verbose:
            print('plot2d | decors:', decors)
        rev_decors = list(decors.values())
        rev_decors.reverse()
        plot_legend = Legend([v for v in rev_decors])

        fig, ax = plt.subplots(ncols=2, figsize=figsize)
        ax[0].set_title(self.name, size=text_size, color='b')
        plot_from_striplog(self, legend=plot_legend, match_only=[repr_attribute], ax=ax[0])
        ax[1].set_title('Legend', size=text_size, color='r')
        plot_legend.plot(ax=ax[1])
