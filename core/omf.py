from striplog import Lexicon, Striplog, Legend, Interval, Decor
from utils.omf import striplog_legend_to_omf_legend
import matplotlib.pyplot as plt
import numpy as np
from utils.omf import build_bh3d_legend
from copy import deepcopy
import re
import omfvista as ov
import pyvista as pv
import omf
from vtk import vtkX3DExporter
from IPython.display import HTML
from utils.config import DEFAULT_LITHOLOGY


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

    Methods
    --------
    get_components_indices()
    build_geometry()
    commit()
    add_components(components)
    plot3d(x3d=False)

    """

    def __init__(self, intervals=None, components=None, repr_attribute='lithology', name='', diam=0.5, length=0,
                 x_collar=0., y_collar=0., z_collar=0., legend=None):

        """
        build a Borehole3D object from Striplog.Intervals list
        
        Parameters
        -----------
        intervals : list
            list of Striplog.Interval objects (default = None)
        components : list
            list of Striplog.Component objects (default = None)
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
        """

        self.name = name
        self.x_collar = x_collar
        self.y_collar = y_collar
        self.z_collar = z_collar
        self.diameter = diam
        self.length = length
        self._repr_attribute = None
        self._components = components  # given components

        if intervals is None and length == 0:
            raise(ValueError("Cannot create a borehole without length and interval !"))

        if intervals is None and length != 0:
            lexicon = Lexicon.default()
            intervals = [Interval(top=0, base=length, description=DEFAULT_LITHOLOGY, lexicon=lexicon)]
            print(f"No intervals given, default interval is used, with lithology ({DEFAULT_LITHOLOGY})!\n")

        self.intervals = intervals
        self._geometry = []
        self._vtk = None

        # instantiation with supers properties
        Striplog.__init__(self, list_of_Intervals=self.intervals)

        # other object building processes
        if legend is None or not isinstance(legend, Legend):
            print("No given legend or incorrect format ! A default one is used")
            self._legend = Legend.default()
        else:
            self._legend = legend  # given legend

        # create object legend
        # self.legend = self._legend
        self.legend = build_bh3d_legend(borehole3d=self, default_legend=self._legend)
        self.omf_legend, self.omf_cmap = striplog_legend_to_omf_legend(self.legend)
        self.geometry
        self.vtk()

    def get_components_indices(self):
        """
        retrieve components indices from borehole's intervals
        
        Returns
        --------
        array of indices
        """

        indices = []
        idx = 0
        for i in self.intervals:
            if i.primary in self.components:
                idx += 1
                indices.append(idx)  # not really effective
                # indices.append(self.components.index(i.primary))  # old code
            else:
                indices.append(-1)
        return np.array(indices)

    def vtk(self, radius=None, res=50):
        """ build a vtk tube of given radius based on the borehole geometry """
        if radius is None:
            radius = self.diameter/2 * 5  # multiply for visibility
            vtk_obj = ov.line_set_to_vtk(self.geometry).tube(radius=radius, n_sides=res)
            vtk_obj.set_active_scalars('component')
            self._vtk = vtk_obj
        return self._vtk

    @property
    def repr_attribute(self):
        return self._repr_attribute

    @repr_attribute.setter
    def repr_attribute(self, value):
        assert(isinstance(value, str))


    @property
    def geometry(self):
        """
        build an omf.LineSetElement geometry of the borehole
        
        Returns
        --------
        geometry : omf.lineset.LineSetGeometry
            Contains spatial information of a line set
        """

        vertices, segments = [], []

        for i in self.intervals:
            if i.top not in vertices:
                if hasattr(i.top, 'x') and hasattr(i.top, 'y'):
                    x = i.top.x
                    y = i.top.y
                else:
                    x = self.x_collar
                    y = self.y_collar
                vertices.append([x, y, -i.top.z])
                top = len(vertices) - 1
            else:
                top = vertices.index(i.top)

            if i.base not in vertices:
                if hasattr(i.base, 'x') and hasattr(i.base, 'y'):
                    x = i.base.x
                    y = i.base.y
                else:
                    x = self.x_collar
                    y = self.y_collar
                vertices.append([x, y, -i.base.z])
                base = len(vertices) - 1
            else:
                base = vertices.index(i.base)

            segments.append([top, base])

        vertices = np.array(vertices)

        self._geometry = omf.LineSetElement(name=self.name,
                                           geometry=omf.LineSetGeometry(
                                               vertices=vertices,
                                               segments=segments),
                                           data=[omf.MappedData(name='component',
                                                                description='test',
                                                                array=omf.ScalarArray(self.get_components_indices()),
                                                                legends=[self.omf_legend],
                                                                location='segments')]
                                           )

        print("Borehole geometry created successfully !")

        return self._geometry


    def plot3d(self, plotter=None, attribute='lithology', x3d=False, diam=None, update_vtk=False,
               bg_color=["royalblue", "aliceblue"]):
        """
        Returns an interactive 3D representation of all boreholes in the project
        
        Parameters
        -----------
        plotter : pyvista.plotter object
            Plotting object to display vtk meshes or numpy arrays (default=None)
            
        x3d : bool
            if True, generates a 3xd file of the 3D (default=False)
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

        #omf_legend, _ = striplog_legend_to_omf_legend(self.legend)

        if update_vtk or diam is not None:
            seg = self.vtk(radius=(diam/2)*10)
        else:
            seg = self._vtk
        seg.set_active_scalars('component')

        legend3d = build_bh3d_legend(borehole3d=self, default_legend=self.legend, attribute=attribute)
        omf_cmap3d = striplog_legend_to_omf_legend(legend3d)[1]

        plotter.add_mesh(seg, cmap=omf_cmap3d)

        # set background color for the render (None : pyvista default background color)
        if bg_color is not None:
            if len(bg_color) == 2:
                top_c = bg_color[1]
                btm_c = bg_color[0]
            elif len(bg_color) == 1:
                top_c = None
                btm_c = bg_color
            else:
                print('bg_color must be a color string or a list of 2 colors strings !')

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

    def plot2d(self, figsize=(6, 6), legend=None, text_size=15, width=3, attribute='lithology'):
        """
        Plot a 2D lithological log
        """

        if legend is None:
            legend = self.legend

        legend_copy = deepcopy(legend)  # work with a copy to keep initial legend state
        plot_decors = []  # list of decors to build a own legend for the borehole
        attrib_values = []  # list of lithologies in the borehole

        for i in self.intervals:
            intv_value = i.primary[attribute]
            if isinstance(intv_value, str):
                intv_value = intv_value.lower()
            attrib_values.append(intv_value)

        for i in range((len(legend_copy) - 1), -1, -1):
            leg_value = legend_copy[i].component[attribute]
            reg = re.compile("^{:s}$".format(leg_value), flags=re.I)
            reg_value = list(filter(reg.match, attrib_values))  # find value that matches
            if len(reg_value) > 0:
                legend_copy[i].component[attribute] = reg_value[0]  # force matching to plot
                plot_decors.append(legend_copy[i])
                legend_copy[i].width = width
        plot_legend = Legend(plot_decors)
        fig, ax = plt.subplots(ncols=2, figsize=figsize)
        ax[0].set_title(self.name, size=text_size, color='b')
        self.plot(legend=plot_legend, match_only=[attribute], ax=ax[0])
        ax[1].set_title('Legend', size=text_size, color='r')
        plot_legend.plot(ax=ax[1])
