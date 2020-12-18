from core.orm import BoreholeOrm, ComponentOrm
from core.omf import Borehole3D
from utils.orm import get_interval_list
from vtk import vtkX3DExporter
from IPython.display import HTML
import pyvista as pv


class Project:
    def __init__(self, session, legend=None, name='new_project'):
        self.session = session
        self.name = name
        self.boreholes = None
        self.boreholes_3d = None
        self.legend = legend
        self.refresh(update_3d=True)

    def refresh(self, update_3d=False):
        self.boreholes = self.session.query(BoreholeOrm).all()
        if update_3d:
            self.boreholes_3d = []
            for bh in self.boreholes:
                list_of_intervals = get_interval_list(bh)
                print(list_of_intervals)
                self.boreholes_3d.append(Borehole3D(intervals=list_of_intervals, legend=self.legend))

    def commit(self):
        self.session.commit()
        
    def add_borehole(self, bh):
        self.session.add(bh)
        self.commit()
        self.refresh()
        list_of_intervals = get_interval_list(bh)
        self.boreholes_3d.append(Borehole3D(intervals=list_of_intervals, legend=self.legend))

    def add_components(self, components):
        for comp_id in components.keys():
            new_component = ComponentOrm(id=comp_id, description=components[comp_id].summary())
            self.session.add(new_component)
        self.commit()
        self.refresh()

    def plot3d(self, x3d=False):
        pl = pv.Plotter()
        for bh in self.boreholes_3d:
            bh.plot3d(plotter=pl)
        if not x3d:
            pl.show()
        else:
            writer = vtkX3DExporter()
            writer.SetInput(pl.renderer.GetRenderWindow())
            filename = f'project_{self.name:s}.x3d'
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