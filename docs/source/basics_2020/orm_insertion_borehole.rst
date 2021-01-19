Insertion of borehole data in the database
==============================================

As a reminder, in order to add entries in the database using SQLAlchemy, it is necessary to create objects based on the classes that will then be mapped on the database. This step consists in creating a BoreholeOrm and ComponentOrm object from LAS files or CSVs and then, add them to the Data Base.

Read boreholes data from files and create a list of borehole objects
---------------------------------------------------------------------

The two functions defined below allow to create a list of BorholeOrm objects and a component dictionnary.

The boreholes_dict parameter is a dictionary with the name of the boreholes to insert in the database and the associated LAS or CSV file. For example, it can be presented as follow: 

.. code:: python

 borehole_dict = {'F01':ROOT_DIR+'/data/test.las', 'F02':ROOT_DIR+'/data/test.csv'} 

If the dictionary contains data, the "boreholes_from_files()" function first determines the number of boreholes to be inserted in the DB. Then the "striplog_from_text()" function is called in order to create a striplog object from the associated LAS or CSV file (see the second function just after).

The function creates **the component dictionnary** by adding only the different components present in the Striplog object.

**The list of BoreholeOrm objects** is made by step :

 - The Id of the BoreholeOrm objects is created from the name of the borehole referenced in the boreholes_dict.
 - The IntervalOrm objects present in each borehole are created from a dictionary "d" containing the base (PositionOrm object), the top (PositionOrm object), the description and the interval_number of the intervals.

.. code:: python

 def boreholes_from_files(borehole_dict=None):
   """Creates a list of BoreholeORM objects from flat text or las files
    
    Parameters
    ----------
    boreholes_dict: dict
                    
    Returns
    -------
    boreholes: list
               boreholes object
    components: dict
                dictionnary containing ID and component
    """
    int_id = 0
    bh_id = 0
    pos_id = 0
    boreholes = []
    components = []
    comp_id = 0
    component_dict={}
    pos_dict = {}
    x = [0., 20.]
    y = [0., 120.]
    
    for bh, filename in borehole_dict.items():
        interval_number = 0
        boreholes.append(BoreholeOrm(id=bh))
        #with open(filename, 'r') as las3:
        #    strip = Striplog.from_las3(las3.read(), lexicon)
        
        strip=striplog_from_text(filename)
        
        for c in strip.components:
            if c not in component_dict.keys():
                component_dict.update({c:comp_id})
                comp_id += 1
        d ={}
        for interval in strip:
            top = PositionOrm(id=pos_id, upper=interval.top.upper, middle=interval.top.middle,  
                              lower=interval.top.lower, x=x[bh_id], y=y[bh_id])
            base = PositionOrm(id=pos_id+1, upper=interval.base.upper, middle=interval.base.middle,  
                               lower=interval.base.lower, x=x[bh_id], y=y[bh_id])
            d.update({int_id:{'description':interval.description, 'interval_number' : interval_number, 
                              'top': top, 'base': base 
                             }})
            interval_number+=1
            int_id += 1
            pos_id += 2
    
     
    
        print(d)
        boreholes[bh_id].intervals_values = d
        #boreholes[bh_id].components_values = c
        bh_id += 1 
    components = {v:k for k,v in component_dict.items()}
    return boreholes, components

This second function, already presented above, creates a Striplog object from a las or CSV file. The Striplog object will then be used directly to create the list of BoreholeOrm object and the component dictionary.




.. code:: python

 def striplog_from_text(filename, lexicon=None):
    """ creates a Striplog object from a las or flat text file
    
    Parameters
    ----------
    Lexicon : dict
              A vocabulary for parsing lithologic or stratigraphic descriptions
              (default set to Lexicon.default() if lexicon is None)
              
    Returns
    -------
    """
    strip: striplog object
    
    if lexicon is None:
        lexicon = Lexicon.default()

    if re.compile(r".+\.las").match(filename):
        print(f"File {filename:s} OK! Creation of the striplog ...")
        with open(filename, 'r') as las3:
            strip = Striplog.from_las3(las3.read(), lexicon)

    elif re.compile(r".+\.(csv|txt)").match(filename):
        print(f"File {filename:s} OK! Creation of the striplog ...")
        f = re.DOTALL | re.IGNORECASE
        regex_data = r'start.+?\n(.+?)(?:\n\n+|\n*\#|\n*$)'  # retrieve data of BH

        pattern = re.compile(regex_data, flags=f)
        with open(filename, 'r') as csv:
            text = pattern.search(csv.read()).group(1)
            text = re.sub(r'[\t]+', ';', re.sub(r'(\n+|\r\n|\r)', '\n', text.strip()))
            strip = Striplog.from_descriptions(text, dlm=';', lexicon=lexicon)

    else:
        print("Error! Please check the file extension !")
        raise

    return strip






    
Insertion of borehole objects in the data base
------------------------------------------------

To insert the borehole data into the database using SQLAlchemy, the Session object is used which adds the BoreholeOrm and ComponentOrm objects as an entry in the DB.

In the perspective of object-oriented programming, a "Project" class has been created. 

Located below, it is defined by a list of BoreholeOrm objects, a Session object from SQLAlchemy, a name and a legend object from Striplog.

.. code:: python

 class Project:
    """Create a project that will contain Borehole object
    
    Attributes
    -----------
    session : ORM Session object
    name : str
    boreholes : list of BoreholeORM object
    legend : Striplog Legend object
    Methods
    --------
    refresh(update_3d=false)
    add_borehole(self, bh)
    commit()
    add_components(self, components)
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
        self.legend = legend
        self.refresh(update_3d=True)

    def commit(self):
        'Validate all modifications done in the project'
        self.session.commit()


Different routines are implemented in the class Project such as, for example, adding the BoreholeOrm object list to the database using the function "add_borehole()" below.

The "add()" function of the session object specifies the addition of the boreholeOrm object list to the database. This addition takes place when applying the "commit()" function (define above) which validates the modifications made in the project class.

.. code:: python

    def add_borehole(self, bh):
        """Add a list of Boreholes to the project
        
        Parameters
        -----------
        bh : list
            list of Boreholes objects
            
        See Also
        ---------
        BoreholeORM : ORM borehole object
        Borehole3D : Striplog/OMF borehole object
        """
        self.session.add(bh)
        self.commit()
        self.refresh()
        list_of_intervals = get_interval_list(bh)
        self.boreholes_3d.append(Borehole3D(intervals=list_of_intervals, legend=self.legend))

The "add_components()" function will add the information from the component dictionary to the Component table of the database.

In the "add_components()" routine, the "add()" function could be used directly because the list introduced in the function contained BoreholeOrm objects. In the case of the "add_components()" routine, the parameter introduced is a component dictionary and not a Component object. It is therefore necessary to build the new_component object first, then add it to the database.


.. code:: python

    def add_components(self, components):
        """Add a list of Components to the project
        
        Parameters
        -----------
        Component : dict
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





