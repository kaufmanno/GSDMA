"""
orm example
===========
This example shows one way of using the orm classes.
"""

# # Example of using the orm classes

# Imports

# In[1]:


from os import remove
from core.core import Project
from core.orm import BoreholeOrm, PositionOrm, Base
from striplog import Lexicon, Striplog
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


# In[2]:


remove('./tmp/test_orm_db.db')


# Create the db engine and the database structure

# In[3]:


engine = create_engine('sqlite:///tmp/test_orm_db.db', echo=True)


# In[4]:


Base.metadata.create_all(engine)


# Create the objects from las files

# In[5]:


lexicon = Lexicon.default()


# In[6]:


borehole_dict = {'F01':'../data/test.las', 'F02':'../data/test.las'} # boreholes to insert into the db


# In[7]:


int_id = 0
bh_id = 0
pos_id = 0
boreholes = []
components = []
comp_id = 0
component_dict={}
pos_dict = {}
x = [0., 20.]
y = [0., 20.]
for bh, filename in borehole_dict.items():
    interval_number = 0
    boreholes.append(BoreholeOrm(id=bh))
    with open(filename, 'r') as las3:
        strip = Striplog.from_las3(las3.read(), lexicon)
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


# Create the session

# In[8]:


Session = sessionmaker(bind=engine)
session = Session()


# Create the project

# In[9]:


p = Project(session)
p.add_components(components)


# Add boreholes into the database

# In[10]:


for bh in boreholes:
    p.add_borehole(bh)


# In[11]:


p.boreholes[0].id


# In[12]:


p.commit()


# In[13]:


p.boreholes[0].intervals[0].description


# In[14]:


session.close()

