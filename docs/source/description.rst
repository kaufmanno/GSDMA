Description
===========


This project of geospatial data management and analysis supervised by Mr Kaufmann consists of displaying data extracted on a polluted industrial site in 2D and 3D in order to have a good representation of the composition of the soil. These data are about the lythology of boreholes realised on the polluted site and géophysics results such as resistivity mesured by some electrodes. 

Firstly, the program start from the boreholes description given by .txt files. Those data are gathered into a SQLite database, in a specific organization, in 4 tables : Boreholes - Components - Intervals - Lexicon, with the format of Geopackage, which is a format for geospatial information.

Then, the data are read and put into a specific structure called Striplog.

Finally, from the striplog structure the data are displaying in 2D (using Striplog package) and in 3D (using PyVista package).


Summary
-------------

.. toctree::
   :maxdepth: 2

   GSDMA Objectives: 2019 objectives<summary/2019_project_review.rst>
   Project release 2020<summary/Objectives_and_achievements_of_the_2020_project.rst>
   Object-oriented programming<summary/Object_oriented_programming.rst>
   Improving documentation<summary/improving_documentation.rst>
   Packages used in GSDMA<summary/packages.rst>

Contributing
------------

When contributing to this repository, please first discuss the change you wish to make via issue, email, or any other method with the owners of this repository before making a change.

Please note we have a `code of conduct <https://github.com/kaufmanno/GSDMA/blob/master/CODE_OF_CONDUCT.md>`_, please follow it in all your interactions with the project.

To further notice: `CONTRIBUTING.md <https://github.com/kaufmanno/GSDMA/blob/improvedocs/README.md>`_

License
-------

The license of the project is avalaible `here
<https://github.com/kaufmanno/GSDMA/blob/master/LICENSE>`_.

Contact
-------

We are interested in your feed back. Please contact us at:

Olivier Kaufmann

Contributors
------------

Olivier Kaufmann, Yanick N'Depo, Quentin Campeol, Joris Coron, Joseph Wandji Kamwa, Isaac Assiene, Antoine Iragena,
Arthur Heymans, Ivan Nanfo

