from striplog import Lexicon, Striplog, Legend, Interval, Decor
from utils.omf import striplog_legend_to_omf_legend
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import random
import re
import numpy as np
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

    def __init__(self, intervals=None, components=None, name='', diam=0.5, length=0,
                 x_collar=0., y_collar=0., z_collar=0., legend=None,
                 legend_colors=None, legend_hatches=None):

        """
        build a Borehole3D object from Striplog.Intervals list
        
        Parameters
        -----------
        intervals : list
            list of Striplog.Interval object (default = None)
            
        components : 
            (default = None)
        
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

        # print(isinstance(self._legend, Legend))
        # create object legend
        self.legend = self._legend  # self.build_bh3d_legend(default_legend=self._legend, hatches=legend_hatches, colors=legend_colors)
        self.omf_legend, self.omf_cmap = striplog_legend_to_omf_legend(self.legend)

        self.geometry
        self.vtk()

    def build_bh3d_legend(self, default_legend, hatches=None, colors=None, width=3):
        """
        Build a legend based on lithologies in the borehole

        Parameters
        -------------
        default_legend: striplog.Legend
            A legend that contains default lithologies and their associated colors / hatches
        Returns
        --------
        striplog.Legend
        """

        # given values test
        if not isinstance(default_legend, Legend):
            raise(TypeError('legend must be a Striplog.Legend'))

        if (colors is not None and colors not in ['random', 'default']) \
                and not isinstance(colors, list):
            raise(TypeError('colors must be a list of colors in str, html or RGB(A) codes'))

        if (hatches is not None and hatches not in ['random', 'default']) \
                and not isinstance(hatches, list):
            raise(TypeError('hatches must be a list of hatches in str'))

        # default values
        if hatches == 'random' or hatches is None:
            def_hatches = ['+', 'x', '.', 's', '*', 'b', 'c', 'v', '/', 't']

        if colors == 'random':
            def_colors = [i.colour for i in Legend.default()] + list(mcolors.CSS4_COLORS.values())

        list_of_decors, hatches_used = [], []

        if self._components is None:
            components = [i.components[0] for i in self.intervals]  # don't use self.components !
        else:
            components = self._components
        i = 0  # increment to retrieve given colors or hatches

        for comp in components:
            print('---------------\n', components)
            if hasattr(comp, 'lithology'):
                print(f'{i}, {comp}')
                comp_litho = comp.lithology
                for leg in default_legend:
                    leg_litho = leg.component.lithology
                    reg = re.compile("^{:s}$".format(leg_litho), flags=re.I).match(comp_litho)
                    #print(reg)
                    if reg:  # lithology found
                        print('found')
                        # ------------ color processing --------------------
                        if colors is None:
                            if hasattr(comp, 'colour'):
                                c = comp.colour
                            else:
                                c = leg.colour
                        elif colors == 'default':
                            c = leg.colour
                        elif colors == 'random':
                            c = random.sample(def_colors, 1)[0]
                        elif colors is not None:
                            c = colors[i]

                        # ------------ hatch processing ------------------------
                        if hatches is None:
                            if hasattr(comp, 'hatch'):
                                h = comp.hatch
                            else:
                                h = random.sample(def_hatches, 1)[0]
                                # h = leg.hatch  # no hatches in default !
                        elif hatches == 'default':
                            h = leg.hatch
                        elif hatches == 'random':
                            h = random.sample(def_hatches, 1)[0]
                            while h in hatches_used:
                                if len(hatches_used) >= len(def_hatches):
                                    h = ''.join(random.sample(hatches_used, 2))
                                elif len(hatches_used) >= 2 * len(def_hatches):
                                    h = ''.join(random.sample(hatches_used, 3))
                                else:
                                    h = random.sample(hatches, 1)[0]

                            hatches_used.append(h)
                        elif hatches is not None:
                            h = hatches[i]
                        else:
                            h = None
            else:
                # print(f"All components : {components}")
                # print(f"Empty component: {i}-{comp}")
                raise (TypeError('Cannot create a legend for empty component'))
                # TODO : allow empty component (define a lacking lithology type)

            i += 1

            decor = Decor({'color': c, 'hatch': h, 'component': comp, 'width': width})
            list_of_decors.append(decor)

        return Legend(list_of_decors)

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
                # indices.append(self.components.index(i.primary)) #old code
            else:
                indices.append(-1)
        return np.array(indices)

    def vtk(self, radius=None, res=50):
        """ build a vtk tube of given radius based on the borehole geometry """
        if radius is None:
            radius = self.diameter/2 * 5 # multiply for visibility
            vtk_obj = ov.line_set_to_vtk(self.geometry).tube(radius=radius, n_sides=res)
            vtk_obj.set_active_scalars('component')
            self._vtk = vtk_obj
        return self._vtk

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


    def plot3d(self, plotter=None, x3d=False, diam=None, update_vtk=False,
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
        # seg = ov.line_set_to_vtk(self.geometry)
        seg.set_active_scalars('component')
        # ov.lineset.add_data(seg, self.geometry.data)
        # print(seg.active_scalars)

        plotter.add_mesh(seg, cmap=self.omf_cmap)

        # set background color for the render
        # None : pyvista default background color
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

    def plot2d(self, figsize=(6, 6), legend=None, text_size=15, width=3):
        """
        Plot a 2D lithological log
        """
        if legend is None:
            legend = self.legend

        plot_decors = []  # list of decors to build a own legend for the borehole
        bh_litho = []  # list of lithologies in the borehole

        for i in self.intervals:
            bh_litho.append(i.primary.lithology)

        for i in range((len(legend)-1), -1, -1):
            litho = legend[i].component.lithology
            if litho in bh_litho:
                plot_decors.append(legend[i])
                legend[i].width = width
        plot_legend = Legend(plot_decors)

        fig, ax = plt.subplots(ncols=2, figsize=figsize)
        ax[0].set_title(self.name, size=text_size, color='b')
        self.plot(legend=plot_legend, ax=ax[0])
        ax[1].set_title('Legend', size=text_size, color='r')
        plot_legend.plot(ax=ax[1])
