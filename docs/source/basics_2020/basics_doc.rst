GSDMA basics 2020
====================
.. warning:: This version of the documentation is not yet up-to-date!


ORM development : SQLAlchemy
-------------------------------

.. toctree::
   :maxdepth: 2

   Principle<orm_Principle.rst>
   Building ORM classes<orm_classes.rst>
   Insertion of borehole data in the database<orm_insertion_borehole.rst>
   The final database in GSDMA 2020 release<orm_final_database.rst>


OMF development
--------------------

.. toctree::
   :maxdepth: 2

   Principle<omf_Principle.rst>
   Borehole3D class<omf_classes.rst>



Merging the OMF and ORM development
--------------------------------------------

.. toctree::
   :maxdepth: 1
    
    ORM and OMF in a single project<orm_omf_project>



Documentation work
---------------------------

.. toctree::
   :maxdepth: 1

   API documentation<API_Docs.rst>
   








Future prospects and improvements
-----------------------------------

See the remaining issue on the Github of the GSDMA Project with this `link <https://github.com/kaufmanno/GSDMA/issues>`_

Other improvements are to be considered, for example : 

- Implementing the "LinkIntervalComponent" data table to create the many-to-many relationship
- Allow the addition of additional data by creating other ORM classes and adding them to the database. For example, the data related to electrode string or the measured resistivities available in the Data folder.
- Enable the representation of Boreholes3D objects on a map using Folium, as was done in procedural programming in 2019.
- Implement a specific lexicon (instead of a default lexicon) based on available data.