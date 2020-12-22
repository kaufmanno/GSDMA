from striplog import Lexicon, Striplog, Legend
from striplog.utils import hex_to_rgb
from matplotlib.colors import ListedColormap
import numpy as np
import omfvista as ov
import pyvista as pv
import omf
from vtk import vtkX3DExporter
from IPython.display import HTML


def striplog_legend_to_omf_legend(legend):
    """
    Creates an omf.data.Legend object from a striplog.Legend object
    
    Parameters
    -----------
    legend : striplog.Legend object
    
    Returns
    --------
    omf.data.Legend 
        Legends to be used with DataMap indices
        
    ListedColormap(new_colors)
        matplotlib colormap
    """
    # we must add colors as a parameter to allow to change colors style
    

    omf_legend = []
    new_colors = [np.array([0.9, 0.9, 0.9, 1.])]
    for i in legend:
        omf_legend.append(i.colour)
        new_colors.append(np.hstack([np.array(hex_to_rgb(i.colour))/255, np.array([1.])]))
    return omf.data.Legend(description='', name='', values=omf.data.ColorArray(omf_legend)), ListedColormap(new_colors)


class Borehole3D(Striplog):
    """
    Borehole object based on striplog object that can be displayed in a 3D environment
    
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

    def __init__(self, intervals=None, components=None, name='', legend=None, x_collar=0., y_collar=0.):
        
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
        """
        
        self.name = name

        if legend is None or not isinstance(legend, Legend):
            self.legend = Legend.default()
        else:
            self.legend = legend

        self.x_collar = x_collar
        self.y_collar = y_collar
        self.omf_legend, self.omf_cmap = striplog_legend_to_omf_legend(self.legend)

        if intervals is None:
            lexicon = Lexicon.default()
            with open('../data/test.las', 'r') as las3:
                default_intv = Striplog.from_las3(las3.read(), lexicon)
                intervals = list(default_intv)
            print("Pay attention that default intervals are actually used !\n")
            
        self.intervals = intervals
        self.geometry = []

        # instantiation with supers properties
        Striplog.__init__(self, list_of_Intervals=self.intervals)

        # self.uid=uuid #get a unique for identification of borehole in the project

        self.build_geometry()

    def get_components_indices(self):
        """
        retrieve components indices from borehole's intervals
        
        Returns
        --------
        array of indices
        """
        
        indices = []
        for i in self.intervals:
            if i.components[0] in self.components:
                indices.append(self.components.index(i.components[0]))
            else:
                indices.append(-1)
        return np.array(indices)

    def build_geometry(self):
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

        self.geometry = omf.LineSetElement(name=self.name,
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

        return self.geometry

    def plot3d(self, plotter=None, x3d=False):
        """
        Returns an interactive 3D representation of all boreholes in the project
        
        Parameters
        -----------
        plotter : pyvista.plotter object
            Plotting object to display vtk meshes or numpy arrays (default=None)
            
        x3d : bool
            if True, generates a 3xd file of the 3D (default=False)
        """
        
        omf_legend, _ = striplog_legend_to_omf_legend(self.legend)

        if plotter is None:
            plotter = pv.Plotter()
            show = True
        else:
            show = False
            
        seg = ov.line_set_to_vtk(self.geometry)
        seg.set_active_scalars('component')
        ov.lineset.add_data(seg, self.geometry.data)
        plotter.add_mesh(seg.tube(radius=3), cmap=self.omf_cmap)
        
        if show and not x3d:
            plotter.show()
        else:
            writer = vtkX3DExporter()
            writer.SetInput(plotter.renderer.GetRenderWindow())
            filename = f'BH_{self.name:s}.x3d'
            writer.SetFileName(filename)
            writer.Update()
            writer.Write()
            x3d_html = f'<html>\n<head>\n    <meta http-equiv="X-UA-Compatible" content="IE=edge"/>\n' \
                       '<title>X3D scene</title>\n <p>' \
                       '<script type=\'text/javascript\' src=\'http://www.x3dom.org/download/x3dom.js\'> </script>\n' \
                       '<link rel=\'stylesheet\' type=\'text/css\' href=\'http://www.x3dom.org/download/x3dom.css\'/>\n' \
                       '</head>\n<body>\n<p>\n For interaction, click in the view and press "a" to see the whole scene. For more info on interaction,' \
                       ' please read  <a href="https://doc.x3dom.org/tutorials/animationInteraction/navigation/index.html">the docs</a>  \n</p>\n' \
                       '<x3d width=\'968px\' height=\'600px\'>\n <scene>\n' \
                       '<viewpoint position="-1.94639 1.79771 -2.89271" orientation="0.03886 0.99185 0.12133 3.75685">' \
                       '</viewpoint>\n <Inline nameSpaceName="Borehole" mapDEFToID="true" url="' + filename + '" />\n' \
                                                                                                              '</scene>\n</x3d>\n</body>\n</html>\n'
            return HTML(x3d_html)