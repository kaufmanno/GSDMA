from core.orm import BoreholeOrm, ComponentOrm, IntervalOrm, PositionOrm, LinkIntervalComponentOrm
from sqlalchemy import select
from utils.orm import create_bh3d_from_bhorm
from vtk import vtkX3DExporter, vtkPolyDataMapper # NOQA
from IPython.display import HTML
from utils.visual import build_bh3d_legend_cmap
from utils.config import DEFAULT_BOREHOLE_LEGEND, DEFAULT_BOREHOLE_LEXICON, DEFAULT_LITHO_LEGEND, DEFAULT_POL_LEGEND
import numpy as np
import pyvista as pv
import folium as fm
from folium import plugins
import geopandas as gpd
from copy import deepcopy
from core.orm import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class Project:
    """
    Create a project that will contain Borehole object
    
    Attributes
    -----------
    session : ORM Session object
    name : str
    boreholes_orm : list of BoreholeORM object
    boreholes_3d : list of Borehole3D object

    Methods
    --------
    refresh(update_3d=false)
    commit()
    add_borehole(self, bh)
    add_components(self, components)
    plot3d(self, x3d=False)
        
    """
    
    def __init__(self, session, legend_dict=None, lexicon=None, name='new_project'):
        """
        Project class
        
        Parameters
        -----------
        session : ORM session object
        legend_dict : dict
        name : str
        
        """
        
        self.session = session
        self.name = name
        self.boreholes_orm = None
        self.boreholes_3d = None
        self.__components_dict__ = None

        if legend_dict is None:
            legend_dict = {'borehole_type': {'legend': DEFAULT_BOREHOLE_LEGEND},
                           'lithology': {'legend': DEFAULT_LITHO_LEGEND},
                           'benzene_industrial': {'legend': DEFAULT_POL_LEGEND}}
        if lexicon is None:
            lexicon = DEFAULT_BOREHOLE_LEXICON

        self.legend_dict = deepcopy(legend_dict)
        self.lexicon = lexicon
        self._repr_attribute = 'borehole_type'
        self.refresh(update_3d=True)

    @classmethod
    def load(cls, db_name, legend_dict=None, verbose=False, lexicon=None):
        """ creates a project from a project database"""
        project_name = db_name.rstrip('.db')

        engine = create_engine(f"sqlite:///{db_name}", echo=verbose)
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        if verbose:
            print(f'legend_dict: {legend_dict}')
        p = cls(session, name=project_name, legend_dict=legend_dict, lexicon=lexicon)
        p.refresh()
        session.close()
        return p

    # ------------------------------- Class Properties ----------------------------
    @property
    def repr_attribute(self):
        return self._repr_attribute

    @repr_attribute.setter
    def repr_attribute(self, value):
        assert (isinstance(value, str))
        self._repr_attribute = value
        self.refresh(update_3d=True)
        self.update_legend_cmap()

    def refresh(self, update_3d=False, verbose=False):
        """
        read Boreholes in the database and updates 3D boreholes
        
        Parameters
        -----------
        update_3d : bool
            if True, updates Striplog/OMF 3D boreholes (default=False)
        verbose : bool
            verbose display if True
        """

        self.boreholes_orm = {i.id: i for i in self.session.query(BoreholeOrm).all()}
        if verbose:
            print(self.legend_dict)
        if update_3d:
            self.boreholes_3d = []
            for bh in self.boreholes_orm.values():
                self.boreholes_3d.append(create_bh3d_from_bhorm(bh, verbose=verbose, attribute=self.repr_attribute,
                                                                legend_dict=self.legend_dict))

    def save_modification(self):
        """Validate all modifications done in the project"""
        self.session.commit()
        print('Modifications saved! Boreholes in the project : ', len(self.boreholes_orm))

    def cancel_modification(self):
        """Cancel all modifications done in the project"""
        self.session.rollback()
        print('Modifications cancelled !')
        
    def add_borehole(self, bh_orm, update_3d=False):
        """
        Add a Borehole to the project
        
        Parameters
        -----------
        bh_orm : BoreholeOrm object

        update_3d: bool

        See Also
        ---------
        BoreholeOrm : ORM borehole object
        Borehole3D : Striplog/OMF borehole object
        """
        
        self.session.add(bh_orm)
        self.save_modification()
        self.refresh(update_3d=update_3d)
            
    def add_components(self, components):
        """
        Add a list of Components to the project
        
        Parameters
        -----------
        components : dict
            dict of Component objects
            
        See Also
        ---------
        Component : ORM Component object
        """
        
        for comp_id in components.keys():
            new_component = ComponentOrm(description=str(components[comp_id].__dict__), id=comp_id)
            self.session.add(new_component)

        self.__components_dict__ = components
        self.save_modification()
        self.refresh()

    def add_link_components_intervals(self, link_component_interval, commit=True):
        """
        Add a list of Components to the project

        Parameters
        -----------
        link_component_interval : dict
            dict of links between Component objects and Interval objects

        """

        for link in link_component_interval.keys():
            new_link = LinkIntervalComponentOrm(intv_id=link[0], comp_id=link[1], **link_component_interval[link])
            self.session.add(new_link)

        if commit:
            self.save_modification()
            self.refresh()

    def find_next_id(self, orm_class):
        """ Gets the next id for a given ORM_Class

        Parameters
        ----------
        orm_class : class
            A class from core.orm

        Returns
        -------
        int
            Next record id
        """

        stmt = select(orm_class.id).order_by(orm_class.id.desc())
        last_id = self.session.execute(stmt).first()
        if last_id is None:
            last_id = -1
        else:
            last_id = last_id[0]
        return last_id + 1

    def get_component_id_from_description(self, description):
        """ Gets the id of the (first) component corresponding to the given description

         Parameters
         ----------
         description : str
            A string that can be evaluated as a dictionary e.g. "{'lithology': 'sand'}"

        Returns
        -------
        int
            Id of the component or None if none where found
        """

        stmt = select(ComponentOrm.id).where(ComponentOrm.description == description)
        result = self.session.execute(stmt).first()
        if result is not None:
            result = result[0]
        return result

    def insert_borehole(self, bh_dict, verbose=False):
        bh_orm = BoreholeOrm(id=bh_dict['id'], date=bh_dict.pop('date', None), length=bh_dict.pop('length', None),
                             diameter=bh_dict.pop('diameter', None))
        intv_id = self.find_next_id(IntervalOrm)
        bh_orm.intervals_values.update({intv_id: {'description': f"{bh_dict['borehole_type']} {bh_dict['id']}",
                                                  'interval_number': 0,
                                                  'top': PositionOrm(**bh_dict['top']),
                                                  'base': PositionOrm(**bh_dict['base'])}})

        description = "{'borehole_type': '" + bh_dict['borehole_type'] + "'}"
        component_id = self.get_component_id_from_description(description)
        if component_id is None:
            component_id = self.find_next_id(ComponentOrm)
            bh_component = ComponentOrm(id=component_id, description=description)
            self.session.add(bh_component)

        link_dict = {(intv_id, component_id): {'extra_data': 'None'}}
        if verbose:
            print(f'interval : {intv_id}, component: {component_id}')
        self.add_link_components_intervals(link_dict, commit=False)
        # self.commit()
        self.add_borehole(bh_orm, verbose)

    def insert_interval_in_borehole(self, bh_id, intv_dict, verbose=False):

        intv_id = self.find_next_id(IntervalOrm)
        self.boreholes_orm[bh_id].intervals_values.update({
            intv_id: {'description': intv_dict['description'],
                      'interval_number': intv_dict['interval_number'],
                      'top': PositionOrm(**intv_dict['top']),
                      'base': PositionOrm(**intv_dict['base'])}})
        link_dict = {}
        for descr_comp in intv_dict['components']:
            component_id = self.get_component_id_from_description(descr_comp)
            if component_id is None:
                component_id = self.find_next_id(ComponentOrm)
                new_component = ComponentOrm(id=component_id, description=descr_comp)
                self.session.add(new_component)
            link_dict.update({(intv_id, component_id): {'extra_data': intv_dict['extra_data']}})
            if verbose:
                print(f'adding interval : {intv_id}, component: {component_id}')
        self.add_link_components_intervals(link_dict)
    
    def plot3d(self, plotter=None, repr_attribute='borehole_type', repr_legend_dict=None,
               labels_size=15, labels_color=None, bg_color=("royalblue", "aliceblue"),
               x3d=False, window_size=None, verbose=False, **kwargs):
        """
        Returns an interactive 3D representation of all boreholes in the project
        
        Parameters
        -----------
        x3d : bool
            if True, generates a 3xd file of the 3D (default=False)
        """
        custom_legend = False
        name_pts = {}
        if window_size is not None:
            notebook = False
        else:
            notebook = True
            window_size = (600, 400)

        if plotter is not None:
            pl = plotter
        else:
            pl = pv.Plotter(notebook=notebook, window_size=window_size)

        if repr_legend_dict is None:
            repr_legend_dict = self.legend_dict
        self.repr_attribute = repr_attribute
        plot_cmap = repr_legend_dict[repr_attribute]['cmap']
        uniq_attr_val = repr_legend_dict[repr_attribute]['values']

        for bh in self.boreholes_3d:
            bh_val_un = bh.legend_dict[repr_attribute]['values']
            bh.plot3d(plotter=pl, repr_attribute=repr_attribute,
                      bg_color=bg_color,
                      repr_legend_dict=repr_legend_dict, repr_cmap=plot_cmap,
                      repr_uniq_val=uniq_attr_val, custom_legend=custom_legend, **kwargs)
            name_pts.update({bh.name: bh._vtk.center[:2]+[bh.z_collar]})
            if verbose:
                print(f'Borehole "{bh.name}" | attribute values -> {bh_val_un}')

        if labels_color is None:
            labels_color = 'black'

        if labels_size is not None:
            pv_pts = pv.PolyData(np.array(list(name_pts.values())))
            pv_pts['bh_name'] = list(name_pts.keys())
            pl.add_point_labels(pv_pts, 'bh_name', point_size=1, font_size=labels_size,
                                text_color=labels_color, show_points=False)

        if not x3d:
            pl.show(auto_close=True)
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

    def plot_log(self, bh_name):
        """ plot a stratigraphical log of a borehole for an attribute

        bh_name: str
        """

        for bh in self.boreholes_3d:
            if bh.name == bh_name:
                bh.plot_log(repr_attribute=self.repr_attribute)
                break

    def plot_map(self, tiles=None, epsg=31370, save_as=None, radius=0.2, opacity=0.1, zoom_start=15, max_zoom=25, control_scale=True, marker_color='red'):
        """2D Plot of all boreholes in the project

        parameters
        -------------
        tile : dict of a tile properties (name, attributes, url)
        epsg : int
            Value of Coordinates Reference System (CRS)
        save_as : str
             filename (and dir) to save html version of the map (e.g: 'mydir/mymap.html')

        """
        # create a geopandas with all project boreholes
        bhs = gpd.GeoDataFrame(columns=['Name', 'X', 'Y'])
        for bh in self.boreholes_3d:
            i = len(bhs)
            xy = bh._vtk.center[:2]  # retrieve collars positions
            bhs.loc[i, ['Name', 'X', 'Y']] = [bh.name, xy[0], xy[1]]

        geom = gpd.points_from_xy(bhs.X, bhs.Y, crs=f"EPSG:{epsg}")
        bhs.geometry = geom
        bhs.drop(columns=['X', 'Y'], inplace=True)

        # Change CRS EPSG 31370 (Lambert 72) into EPSG 4326 (WGS 84)
        if epsg != 4326:
            bhs = bhs.to_crs(epsg=4326)
        center = [bhs.geometry.y.mean(), bhs.geometry.x.mean()]

        # Use a satellite map
        if tiles is None:
            tiles = [{'name': 'Satellite',
                    'attributes': "Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community",
                    'url': "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"}]

        bhs_map = fm.Map(location=center, tiles='OpenStreetMap', zoom_start=zoom_start,
                         max_zoom=max_zoom, control_scale=control_scale)

        ch1 = fm.FeatureGroup(name='Boreholes')

        for idx, row in bhs.iterrows():
            fm.CircleMarker([row.geometry.y, row.geometry.x], popup=row.Name,
                            radius=radius, color=marker_color, fill_color=marker_color,
                            opacity=opacity).add_to(ch1)
            # fm.map.Marker([row.geometry.y, row.geometry.x], popup=row.Name).add_to(ch1)

        mini_map = plugins.MiniMap(toggle_display=True, zoom_level_offset=-6)

        # adding features to the base_map
        for tile in tiles:
            fm.TileLayer(name=tile['name'], tiles=tile['url'], attr=tile['attributes'],
                     max_zoom=max_zoom, control=True).add_to(bhs_map)
        ch1.add_to(bhs_map)
        fm.LayerControl().add_to(bhs_map)
        bhs_map.add_child(mini_map)

        # save in a file
        if save_as is not None:
            bhs_map.save(save_as)  # ('tmp_files/BH_location.html')

        return bhs_map

    def update_legend_cmap(self, repr_attribute_list=None, legend_dict=None, width=3,
                           compute_all_attrib=False, update_bh3d_legend=False,
                           update_project_legend=True, verbose=False):
        """Update the project cmap based on all boreholes in the project"""

        if repr_attribute_list is None:
            repr_attribute_list = [self.repr_attribute]

        if legend_dict is None:
            legend_dict = self.legend_dict

        synth_leg, detail_leg = build_bh3d_legend_cmap(bh3d_list=self.boreholes_3d, legend_dict=legend_dict,
                                                       repr_attrib_list=repr_attribute_list, width=width,
                                                       compute_all=compute_all_attrib,
                                                       update_bh3d_legend=update_bh3d_legend,
                                                       update_given_legend=update_project_legend, verbose=verbose)

        if update_project_legend:
            # print('-----------\n', legend_dict)
            self.legend_dict = legend_dict

        if not update_project_legend:
            return synth_leg, detail_leg

