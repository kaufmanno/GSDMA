from striplog import Striplog, Legend, Component
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from copy import deepcopy
import re
import omfvista as ov
import pyvista as pv
import omf
from vtk import vtkX3DExporter  # NOQA
from IPython.display import HTML
from utils.config import WARNING_TEXT_CONFIG, X3D_HTML
from utils.visual import find_component_from_attrib, plot_from_striplog, build_bh3d_legend_cmap, striplog_legend_to_omf_legend


class Borehole3D(Striplog):
    """
    Borehole object based on striplog.Striplog object that can be displayed in a 3D environment

    Attributes
    -----------
    name : str
    intervals : list
    geometry : list of omf.lineset.LineSetGeometry objects
    legend : Striplog.Legend object
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

    def __init__(self, intervals=None, repr_attribute='borehole_type', name='BH3D', diam=0.5, length=0.1, date=None, legend_dict=None, verbose=False, **kwargs):
        """
        build a Borehole3D object from Striplog.Intervals list

        Parameters
        -----------
        intervals_dict : dict
            dictionary containing list of Striplog.Interval objects
        name : str
        legend_dict : dict
            dictionary of Striplog Legend objects (default = None)
        x_collar : float
            X coordinate of the borehole (default = 0)
        y_collar : float
            Y coordinate of the borehole (default = 0)
        z_collar : float
            Z coordinate of the borehole (default = 0)
        diam : float
            diameter of the borehole (default = 0.5)
        length : float
            length of the borehole (default = 0.1)
        verbose : False or str ('geom', 'get_comp', 'build_leg', 'plot3d', 'plot2d')
        """

        # ------------------ Class attributes ----------------------------------------
        self.name = name
        self.diameter = diam
        self.date = date
        self.length = length
        self.legend_dict = deepcopy(legend_dict)  # not to alter given legend_dict
        self._repr_attribute = repr_attribute  # given repr_attribute
        self.geometry = None
        self._vtk = None
        self.__verbose__ = verbose  # checking outputs

        if self.__verbose__:
            print(f'\n************************ CREATION OF {self.name} *************************')

        self.intervals = intervals


        if legend_dict is None or not isinstance(legend_dict[repr_attribute]['legend'], Legend):
            print(f"{WARNING_TEXT_CONFIG['blue']}"
                  f"No given legend or incorrect format ! Using the default one..."
                  f"{WARNING_TEXT_CONFIG['off']}")
            self.legend_dict = {repr_attribute: {'lexicon': None, 'legend': None}}

        # instantiation with super properties
        Striplog.__init__(self, list_of_Intervals=self.intervals)
        x_coord = self.intervals[0].top.x if hasattr(self.intervals[0].top, 'x') else None
        y_coord = self.intervals[0].top.y if hasattr(self.intervals[0].top, 'y') else None
        z_coord = self.intervals[0].top.z if hasattr(self.intervals[0].top, 'z') else None
        self.x_collar = kwargs.pop('x_collar', x_coord)
        self.y_collar = kwargs.pop('y_collar', y_coord)
        self.z_collar = kwargs.pop('z_collar', z_coord)
        if self.z_collar is None and self.intervals is not None:
            self.update_z_collar()
        self.omf_legend = striplog_legend_to_omf_legend(self.legend_dict[repr_attribute]['legend'])[0]
        self._geometry(verbose=verbose)
        self.vtk()

    # ------------------------------- Class Properties ----------------------------
    @property
    def repr_attribute(self):
        return self._repr_attribute

    @repr_attribute.setter
    def repr_attribute(self, value):
        assert (isinstance(value, str))
        self._repr_attribute = value

    @property
    def components(self):
        # all components in each interval as a dict like {interval_number: components_list}
        return {i: intv.components for i, intv in enumerate(self.intervals)}

    # -------------------------------- Class Methods ------------------------------
    def __repr__(self):
        n_intv = len(self._Striplog__list)
        if self.stop.z < self.start.z:
            start = self.start.z
            stop = self.stop.z
        else:
            stop = self.start.z
            start = self.stop.z
        details = "start={:.2f}".format(start) + ", stop={:.2f}".format(stop)
        obj_class = str(self.__class__).strip('"<class>"').strip("' ")
        return f"<{obj_class}> name: {self.name} | length:" + '{:.2f} m'.format(start - stop) + f" | {n_intv} Intervals | {details}"

    def attrib_components(self, attribute=None):
        # components according to the repr_attribute
        if attribute is None:
            attribute = self.repr_attribute
        return self.get_attrib_components_dict(self.__verbose__)[attribute]

    def get_attrib_components_dict(self, verbose=False):
        # compute a dict of components for all attributes found in legend_dict

        comp_attrib_dict = {}
        for attr in self.legend_dict.keys():
            attr_components = {}  # correct components order (not self.components)
            for i, intv in enumerate(self.intervals):
                j = find_component_from_attrib(intv, attr, verbose=verbose)
                if j is not None:
                    attr_components.update({i: intv.components[j]})

            comp_attrib_dict.update({attr: attr_components})
        return comp_attrib_dict

    def get_components_indices(self, repr_attribute=None, intervals=None, verbose=False):
        """
        retrieve components indices from borehole's intervals

        repr_repr_attribute: str
            attribute to consider when retrieving intervals components indices (e.g: 'lithology')

        intervals : List of Striplog.Interval object

        Returns
        --------
        numpy.array
            array of indices
        """

        if repr_attribute is None:
            repr_attribute = self.repr_attribute
        if intervals is None:
            intervals = self.intervals

        components = []
        for i in intervals:
            j = find_component_from_attrib(i, repr_attribute, verbose=verbose)
            if j is not None:
                components.append(i.components[j])
        comp_list = list(pd.unique([c[repr_attribute] for c in components]))

        indices = []
        incr = 0
        for i in intervals:
            j = find_component_from_attrib(i, repr_attribute, verbose=verbose)
            if j is not None:
                indices.append(comp_list.index(i.components[j][repr_attribute]))

            if verbose:
                print(f"""get_comp | uniq_comp_list: {comp_list}, n_intv:{incr}, ind_val: {j},
                 comp: {i.components[j][repr_attribute]}""")
            incr += 1

        if verbose:
            print(f'\nget_comp | comp_indices: {np.array(indices)}')
        return np.array(indices)

    def _geometry(self, verbose=False):
        """
        build an omf.LineSetElement geometry of the borehole

        Returns
        --------
        geometry : omf.lineset.LineSetGeometry
            Contains spatial information of a line set
        """

        vertices, segments = [], []
        for i in self.intervals:
            if self.repr_attribute in ['borehole_type', 'lithology']:
                c_key_list = [list(c.keys())[0] for c in i.components]
            else:  # due to the structure of a pollutant component
                c_key_list = [list(c.__dict__.values())[0] for c in i.components]

            if self.repr_attribute in c_key_list:
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
        array = omf.ScalarArray(self.get_components_indices(repr_attribute=self.repr_attribute, verbose=verbose))
        if len(array.array) > 0:
            legend = striplog_legend_to_omf_legend(self.legend_dict[self.repr_attribute]['legend'])[0]
            data.append(omf.MappedData(name=self.repr_attribute, array=array, legends=[legend],
                                       location='segments', description=''))
        self.geometry = omf.LineSetElement(
            name=self.name, geometry=omf.LineSetGeometry(vertices=vertices, segments=segments),
            data=data)

    def vtk(self, radius=None, res=50, scale=5.):
        """ build a vtk tube of given radius based on the borehole geometry """
        if radius is None:
            radius = (self.diameter / 2)
        vtk_obj = ov.line_set_to_vtk(self.geometry).tube(radius=radius*scale, n_sides=res)   # multiply by scale for visibility
        vtk_obj.set_active_scalars(self.repr_attribute.lower())
        self._vtk = vtk_obj
        return self._vtk

    def update_z_collar(self):
        """
        updates z_collar assuming that collar is at the top elevation of the highest interval
        """
        self.z_collar = max([i.top.z for i in self.intervals])

    def plot_log(self, figsize=(3, 5), repr_legend=None, text_size=15, width=2,
                 ticks=None, aspect=3, repr_attribute=None, verbose=False):
        """
        Plot a stratigraphical log for the attribute
        """

        if repr_attribute is None:
            repr_attribute = self.repr_attribute
        if ticks is None:
            mt = self.length/len(self.intervals)
            ticks = (mt/2, mt)
        if repr_legend is None:
            repr_legend = self.legend_dict[repr_attribute]['legend']

        if repr_attribute in ['borehole_type', 'lithology']:
            attr = repr_attribute
        else:  # due to the structure of a pollutant component
            attr = 'level'

        legend_copy = deepcopy(repr_legend)  # work with a copy to keep initial legend state
        decors = {}  # dict of decors to build a legend for the borehole
        attrib_values = []  # list of lithologies in the borehole
        for n, i in enumerate(self.intervals):
            j = find_component_from_attrib(i, repr_attribute, verbose=verbose)
            if j is not None:
                intv_value = i.components[j][attr]
            if isinstance(intv_value, str):
                intv_value = intv_value.lower()
            attrib_values.append(intv_value)
        attrib_values = list(pd.unique(attrib_values))  # to treat duplicate values

        if verbose:
            print(f'\nattrib_values : {attrib_values}\n')

        for i in range(len(legend_copy)):
            leg_value = legend_copy[i].component[attr]
            if verbose:
                print('plot2d | legend_val:', attr, leg_value)
            reg = re.compile("^{:s}$".format(leg_value), flags=re.I)
            reg_value = list(filter(reg.match, attrib_values))  # find value that matches

            if len(reg_value) > 0:
                # force matching to plot
                legend_copy[i].component = Component({attr: reg_value[0]})
                legend_copy[i].width = width
                # use interval order to obtain correct plot legend order
                decors.update({attrib_values.index(reg_value[0]): legend_copy[i]})

        if verbose:
            print('\nplot2d | decors:', decors)
        rev_decors = list(decors.values())
        rev_decors.reverse()
        plot_legend = Legend([v for v in rev_decors])

        print(f"\033[0;40;46mAttribute: \'{repr_attribute}\'\033[0;0;0m")
        fig, ax = plt.subplots(ncols=2, figsize=figsize)
        ax[0].set_title(self.name, size=text_size, color='b')
        plot_from_striplog(self, legend=plot_legend, match_only=[attr],
                           ax=ax[0], ticks=ticks, aspect=aspect, verbose=verbose)
        ax[1].set_title('Legend', size=text_size, color='r')
        plot_legend.plot(ax=ax[1])

    def plot_3d(self, plotter=None, repr_legend_dict=None, repr_attribute=None,
                repr_cmap=None, repr_uniq_val=None, x3d=False, diam=None,
                bg_color=["royalblue", "aliceblue"], update_vtk=False,
                update_cmap=False, custom_legend=False, str_annotations=True,
                scalar_bar_args=None, smooth_shading=True, verbose=False, **kwargs):
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
        jupyter_backend = kwargs.pop('jupyter_backend', None)
        opacity = kwargs.pop('opacity', 1.)
        show_sbar = kwargs.pop('show_scalar_bar', False)
        t_size = kwargs.pop('title_font_size', 25)
        l_size = kwargs.pop('label_font_size', 8)
        font = kwargs.pop('font_family', 'arial')
        t_color = kwargs.pop('text_color', 'k')
        vert_sb = kwargs.pop('vertical', False)

        if custom_legend:
            show_sbar = False

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
            seg = self.vtk(radius=diam / 2)
        else:
            seg = self._vtk

        if repr_attribute is None:
            repr_attribute = self.repr_attribute

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

        # display a categorical legend
        n_col = len(plot_cmap.colors)
        if str_annotations:
            if scalar_bar_args is None:  # scalar_bar properties
                scalar_bar_args = dict(title=f"{repr_attribute.upper()}", title_font_size=t_size, label_font_size=l_size, n_labels=n_col, fmt='', font_family=font, color=t_color, italic=False, bold=False, interactive=True, vertical=vert_sb, shadow=False)
            incr = (len(uniq_attr_val) - 1) / n_col  # increment
            bounds = [0]  # cmap colors limits
            next_bound = 0
            for i in range(n_col + 1):
                if i < n_col:
                    next_bound += incr
                    bounds.append(bounds[0] + next_bound)
            bounds.append(n_col)  # add cmap last value (limit)
            centers = [(bounds[i] + bounds[i + 1]) / 2 for i in range(n_col)]
            str_annot = {k: v.capitalize() for k, v in zip(centers, uniq_attr_val)}

        else:  # display a numerical legend
            scalar_bar_args = None
            str_annot = None

        if verbose:
            print(f'plot3d | n_colors: {n_col} | incr: {incr}| unique: {uniq_attr_val}'
                  f'\nannotations: {str_annot}')

        plotter.add_mesh(seg, cmap=plot_cmap, scalar_bar_args=scalar_bar_args, opacity=opacity, smooth_shading=smooth_shading, show_scalar_bar=show_sbar, annotations=str_annot, **kwargs)

        if custom_legend:
            plotter.add_scalar_bar(title=repr_attribute, title_font_size=t_size, n_labels=n_col, label_font_size=l_size, font_family=font, color=t_color, fmt='', vertical=vert_sb, italic=False, bold=False, interactive=True, shadow=False)

        # set background color for the render (None : pyvista default background color)
        if bg_color is not None:
            if isinstance(bg_color, list) and len(bg_color) == 2:
                top_c = bg_color[1]
                btm_c = bg_color[0]
            elif isinstance(bg_color, str):
                top_c = None
                btm_c = bg_color
            else:
                raise (ValueError('bg_color must be a color string or a list of 2 colors strings !'))

            plotter.set_background(color=btm_c, top=top_c)

        if show or jupyter_backend is not None:
            plotter.add_axes()
            plotter.show(auto_close=True, jupyter_backend=jupyter_backend)
        elif x3d:
            writer = vtkX3DExporter()
            writer.SetInput(plotter.renderer.GetRenderWindow())
            filename = f'tmp_files/BH_{self.name:s}.x3d'
            writer.SetFileName(filename)
            writer.Update()
            writer.Write()
            x3d_html = X3D_HTML.format(filename)
            return HTML(x3d_html)
