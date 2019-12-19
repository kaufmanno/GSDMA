
An example of reading borehole data from an electrode string file and insert it into a SQLITE3 database
=======================================================================================================

Supervisé par O.KAUFMANN

Antoine,Arthur, Ivan. December 2019.

.. code:: ipython3

    from utils import read_flat_files
    from utils.db_tools import boreholes_dict_to_sqlite3_db
    import sqlite3

Setting parameters
~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    work_dir = './data/boreholes/'

.. code:: ipython3

    boreholes_list =['F10', 'F11', 'F12', 'F13', 'F14', 'F15', 'F16', 'F20', 'F21', 'F22', 'F23', 'F24', 'F25']

.. code:: ipython3

    database = 'project_database.db'

Reading electrode string files and storing data into the *boreholes* dictionary
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    boreholes = {}

.. code:: ipython3

    for i in boreholes_list:
        d = read_flat_files.read_boreholes_description(filename='{dir}Log_{borehole_name:s}.txt'.format(
            dir= work_dir, borehole_name=i))
        boreholes.update(d)       

.. code:: ipython3

    boreholes




.. parsed-literal::

    {'F10': {(0.0, 1.5): {'description': 'remblais non-saturés',
       'lithology': 'remblais',
       'colour': 'brun'},
      (1.5, 4.0): {'description': 'remblais saturés',
       'lithology': 'remblais',
       'colour': 'ocre'},
      (4.0, 6.0): {'description': 'alluvions',
       'lithology': 'silt',
       'colour': 'gris'},
      'markers': {'toit nappe': 1.5, 'mur remblais': 4.0}},
     'F11': {(0.0, 1.5): {'description': 'remblais non-saturés',
       'lithology': 'remblais',
       'colour': 'brun'},
      (1.5, 4.0): {'description': 'remblais saturés',
       'lithology': 'remblais',
       'colour': 'ocre'},
      (4.0, 6.0): {'description': 'alluvions',
       'lithology': 'silt',
       'colour': 'gris'},
      'markers': {'toit nappe': 1.5, 'mur remblais': 4.0}},
     'F12': {(0.0, 1.5): {'description': 'remblais non-saturés',
       'lithology': 'remblais',
       'colour': 'brun'},
      (1.5, 4.0): {'description': 'remblais saturés',
       'lithology': 'remblais',
       'colour': 'ocre'},
      (4.0, 6.0): {'description': 'alluvions',
       'lithology': 'silt',
       'colour': 'gris'},
      'markers': {'toit nappe': 1.5, 'mur remblais': 4.0}},
     'F13': {(0.0, 1.5): {'description': 'remblais non-saturés',
       'lithology': 'remblais',
       'colour': 'brun'},
      (1.5, 4.0): {'description': 'remblais saturés',
       'lithology': 'remblais',
       'colour': 'ocre'},
      (4.0, 6.0): {'description': 'alluvions',
       'lithology': 'silt',
       'colour': 'gris'},
      'markers': {'toit nappe': 1.5, 'mur remblais': 4.0}},
     'F14': {(0.0, 1.5): {'description': 'remblais non-saturés',
       'lithology': 'remblais',
       'colour': 'brun'},
      (1.5, 4.0): {'description': 'remblais saturés',
       'lithology': 'remblais',
       'colour': 'ocre'},
      (4.0, 6.0): {'description': 'alluvions',
       'lithology': 'silt',
       'colour': 'gris'},
      'markers': {'toit nappe': 1.5, 'mur remblais': 4.0}},
     'F15': {(0.0, 1.5): {'description': 'remblais non-saturés',
       'lithology': 'remblais',
       'colour': 'brun'},
      (1.5, 4.0): {'description': 'remblais saturés',
       'lithology': 'remblais',
       'colour': 'ocre'},
      (4.0, 6.0): {'description': 'alluvions',
       'lithology': 'silt',
       'colour': 'gris'},
      'markers': {'toit nappe': 1.5, 'mur remblais': 4.0}},
     'F16': {(0.0, 1.5): {'description': 'remblais non-saturés',
       'lithology': 'remblais',
       'colour': 'brun'},
      (1.5, 4.0): {'description': 'remblais saturés',
       'lithology': 'remblais',
       'colour': 'ocre'},
      (4.0, 6.0): {'description': 'alluvions',
       'lithology': 'silt',
       'colour': 'gris'},
      'markers': {'toit nappe': 1.5, 'mur remblais': 4.0}},
     'F20': {(0.0, 1.5): {'description': 'remblais non-saturés',
       'lithology': 'remblais',
       'colour': 'brun'},
      (1.5, 4.0): {'description': 'remblais saturés',
       'lithology': 'remblais',
       'colour': 'ocre'},
      (4.0, 6.0): {'description': 'alluvions',
       'lithology': 'silt',
       'colour': 'gris'},
      'markers': {'toit nappe': 1.5, 'mur remblais': 4.0}},
     'F21': {(0.0, 1.5): {'description': 'remblais non-saturés',
       'lithology': 'remblais',
       'colour': 'brun'},
      (1.5, 4.0): {'description': 'remblais saturés',
       'lithology': 'remblais',
       'colour': 'ocre'},
      (4.0, 6.0): {'description': 'alluvions',
       'lithology': 'silt',
       'colour': 'gris'},
      'markers': {'toit nappe': 1.5, 'mur remblais': 4.0}},
     'F22': {(0.0, 1.5): {'description': 'remblais non-saturés',
       'lithology': 'remblais',
       'colour': 'brun'},
      (1.5, 4.0): {'description': 'remblais saturés',
       'lithology': 'remblais',
       'colour': 'ocre'},
      (4.0, 6.0): {'description': 'alluvions',
       'lithology': 'silt',
       'colour': 'gris'},
      'markers': {'toit nappe': 1.5, 'mur remblais': 4.0}},
     'F23': {(0.0, 1.5): {'description': 'remblais non-saturés',
       'lithology': 'remblais',
       'colour': 'brun'},
      (1.5, 4.0): {'description': 'remblais saturés',
       'lithology': 'remblais',
       'colour': 'ocre'},
      (4.0, 6.0): {'description': 'alluvions',
       'lithology': 'silt',
       'colour': 'gris'},
      'markers': {'toit nappe': 1.5, 'mur remblais': 4.0}},
     'F24': {(0.0, 1.5): {'description': 'remblais non-saturés',
       'lithology': 'remblais',
       'colour': 'brun'},
      (1.5, 4.0): {'description': 'remblais saturés',
       'lithology': 'remblais',
       'colour': 'ocre'},
      (4.0, 6.0): {'description': 'alluvions',
       'lithology': 'silt',
       'colour': 'gris'},
      'markers': {'toit nappe': 1.5, 'mur remblais': 4.0}},
     'F25': {(0.0, 1.5): {'description': 'remblais non-saturés',
       'lithology': 'remblais',
       'colour': 'brun'},
      (1.5, 4.0): {'description': 'remblais saturés',
       'lithology': 'remblais',
       'colour': 'ocre'},
      (4.0, 6.0): {'description': 'alluvions',
       'lithology': 'silt',
       'colour': 'gris'},
      'markers': {'toit nappe': 1.5, 'mur remblais': 4.0}}}



Connecting to an existing database or to creating a new one if the database doesn't exist
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    conn = sqlite3.connect(database)

.. code:: ipython3

    ?boreholes_dict_to_sqlite3_db

Creating empties tables with differents fiels needed in "striplog objects" and insertting data inside those striplog objects
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Building a Lexicon for borehole data
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: ipython3

    boreholes_dict_to_sqlite3_db(boreholes, conn, commit=True, verbose=False)


.. parsed-literal::

    INSERT INTO Intervals VALUES ('F10', 0.00, 1.50, 'remblais non-saturés')
    INSERT INTO Intervals VALUES ('F10', 1.50, 4.00, 'remblais saturés')
    INSERT INTO Intervals VALUES ('F10', 4.00, 6.00, 'alluvions')
    INSERT INTO Intervals VALUES ('F11', 0.00, 1.50, 'remblais non-saturés')
    INSERT INTO Intervals VALUES ('F11', 1.50, 4.00, 'remblais saturés')
    INSERT INTO Intervals VALUES ('F11', 4.00, 6.00, 'alluvions')
    INSERT INTO Intervals VALUES ('F12', 0.00, 1.50, 'remblais non-saturés')
    INSERT INTO Intervals VALUES ('F12', 1.50, 4.00, 'remblais saturés')
    INSERT INTO Intervals VALUES ('F12', 4.00, 6.00, 'alluvions')
    INSERT INTO Intervals VALUES ('F13', 0.00, 1.50, 'remblais non-saturés')
    INSERT INTO Intervals VALUES ('F13', 1.50, 4.00, 'remblais saturés')
    INSERT INTO Intervals VALUES ('F13', 4.00, 6.00, 'alluvions')
    INSERT INTO Intervals VALUES ('F14', 0.00, 1.50, 'remblais non-saturés')
    INSERT INTO Intervals VALUES ('F14', 1.50, 4.00, 'remblais saturés')
    INSERT INTO Intervals VALUES ('F14', 4.00, 6.00, 'alluvions')
    INSERT INTO Intervals VALUES ('F15', 0.00, 1.50, 'remblais non-saturés')
    INSERT INTO Intervals VALUES ('F15', 1.50, 4.00, 'remblais saturés')
    INSERT INTO Intervals VALUES ('F15', 4.00, 6.00, 'alluvions')
    INSERT INTO Intervals VALUES ('F16', 0.00, 1.50, 'remblais non-saturés')
    INSERT INTO Intervals VALUES ('F16', 1.50, 4.00, 'remblais saturés')
    INSERT INTO Intervals VALUES ('F16', 4.00, 6.00, 'alluvions')
    INSERT INTO Intervals VALUES ('F20', 0.00, 1.50, 'remblais non-saturés')
    INSERT INTO Intervals VALUES ('F20', 1.50, 4.00, 'remblais saturés')
    INSERT INTO Intervals VALUES ('F20', 4.00, 6.00, 'alluvions')
    INSERT INTO Intervals VALUES ('F21', 0.00, 1.50, 'remblais non-saturés')
    INSERT INTO Intervals VALUES ('F21', 1.50, 4.00, 'remblais saturés')
    INSERT INTO Intervals VALUES ('F21', 4.00, 6.00, 'alluvions')
    INSERT INTO Intervals VALUES ('F22', 0.00, 1.50, 'remblais non-saturés')
    INSERT INTO Intervals VALUES ('F22', 1.50, 4.00, 'remblais saturés')
    INSERT INTO Intervals VALUES ('F22', 4.00, 6.00, 'alluvions')
    INSERT INTO Intervals VALUES ('F23', 0.00, 1.50, 'remblais non-saturés')
    INSERT INTO Intervals VALUES ('F23', 1.50, 4.00, 'remblais saturés')
    INSERT INTO Intervals VALUES ('F23', 4.00, 6.00, 'alluvions')
    INSERT INTO Intervals VALUES ('F24', 0.00, 1.50, 'remblais non-saturés')
    INSERT INTO Intervals VALUES ('F24', 1.50, 4.00, 'remblais saturés')
    INSERT INTO Intervals VALUES ('F24', 4.00, 6.00, 'alluvions')
    INSERT INTO Intervals VALUES ('F25', 0.00, 1.50, 'remblais non-saturés')
    INSERT INTO Intervals VALUES ('F25', 1.50, 4.00, 'remblais saturés')
    INSERT INTO Intervals VALUES ('F25', 4.00, 6.00, 'alluvions')
    INSERT INTO Components VALUES ('F10', 0.00, 1.50, 'lithology', 'remblais')
    INSERT INTO Components VALUES ('F10', 0.00, 1.50, 'colour', 'brun')
    INSERT INTO Components VALUES ('F10', 1.50, 4.00, 'lithology', 'remblais')
    INSERT INTO Components VALUES ('F10', 1.50, 4.00, 'colour', 'ocre')
    INSERT INTO Components VALUES ('F10', 4.00, 6.00, 'lithology', 'silt')
    INSERT INTO Components VALUES ('F10', 4.00, 6.00, 'colour', 'gris')
    INSERT INTO Components VALUES ('F11', 0.00, 1.50, 'lithology', 'remblais')
    INSERT INTO Components VALUES ('F11', 0.00, 1.50, 'colour', 'brun')
    INSERT INTO Components VALUES ('F11', 1.50, 4.00, 'lithology', 'remblais')
    INSERT INTO Components VALUES ('F11', 1.50, 4.00, 'colour', 'ocre')
    INSERT INTO Components VALUES ('F11', 4.00, 6.00, 'lithology', 'silt')
    INSERT INTO Components VALUES ('F11', 4.00, 6.00, 'colour', 'gris')
    INSERT INTO Components VALUES ('F12', 0.00, 1.50, 'lithology', 'remblais')
    INSERT INTO Components VALUES ('F12', 0.00, 1.50, 'colour', 'brun')
    INSERT INTO Components VALUES ('F12', 1.50, 4.00, 'lithology', 'remblais')
    INSERT INTO Components VALUES ('F12', 1.50, 4.00, 'colour', 'ocre')
    INSERT INTO Components VALUES ('F12', 4.00, 6.00, 'lithology', 'silt')
    INSERT INTO Components VALUES ('F12', 4.00, 6.00, 'colour', 'gris')
    INSERT INTO Components VALUES ('F13', 0.00, 1.50, 'lithology', 'remblais')
    INSERT INTO Components VALUES ('F13', 0.00, 1.50, 'colour', 'brun')
    INSERT INTO Components VALUES ('F13', 1.50, 4.00, 'lithology', 'remblais')
    INSERT INTO Components VALUES ('F13', 1.50, 4.00, 'colour', 'ocre')
    INSERT INTO Components VALUES ('F13', 4.00, 6.00, 'lithology', 'silt')
    INSERT INTO Components VALUES ('F13', 4.00, 6.00, 'colour', 'gris')
    INSERT INTO Components VALUES ('F14', 0.00, 1.50, 'lithology', 'remblais')
    INSERT INTO Components VALUES ('F14', 0.00, 1.50, 'colour', 'brun')
    INSERT INTO Components VALUES ('F14', 1.50, 4.00, 'lithology', 'remblais')
    INSERT INTO Components VALUES ('F14', 1.50, 4.00, 'colour', 'ocre')
    INSERT INTO Components VALUES ('F14', 4.00, 6.00, 'lithology', 'silt')
    INSERT INTO Components VALUES ('F14', 4.00, 6.00, 'colour', 'gris')
    INSERT INTO Components VALUES ('F15', 0.00, 1.50, 'lithology', 'remblais')
    INSERT INTO Components VALUES ('F15', 0.00, 1.50, 'colour', 'brun')
    INSERT INTO Components VALUES ('F15', 1.50, 4.00, 'lithology', 'remblais')
    INSERT INTO Components VALUES ('F15', 1.50, 4.00, 'colour', 'ocre')
    INSERT INTO Components VALUES ('F15', 4.00, 6.00, 'lithology', 'silt')
    INSERT INTO Components VALUES ('F15', 4.00, 6.00, 'colour', 'gris')
    INSERT INTO Components VALUES ('F16', 0.00, 1.50, 'lithology', 'remblais')
    INSERT INTO Components VALUES ('F16', 0.00, 1.50, 'colour', 'brun')
    INSERT INTO Components VALUES ('F16', 1.50, 4.00, 'lithology', 'remblais')
    INSERT INTO Components VALUES ('F16', 1.50, 4.00, 'colour', 'ocre')
    INSERT INTO Components VALUES ('F16', 4.00, 6.00, 'lithology', 'silt')
    INSERT INTO Components VALUES ('F16', 4.00, 6.00, 'colour', 'gris')
    INSERT INTO Components VALUES ('F20', 0.00, 1.50, 'lithology', 'remblais')
    INSERT INTO Components VALUES ('F20', 0.00, 1.50, 'colour', 'brun')
    INSERT INTO Components VALUES ('F20', 1.50, 4.00, 'lithology', 'remblais')
    INSERT INTO Components VALUES ('F20', 1.50, 4.00, 'colour', 'ocre')
    INSERT INTO Components VALUES ('F20', 4.00, 6.00, 'lithology', 'silt')
    INSERT INTO Components VALUES ('F20', 4.00, 6.00, 'colour', 'gris')
    INSERT INTO Components VALUES ('F21', 0.00, 1.50, 'lithology', 'remblais')
    INSERT INTO Components VALUES ('F21', 0.00, 1.50, 'colour', 'brun')
    INSERT INTO Components VALUES ('F21', 1.50, 4.00, 'lithology', 'remblais')
    INSERT INTO Components VALUES ('F21', 1.50, 4.00, 'colour', 'ocre')
    INSERT INTO Components VALUES ('F21', 4.00, 6.00, 'lithology', 'silt')
    INSERT INTO Components VALUES ('F21', 4.00, 6.00, 'colour', 'gris')
    INSERT INTO Components VALUES ('F22', 0.00, 1.50, 'lithology', 'remblais')
    INSERT INTO Components VALUES ('F22', 0.00, 1.50, 'colour', 'brun')
    INSERT INTO Components VALUES ('F22', 1.50, 4.00, 'lithology', 'remblais')
    INSERT INTO Components VALUES ('F22', 1.50, 4.00, 'colour', 'ocre')
    INSERT INTO Components VALUES ('F22', 4.00, 6.00, 'lithology', 'silt')
    INSERT INTO Components VALUES ('F22', 4.00, 6.00, 'colour', 'gris')
    INSERT INTO Components VALUES ('F23', 0.00, 1.50, 'lithology', 'remblais')
    INSERT INTO Components VALUES ('F23', 0.00, 1.50, 'colour', 'brun')
    INSERT INTO Components VALUES ('F23', 1.50, 4.00, 'lithology', 'remblais')
    INSERT INTO Components VALUES ('F23', 1.50, 4.00, 'colour', 'ocre')
    INSERT INTO Components VALUES ('F23', 4.00, 6.00, 'lithology', 'silt')
    INSERT INTO Components VALUES ('F23', 4.00, 6.00, 'colour', 'gris')
    INSERT INTO Components VALUES ('F24', 0.00, 1.50, 'lithology', 'remblais')
    INSERT INTO Components VALUES ('F24', 0.00, 1.50, 'colour', 'brun')
    INSERT INTO Components VALUES ('F24', 1.50, 4.00, 'lithology', 'remblais')
    INSERT INTO Components VALUES ('F24', 1.50, 4.00, 'colour', 'ocre')
    INSERT INTO Components VALUES ('F24', 4.00, 6.00, 'lithology', 'silt')
    INSERT INTO Components VALUES ('F24', 4.00, 6.00, 'colour', 'gris')
    INSERT INTO Components VALUES ('F25', 0.00, 1.50, 'lithology', 'remblais')
    INSERT INTO Components VALUES ('F25', 0.00, 1.50, 'colour', 'brun')
    INSERT INTO Components VALUES ('F25', 1.50, 4.00, 'lithology', 'remblais')
    INSERT INTO Components VALUES ('F25', 1.50, 4.00, 'colour', 'ocre')
    INSERT INTO Components VALUES ('F25', 4.00, 6.00, 'lithology', 'silt')
    INSERT INTO Components VALUES ('F25', 4.00, 6.00, 'colour', 'gris')
    colour ['brun', 'ocre', 'gris']
    lithology ['silt', 'remblais']




.. parsed-literal::

    0



.. code:: ipython3

    conn.close()
