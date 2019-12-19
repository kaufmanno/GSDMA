Extraction of the data on a polluted site
===========================================

The drawing below shows, what are boreholes.

Several boreholes are represented with the composition of the soil:

.. image:: ./_static/images/bh_scheme.gif
   :scale: 90 %
   :align: center
   
*Source :* http://www.abuildersengineer.com/2012/12/soil-samples-and-soil-proles.html
  
This is an example of what we would like to obtain from the data mesured on the polluted site.

The data mesured were registered in .txt file as represented below :

Borehole data  :
----------------

**Log_F10.txt** 

.. code-block:: 
   :linenos:
   
   # borehole name
   F10
   # borehole description
    start	end	description	lithology	color
    0.00	1.50	remblais non-saturés	remblais	brun
    1.50	4.00	remblais saturés	remblais	ocre
    4.00	6.00	alluvions	silt	gris
   # markers
    toit nappe	1.5
    mur remblais	4.0

Electrode data : 
-----------------

**F10.txt**
    
.. code-block:: 
   :linenos:
   
   # electrode string name
   F10
   # electrode string origin coordinates
   884.68	577.91	102.00
   # electrodes relative coordinates
   1	0.00	0.00	-5.92
   2	0.00	0.00	-4.92
   3	0.00	0.00	-3.92
   4	0.00	0.00	-2.92
   5	0.00	0.00	-1.92
   6	0.00	0.00	-0.92
   
But we discovered that in the Borehole data the word "color" should be replace by "colour" to work with Striplog !
.. ::

Legend:
--------
Initally, we add 2 files to compose the legend. These files were merged into the file legend_GSDMA.csv, in order to satisfy the striplog legend. 

**color_chart.txt**

.. code-block:: 
   :linenos:
   # color chart
   ocre	91662B
   vert	777545
   gris brun	B4A87D
   vert foncé	7A7861
   gris blanc	D9D6B7
   gris	7E8388
   gris violet	9A887F
   brun	593C1E
   brun noir	4C4532
   ind	FF6600
   blanc	FFFFFF
   noir	000000
   rouille	794324


**litho_hatches.txt**

.. code-block::
   """   
   :linenos:
   remblais	x
   silt	.--
   vide	 
   argile	- 
   argile sableuse	.-
   sable	.
   sable fin	.
   sable argileux	.-
   sable graveleux	.o
   gravier	o
   marne	/-
   marne sableuse	./-
   calcaire	-|
   calcaire altéré	\\\-
   calcaire sain	-|
   """
   
   
**legend_GSDMA.csv**

.. code-block:: python
   :linenos: 
   """   
   colour, width, comp lithology, comp colour, hatch
   #91662B,5,remblais,ocre,x
   #777545,5,None,vert,.--
   #B4A87D,5,silt,gris brun,.--
   #7A7861,5,None,vert foncé,
   #D9D6B7,5,None,gris blanc,
   #7E8388,5,None,gris,
   #9A887F,5,None,gris violet,
   #593C1E,5,remblais,brun,x
   #4C4532,5,None,brun noir,
   #FF6600,5,None,ind,
   #FFFFFF,5,None,blanc,
   #000000,5,None,noir,
   #794324,5,None,rouille,
   
   """
   
   
.. csv-table:: 
   :widths: 15 15 20 20 20 
   :header: "Header 1", "Header 2", "Header 3", "Header 4", "Header 5"
   :file: legend_GSDMA.csv

