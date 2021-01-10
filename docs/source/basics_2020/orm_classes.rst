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

Considering the classes that make up the striplog objects, the classes below have been implemented in the GSDMA 2020 project.


The classes implemented
__________________________

The class BoreholeOrm
---------------------------------


The class IntervalOrm
---------------------------------


The class PositionOrm
---------------------------------


The class ComponentOrm
---------------------------------



The class LinkIntervalComponentOrm
-------------------------------------






