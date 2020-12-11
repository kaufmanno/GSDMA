from striplog import Striplog, Component, Lexicon, Legend, Interval, Position
import scipy
import pyvista as pv

#print("""Additional modules imported : Striplog, Component, Lexicon, Legend, Interval, Position, scipy, pyvista""")

#--------------------------------------------------------------------------------------------
def build_strip_from_list(name,dfs):
	"""
	Create a striplog from borehole's name
	:bh_test : Borehole's name (String)
	:dfs : Dict of boreholes, Intervals, Components, Lexicon data
	"""
	
	bh_strip = []  # striplog object
	intervals = dfs['Intervals'].query('borehole=="{borehole:s}"'.format(borehole=name))[['top','base', 'description']]
	
	for row in intervals.iterrows():
		components = dfs['Components'].query('borehole=="{borehole:s}" and top=={top:f} and base=={base:f}'.format(borehole=name, top=row[1]['top'], base=row[1]['base']))
		
		components_dict={}
		for r in components.iterrows():
			components_dict.update({r[1]['key']:r[1]['value']})
			
		bh_strip.append(Interval(**{'top': Position(middle=row[1]['top'], units='m'),
			'base': Position(middle=row[1]['base'], units='m'),
			'description': row[1]['description'], 'components': [Component(properties=components_dict)]}))
	
	return(bh_strip)
#-------------------------------------------------------------------------------

def add_interval_list(cylinders,intervals,plotter=None,cap=True, radius=.09, res=100):
    """ 
    add a list of intervals to a plotter 
    :param cylinders: list of cylinders to be plotted
    :param intervals: list of intervals to add to the plotter 
    :type intervals: list
    :param plotter: plotter pyvista 
    :type plotter: pyvista.plotting.plotting.Plotter
    :param radius: radius of the boreholes (if different radii, make distinct lists of intervals)
    :type radius: float
    """    
    color=['blue', 'yellow', 'red','green','purple','orange', 'brown','cyan', 'magenta']
    i, k, tmp = 0, 0, 0
    
    if plotter==None:
        plotter = pv.Plotter(shape=(1,1), window_size=[640,640])
    
    for interval in intervals:
        #print(i)
        
        i = intervals.index(interval)
        x,y=1,1
        ct = (interval.base.middle + interval.top.middle)/2
        ht = interval.base.middle - interval.top.middle
        
        cylinders.append( 
                    pv.Cylinder(
                                    center = (x,y,ct),
                                    height = ht,
                                    direction = (0.0, 0.0, 1),
                                    radius = radius,
                                    capping=cap,
                                    resolution=res,                               
                                  ),
                            )
        #print(cylinders)
    """	 
        if i!=i_tmp : 
        		k=+1
        		print("color=",k)
    
        for k in np.arange(0,len(cylinders)):
        	if c>8:
                c=0
            plotter.add_mesh(cylinders[k], color=color[c], show_edges=False)
        
    #print(type(plotter), " ; ", type(radius))
    """
    #plotter.show()
    
#----------------------------------------------------

