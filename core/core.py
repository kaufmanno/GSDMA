from core.orm import BoreholeOrm, ComponentOrm, LinkIntervalComponentOrm
from core.omf import Borehole3D
from utils.io import get_interval_list
from vtk import vtkX3DExporter
from IPython.display import HTML
import numpy as np
import pyvista as pv

class Project:
    """
    Create a project that will contain Borehole object
    
    Attributes
    -----------
    session : ORM Session object
    name : str
    boreholes : list of BoreholeORM object
    boreholes_3d : list of Borehole3D object
    legend : Striplog Legend object

    Methods
    --------
    refresh(update_3d=false)
    commit()
    add_borehole(self, bh)
    add_components(self, components)
    plot3d(self, x3d=False)
        
    """
    
    def __init__(self, session, legend=None, name='new_project'):
        """
        Project class
        
        Parameters
        -----------
        session : ORM session object
        legend : bool
        name : str
        
        """
        
        self.session = session
        self.name = name
        self.boreholes = None
        self.boreholes_3d = None
        self.legend = legend
        self.refresh(update_3d=True)

    def refresh(self, update_3d=False, verbose=False):
        """
        read Boreholes in the database and updates 3D boreholes
        
        Parameters
        -----------
        update_3d : bool
            if True, updates Striplog/OMF 3D boreholes (default=False)
        """
        
        self.boreholes = self.session.query(BoreholeOrm).all()
        print(self.legend)
        if update_3d:
            self.boreholes_3d = []
            for bh in self.boreholes:
                list_of_intervals, bh.length = get_interval_list(bh)
                print(list_of_intervals[0].components[0].lithology)
                if verbose:
                    print(bh.id, " added")
                self.boreholes_3d.append(Borehole3D(name=bh.id, diam=bh.diameter, intervals=list_of_intervals, legend=self.legend, length=bh.length))

    def commit(self):
        'Validate all modifications done in the project'
        self.session.commit()
        
    def add_borehole(self, bh):
        """
        Add a list of Boreholes to the project
        
        Parameters
        -----------
        bh : list
            list of BoreholeOrm objects
            
        See Also
        ---------
        BoreholeOrm : ORM borehole object
        Borehole3D : Striplog/OMF borehole object
        """
        
        self.session.add(bh)
        self.commit()
        self.refresh()
        list_of_intervals, bh.length = get_interval_list(bh)
        self.boreholes_3d.append(Borehole3D(name=bh.id, diam=bh.diameter, intervals=list_of_intervals, legend=self.legend, length=bh.length))
            
    def add_components(self, components):
        """
        Add a list of Components to the project
        
        Parameters
        -----------
        Components : dict
            dict of Component objects
            
        See Also
        ---------
        Component : ORM Component object
        """
        
        for comp_id in components.keys():
            new_component = ComponentOrm(id=comp_id, description=components[comp_id].summary())
            self.session.add(new_component)
            
        self.commit()
        self.refresh()

    def add_link_between_components_and_intervals(self, link_component_interval):
        """
        Add a list of Components to the project

        Parameters
        -----------
        link_component_interval : dict
            dict of links between Component objects and Interval objects

        """

        for link in link_component_interval.keys():
            new_link = LinkIntervalComponentOrm(int_id=link[0], comp_id=link[1], **link_component_interval[link])
            self.session.add(new_link)

        self.commit()
        self.refresh()

    def plot3d(self, plotter=None, x3d=False, labels_size=None, labels_color=None, bg_color=("royalblue", "aliceblue"), window_size=None):
        """
        Returns an interactive 3D representation of all boreholes in the project
        
        Parameters
        -----------
        x3d : bool
            if True, generates a 3xd file of the 3D (default=False)
        """
        pts = {}
        if window_size is not None:
            notebook = False
        else:
            notebook = True
            window_size = (600, 400)

        if plotter is not None:
            pl=plotter
        else:
            pl = pv.Plotter(notebook=notebook, window_size=window_size)

        for bh in self.boreholes_3d:
            bh.plot3d(plotter=pl, bg_color=bg_color)
            pts.update({bh.name: bh._vtk.center[:2]+[0]})

        if labels_color is None:
            labels_color = 'black'

        if labels_size is not None:
            pv_pts = pv.PolyData(np.array(list(pts.values())))
            pv_pts['bh_name'] = list(pts.keys())
            pl.add_point_labels(pv_pts, 'bh_name', point_size=1, font_size=labels_size,
                                text_color=labels_color, show_points=False)
            
        if not x3d:
            pl.show()
        else:
            writer = vtkX3DExporter()
            writer.SetInput(pl.renderer.GetRenderWindow())
            filename = f'tmp_files/project_{self.name:s}.x3d'
            writer.SetFileName(filename)
            writer.Update()
            writer.Write()
            x3d_html = f'<html>\n<head>\n    <meta http-equiv="X-UA-Compatible" content="IE=edge"/>\n' \
                       '<title>X3D scene</title>\n <p>' \
                       '<script type=\'text/javascript\' src=\'http://www.x3dom.org/download/x3dom.js\'> </script>\n' \
                       '<link rel=\'stylesheet\' type=\'text/css\' href=\'http://www.x3dom.org/download/x3dom.css\'/>\n' \
                       '</head>\n<body>\n<p>\n For interaction, click in the view and press "a" or "i" to see the whole scene, "d" to display info, "space" for shortcuts. For more info col interaction,' \
                       ' please read  <a href="https://doc.x3dom.org/tutorials/animationInteraction/navigation/index.html">the docs</a>  \n</p>\n' \
                       '<x3d width=\'968px\' height=\'600px\'>\n <scene>\n' \
                       '<viewpoint position="152919.656 122576.828 36.522" orientation="0.5537 0.1614 0.81692 1.4642">' \
                       '</viewpoint>\n <Inline nameSpaceName="Borehole" mapDEFToID="true" url="' + filename + '" />\n' \
                       '</scene>\n</x3d>\n</body>\n</html>\n'
            return HTML(x3d_html)