Building ORM classes
===================================


Philosophy in the creation of classes
_______________________________________

To implement the classes that will form the tables in the database, we need to understand the purpose of the database and how the data will be used in the rest of the project.

The purpose of this database is to reference all the useful information related to boreholes for its use in Striplog and in Pyvista. Indeed, it is useful to remember that the GSDMA project use these packages in order to represent respectively in 2D and 3D the boreholes data (lithology, geophysical data, etc.).

It is therefore necessary to create a database that can be directly used by Striplog, i.e. to arrange the data so that it can be implemented as a Striplog object. 

The study of a Striplog object demonstrated that it depends on a hierarchy of 5 objects :

 - Striplog : The main object of the hierarchy, a sequence of intervals.
 - Interval : One element from a Striplog — consists of a top, base, a description, one or more Components, and a source
 - Position : The class of the top and base objects composed of an upper, middle and lower value.
 - Component : A set of attributes, related to interval objects.
 - Lexicon : A dictionary used for rock descriptions and containing words and word categories. In the 2020 GSDMA release, we just load the default one.

Considering the classes that constitute the striplog objects, the five classes below have been implemented in the GSDMA 2020 project.


The implemented classes
__________________________

The BoreholeOrm class
---------------------------------
The main class is the BoreholeOrm class. The class allows to identify each borehole entered by the user via a unique index.

The table mapped on this class will reference the different boreholes entered in the database.

.. code:: python

 class BoreholeOrm(Base):
    """The Boreholes Info table
    
    Attributes
    ----------
    id : str
         The id of the borehole.
        
    See Also
    --------
    IntervalOrm : Relationship one to many with the IntervalOrm table.
    """
    __tablename__ = 'Boreholes'
    id = Column(String(32), primary_key=True)
    intervals = relationship(
        'IntervalOrm',
        collection_class=attribute_mapped_collection('id'),
        cascade='all, delete-orphan')
    intervals_values = association_proxy(
        'intervals', 'value',
        creator=lambda k, v: IntervalOrm(id=k, description=v['description'], interval_number=v['interval_number'],
                                         top=v['top'], base=v['base']))


The IntervalOrm class
---------------------------------
As the striplog object, the boreholeOrm object is composed by a sequence of intervals. Considering that each boreholeOrm object can be related to several intervals (one-to-many relationship), this class holds a primary key representing by a unique Id for any interval and a foreign key representing by the borehole attribute, link to the boreholeOrm object id.

The classe present also a description which represent the name of the main component contained in the interval. 

The interval_number attribute represent the number of the interval in the borehole. It starts at 0 for the upper interval of each different borehole.

Each interval object possess also a base and a top position. As in Striplog objects, these positions are linked to a Position object via the top_id and base_id attributes of the class.

.. code:: python

 class IntervalOrm(Base):
    """The Interval table
        
    Attributes
    ----------
    id : int
        The id of the interval, different for each borehole interval.
    borehole : str
              The name of the borehole from which the interval originated.
    interval_number : integer 
                     The number of the interval in the borehole, starts at 0 for the upper interval of each different borehole.
    description : str
                 The name of the main component in the interval.
    top_id : int
            The id of the top position of the interval, link to the position id in the PositionOrm table.
    base_id : int
             The id of the base position of the interval, link to the position id in the PositionOrm table.
             
    See Also
    --------
    ComponentOrm : Relationship many to many with the Intervals table using the intermediate LinkIntervalComponentOrm table.
    PositionOrm : Relationship many to one with the Intervals table
    
    """
    __tablename__ = 'Intervals'
    id = Column(Integer, primary_key=True)
    borehole = Column(String(32), ForeignKey('Boreholes.id'))
    interval_number = Column(Integer)
    components = relationship('ComponentOrm', secondary='Linkintervalcomponent')
    description = Column(String(32))
    top_id = Column(Integer, ForeignKey('Positions.id'))
    top = relationship(PositionOrm, foreign_keys=[top_id])
    base_id = Column(Integer, ForeignKey('Positions.id'))
    base = relationship(PositionOrm, foreign_keys=[base_id])
    

The PositionOrm class
---------------------------------

The Position object is constituted by an upper, a middle and a lower value of a position (the top or the base of an interval). The id of the Position class is link to a base_id or a top_id of the Interval class.

The coordinates of the position are also mentionned in this class which makes it no longer possible to impose a single position on the borehole and its intervals (with a view to implementing a deviated borehole).

.. code:: python

 class PositionOrm(Base):
    """The Position table
    
    Attributes
    ----------
    id : int
        The id of the interval, different for each borehole interval.
    upper : float
           The upper value of the position.
    middle : float
            The middle value of the position.
    lower : float
           The lower value of the position.
    x : float
        The X coordinate.
    y : float
        The Y coordinate.
    z : float
        The Y coordinate, synonym of the middle attribute.    
    """
    __tablename__ = 'Positions'
    id = Column(Integer, primary_key=True)
    upper = Column(Float(32))
    middle = Column(Float(32))
    lower = Column(Float(32))
    x = Column(Float(64), default=0.)
    y = Column(Float(64), default=0.)
    z = synonym('middle')


The ComponentOrm class
---------------------------------

In a general case, an interval can possess several components such as for example, anhydrite, limestone. Also, a component may be present in several intervals and in different boreholes.

To fix this problem of a many-to-many relationship, two new classes - ComponentOrm and LinkIntervalComponentOrm - has been created. 

Indeed, in order to implement this type of relationship with SQLAlchemy, components and intervals must be listed in separate classes. It is then necessary to create a third class whose objects are pairs of component-interval allowing this many-to-many relationship.

.. code:: python

 class ComponentOrm(Base):
    """The Component table
    
    Attributes
    ----------
    id : str
        The id of the component.
    description : str
                 The name of the component.
        
    See Also
    --------
    IntervalOrm : Relationship one to many with the IntervalOrm table.
    """
    __tablename__ = 'Components'
    id = Column(String(32), primary_key=True)
    intervals = relationship(IntervalOrm, secondary='Linkintervalcomponent')
    description = Column(String(32))



The LinkIntervalComponentOrm class 
-------------------------------------
Refer to the ComponentOrm class description above.

.. code:: python

 class LinkIntervalComponentOrm(Base):
    """The junction table between component and interval
    
    Attributes
    ----------
    id : int
        The id of the interval, different for each borehole interval.
    description : str
                 The name of the component.
    
    """
    __tablename__ = 'Linkintervalcomponent'

    int_id = Column(
        Integer,
        ForeignKey('Intervals.id'),
        primary_key=True)

    comp_id = Column(
        Integer,
        ForeignKey('Components.id'),
        primary_key=True)







