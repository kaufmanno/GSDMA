The project of GSDMA
====================
The purpose of this project is to use the data mesured by some electrodes on a polluted site and display it in 2D and 3D.

The following schema shows how the project of Geospatial data management and analysis were organized:

.. image:: ./_static/images/Main_scheme.png
   :scale: 70 %
   :align: center
   
Firstly, we start from the boreholes description given by .txt files.
Those data are gathered into a SQLite database, in a specific organization, in 4 tables : Boreholes - Components - Intervals - Lexicon, with the format of Geopackage, which is a format for geospatial information.

Then, the data are read and put into a specific structure called Striplog.

Finally, from the striplog structure the data are displaying in 2D (using Striplog package) and in 3D (using PyVista package).

.. Redo the schema on Inkscape, developp it if necessary + explain it 