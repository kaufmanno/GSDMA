Implementation of Borehole3D class
===================================
The first idea developed in the 2019 version of the GSDMA project was the creation of a tool which can represent 2D data acquired along a borehole. These data can be classified in 2 categories:

- geological information (lithology encountered, color, thickness, ...)
- specific measurements (geophysical data, temperature, ...)

But in a study, there is more than one borehole, and each borehole must be modeled with its own characteristics, independently from the others : hence the need to move to an object-oriented implementation.

In the 2020 version of the project, the **Borehole3D** class was built to meet this need. This class has been built based on the Striplog module to easily represent geological data, and on some classes of the omf and omfvista modules to allow the 3D representation of each borehole.

*Borehole3D as a Striplog object*
-------------------------------------------
As the **Borehole3D** object must represent geological information, it was judicious to make it inherit the attributes and methods of the **Striplog** class. When Borehole3D class is instanciate, it can take, as parameters, lists of objects *Interval*, *Component*, *Legend* from the Striplog module. Finally the Borehole3D object works as a Striplog object and it is composed of Intervals, themselves composed of Components, each with its own Decor to build a Legend.


.. code:: python

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
            with open(ROOT_DIR + '/data/test.las', 'r') as las3:
                default_intv = Striplog.from_las3(las3.read(), lexicon)
                intervals = list(default_intv)
            print("Pay attention that default intervals are actually used !\n")
            
        self.intervals = intervals
        self.geometry = []

        # instantiation with supers properties
        Striplog.__init__(self, list_of_Intervals=self.intervals)

        # self.uid=uuid #get a unique for identification of borehole in the project

        self.build_geometry()




*Borehole3D as an omf object*
-------------------------------------------
At this level, the trick used is not inheritance but the definition of a specific property of the **Borehole3D** object (*geometry*), allowing to take advantage of some of the methods of the *LineSetElement* class in the **omf** package. 

This property is constructed to contain the spatial information of a LineSetElement object by defining a geometry. This property offers the possibility to name each borehole in an intrinsic way : it is not the name assigned when defining a variable but rather a specific property of the LineSetElement objects. This is an essential point for the user to differentiate and recognize each borehole.

The definition of the borehole geometry is performed by the **Borehole3D** class method `build_geometry()`_.


*3D representation of Borehole3D object*
-------------------------------------------

Finally comes the stage of three-dimensional representation. For this, the modules omfvista and pyvista were used. 

**omfvista** serves as an interface between **pyvista (vtk)** and omf in order to provide 3D visualization and to allow the use of meshes for data processing in OMF specifications. Thus, the use of omfvista's *line_set_to_vtk* class allowed to convert the **Borehole3D** object, via its geometry, into a *PolyData* object usable by pyvista for 3D representation. 

The 3D display is realized by invocation of the `plot3d()`_ method of the **Borehole3D** class, otherwise the call of a Borehole3D type variable simply leads to the 2D display.

Methods of Borehole3D class
----------------------------------------

*get_components_indices()* 
_____________________________

This method returns an array of indices for all geological formations (components) find in a borehole.

.. code:: python 

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

.. _*build_geometry()* : 

*build_geometry()* 
_______________________________________

This method is used to build the geometry of the Borehole3D object. As an omf.LineSetGeometry, this property needs at least vertices and segments arrays. So, considering each interval in the borehole, the method add the X,Y,Z coordinates of the top and the base to vertices and segments array. 

To wrap each component in the borehole with its decor (legend), an omf_legend property has been designed. This omf_legend is built from an external function (`striplog_legend_to_omf_legend()`_) by converting Striplog legend to an *omf.data.legend*.

.. code:: python 

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
        


.. _*plot3d()* :

*plot3d()* 
_______________

When this method is called, it create an 3D display of the borehole. It converts the borehole3D geometry to a vtk mapping that will be used by pyvista for tridimensional display. This display can be interactive if the parameter x3d is set TRUE.

.. code:: python 

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
    'please read  <a href="https://doc.x3dom.org/tutorials/animationInteraction/navigation/index.html">the docs</a>  \n</p>\n' \
    '<x3d width=\'968px\' height=\'600px\'>\n <scene>\n' \
    '<viewpoint position="-1.94639 1.79771 -2.89271" orientation="0.03886 0.99185 0.12133 3.75685">' \
    '</viewpoint>\n <Inline nameSpaceName="Borehole" mapDEFToID="true" url="' + filename + '" />\n' \
    '</scene>\n</x3d>\n</body>\n</html>\n'
            return HTML(x3d_html)



.. _`striplog_legend_to_omf_legend()` :

external function
----------------------

.. code:: python

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


