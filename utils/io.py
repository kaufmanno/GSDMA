import re
import numpy as np
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
from shapely import wkt
from striplog import Striplog, Lexicon
from core.orm import BoreholeOrm, PositionOrm
from definitions import ROOT_DIR
from ipywidgets import interact, IntSlider
from IPython.display import display 


def striplog_from_text(filename, lexicon=None):
    """ 
    creates a Striplog object from a las or flat text file
    
    Parameters
    ----------
    Lexicon : dict
              A vocabulary for parsing lithologic or stratigraphic descriptions
              (default set to Lexicon.default() if lexicon is None)
              
    Returns
    -------
    strip: striplog object
    
    """
    
    if lexicon is None:
        lexicon = Lexicon.default()

    if re.compile(r".+\.las").match(filename):
        #print(f"File {filename:s} OK! Creation of the striplog ...")
        with open(filename, 'r') as las3:
            strip = Striplog.from_las3(las3.read(), lexicon)

    elif re.compile(r".+\.(csv|txt)").match(filename):
        #print(f"File {filename:s} OK! Creation of the striplog ...")
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


def boreholes_from_files(borehole_dict=None, x=None, y=None, verbose=False):
    """Creates a list of BoreholeORM objects from flat text or las files
    
    Parameters
    ----------
    boreholes_dict: dict
    
    x : list of float
        X coordinates
    
    y : list of float
        Y coordinates
    
    verbose : Bool
        allow verbose option if set = True
                    
                    
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
    
    if x is None:
        x = [0., 20., 5, 10] 
    else: 
        x=x
        
    if y is None:
        y = [0., 40., 50, 2] 
    else : 
        y=y  
    
    if (borehole_dict is None): print("Error! Borehole dict not given.")

    while (borehole_dict is not None) and bh_id<len(borehole_dict):
        for bh, filename in borehole_dict.items():
            interval_number = 0
            boreholes.append(BoreholeOrm(id=bh))
            strip = striplog_from_text(filename)
            
            for c in strip.components:
                if c not in component_dict.keys():
                    component_dict.update({c: comp_id})
                    comp_id += 1

            d = {}
            
            for interval in strip:
                top = PositionOrm(id=pos_id, upper=interval.top.upper, middle=interval.top.middle,
                                  lower=interval.top.lower, x=x[bh_id], y=y[bh_id])
                
                base = PositionOrm(id=pos_id + 1, upper=interval.base.upper, middle=interval.base.middle, lower=interval.base.lower, x=x[bh_id], y=y[bh_id])
                
                d.update({int_id: {'description': interval.description, 'interval_number': interval_number, 'top': top, 'base': base}})
                
                interval_number += 1
                int_id += 1
                pos_id += 2
                
            if verbose: print(d)
            
            boreholes[bh_id].intervals_values = d
            bh_id += 1
        components = {v: k for k, v in component_dict.items()}
        
   
    else :
        pos=bh_id
        for pos in np.arange(bh_id, len(x)) :
            bh=f'F{bh_id+1}'
            
            filename=borehole_dict.setdefault('F1') #default filename used

            interval_number = 0
            boreholes.append(BoreholeOrm(id=bh))

            strip=striplog_from_text(filename)

            for c in strip.components:
                if c not in component_dict.keys():
                    component_dict.update({c:comp_id})
                    comp_id += 1
            d ={}
            for interval in strip:
                top = PositionOrm(id=pos_id, upper=interval.top.upper, 
                                  middle=interval.top.middle,  
                                  lower=interval.top.lower, 
                                  x=x[bh_id], y=y[bh_id])

                base = PositionOrm(id=pos_id+1, upper=interval.base.upper, 
                                   middle=interval.base.middle,  
                                   lower=interval.base.lower, 
                                   x=x[bh_id], y=y[bh_id])

                d.update({int_id:{'description':interval.description, 
                                  'interval_number' : interval_number, 
                                  'top': top, 'base': base 
                                 }})

                interval_number+=1
                int_id += 1
                pos_id += 2

            if verbose: print(d)

            boreholes[bh_id].intervals_values = d
            bh_id += 1 
        components = {v:k for k,v in component_dict.items()}

    return boreholes, components


def read_gdf_file(filename=None, epsg=None, to_epsg=None, interact=False): # file_dir=None,
    """
    create a geodataframe and transform coordinates system (if 'to_epsg' is set)
    
    Parameters
    -------------
    filename: str 
        file's name and extension format (.gpkg, .json, .csv)
    
    epsg: int
        actual data Coordinates EPSG number
        
    to_epsg : int
        coordinates EPSG number to convert into
     
    file_dir : str
        Directory that contains the file
    
    Returns
    ---------
    geodataframe object
    
    """  
    
    
    
    if filename == None:
        filename = str(input("File name and extension (.json, .gpkg, .csv) ? : "))
    
    #if file_dir == None : 
     #   file_dir = ROOT_DIR + '/playground/TFE_test/tmp_files/'    
      #  filename=file_dir+filename
    

    gdf=gpd.GeoDataFrame()
    
    if re.compile(r".+\.json").match(filename):
        with open(filename, 'r') as json:
            gdf = gpd.read_file(filename)
    
    if re.compile(r".+\.gpkg").match(filename):
        with open(filename, 'r') as gpkg:
            gdf = gpd.read_file(filename)
            
    if re.compile(r".+\.csv").match(filename):
        if epsg == None:
            epsg = input("data EPSG (a number) ? : ")
            
        with open(filename, 'r') as csv:
            df = pd.read_csv(filename, header=0, sep=',')

            if 'geometry' in df.columns:
                df['geometry'] = df['geometry'].apply(wkt.loads)
                gdf = gpd.GeoDataFrame(df, geometry='geometry', crs=str("EPSG:{}".format(epsg)))

            elif ('Longitude' and 'Latitude' in df.columns) or ('longitude' and 'latitude' in df.columns):          
                df=df.rename(columns={'longitude':'Longitude', 'latitude': 'Latitude'})
                gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.Longitude, df.Latitude, crs=str("EPSG {}".format(epsg))))

            elif ('X' and 'Y' in df.columns) or ('x' and 'y' in df.columns):
                df=df.rename(columns={'x':'X', 'y': 'Y', 'Altitude':'Z'})

                if 'altitude' in df.columns or 'Altitude' in df.columns:
                    df=df.rename(columns={'altitude':'Z', 'Altitude':'Z'})

                gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.X, df.Y, crs=str("EPSG:{}".format(epsg))))
            else:
                print("Error, the input dataframe does not have the correct coordinates fields !!")

    # EPSG conversion 

    if to_epsg!=None and interact==True:
        gdf.to_crs(epsg=to_epsg, inplace=True)

        while True :
            resp = str(input("Last step before create the geodataframe\n Overwrite X,Y coordinates fields ? (y/n) : ")).strip().lower()

            if resp == 'y':      
                gdf=gdf.drop(['Longitude', 'Latitude', 'X', 'Y'], axis=1, errors='ignore')
                gdf.insert(0, 'X',[row.geometry.x for idx, row in gdf.iterrows()]) 
                gdf.insert(1, 'Y',[row.geometry.y for idx, row in gdf.iterrows()])
                break
            elif resp == 'n':
                break
            print(f'{resp} is invalid, please try again...')
            
    elif to_epsg!=None and interact==False:
        gdf.to_crs(epsg=to_epsg, inplace=True)
        gdf=gdf.drop(['Longitude', 'Latitude', 'X', 'Y'], axis=1, errors='ignore')
        gdf.insert(0, 'X',[row.geometry.x for idx, row in gdf.iterrows()]) 
        gdf.insert(1, 'Y',[row.geometry.y for idx, row in gdf.iterrows()])
             
    return gdf


def export_gdf(gdf, epsg, save_name=None):
    """
    Save data location in a geodataframe into Geopackage / GeoJson / csv file
    
    Parameters
    -----------
    gdf: geopandas.GeoDataframe object
        a dataframe from which we build the geodataframe
    
    epsg: int
        Coordinates EPSG number to be saved
    
    save_name: str
        file's name and extension format (.gpkg, .json, .csv)
    """
    
    if save_name == None:
        save_name = str(input("File name and extension (.json, .gpkg, .csv) ? : "))
    
    gdf.to_crs(epsg=str(epsg), inplace=True)

    ext=save_name[save_name.rfind('.')+1:]

    if ext == 'json':
        gdf.to_file(f'{save_name}', driver="GeoJSON")
        print(f'{save_name}'+" has been saved !" )
        
    elif ext == 'gpkg':
        gdf.to_file(f'{save_name}', driver="GPKG", layer="Boreholes")
        print(f'{save_name}'+" has been saved !" )
        
    elif ext == 'csv':
        if 'X' in gdf.columns:
            gdf=gdf.drop(['X'], axis=1)
            gdf.insert(0, 'X',gdf.geometry.x)
        else :
            gdf.insert(0, 'X',gdf.geometry.x)

        if 'Y' in gdf.columns:
            gdf=gdf.drop(['Y'], axis=1)
            gdf.insert(1, 'Y',gdf.geometry.y)
        else :
            gdf.insert(1, 'Y',gdf.geometry.y)

        gdf.to_csv(f'{save_name}', index_label="Id", index = False, sep=',')
        print(f'{save_name}'+" has been saved !" )
    else:
        print(f'file\'s name extension not given or incorrect, please choose (.json, .gpkg, .csv)')
        
            
def gdf_viewer(df, rows=10, cols=14, step_r=1, step_c=1, un_val=None):# Afficher les dataframes au moyen d'un widget (affichage dynamique)
      
    if un_val is None:
        print(f'Rows : {df.shape[0]}, columns : {df.shape[1]}')
    else:
        print(f"Rows : {df.shape[0]}, columns : {df.shape[1]}, Unique on '{un_val}': {len(set(df[un_val]))}")
    
    @interact(last_row=IntSlider(min=min(rows, df.shape[0]),max=df.shape[0],step=step_r,description='rows',
                                 readout=False,disabled=False,continuous_update=True,orientation='horizontal',
                                 slider_color='blue'),
              
              last_column=IntSlider(min=min(cols, df.shape[1]),max=df.shape[1],step=step_c,
                                    description='columns',readout=False,disabled=False,continuous_update=True,
                                    orientation='horizontal',slider_color='blue'))
    
    def _freeze_header(last_row, last_column):
        display(df.iloc[max(0, last_row-rows):last_row,
                        max(0, last_column-cols):last_column])

        
def genID_dated(gdf, col='Ref', datedef='No_date', datecol=None):
    """
    Generate a Id-dated reference for a (geo)dataframe
    
    Parameters
    -----------

    gdf : pandas.(Geo)Dataframe
    col : Reference column
    datedef : Default data's date
    datecol: Column containing dates
    """
    print('Generation of ID-dated...')
    
    if 'Date' in gdf.columns and datedef=='No_date' and datecol is None:
        print("Using 'Date' column in the (geo)dataframe !")
        #gdf[col] = gdf['Date'].apply(lambda x : str(x.year))+ '-' + gdf[col].apply(lambda x : str(x))
        Id=[]
        for Idx, row in gdf.iterrows():
            if not pd.isnull(row['Date'].year):
                Id.append(str(row['Date'].year)+'-'+str(row[col]))
            else:
                Id.append(row[col])

        gdf[col]=Id
        
    elif datedef!='No_date':
        print("Using default date given !")
        gdf[col] = datedef + '-' + gdf[col].apply(lambda x : str(x))
        
    elif datecol is not None:
        print("Using column '", datecol, "' in the (geo)dataframe !")
        gdf[col] = gdf[datecol].apply(lambda x : str(x.year))+ '-' + gdf[col].apply(lambda x : str(x))
        
    else:
        print("No date given and no column 'Date' is the (geo)dataframe, Process cancelled !")
        
    return gdf[col]       

        
def gdf_geom(gdf):
    geom = gpd.GeoSeries(gdf.apply(lambda x: Point(x['X'], x['Y']),1),crs={'init': 'epsg:31370'})
    gdf = gpd.GeoDataFrame(gdf, geometry=geom, crs="EPSG:31370")
    
    return gdf.head(5) 