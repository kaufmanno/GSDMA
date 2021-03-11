import re
from os import walk
import numpy as np
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
from shapely import wkt
from striplog import Striplog, Lexicon, Interval
from core.orm import BoreholeOrm, PositionOrm
from definitions import ROOT_DIR
from ipywidgets import interact, IntSlider
from IPython.display import display 


def files_read(fdir, crit_col, columns=None):

    flist,files_interest=[],[]
    
    for path, dirs, files in walk(fdir):
            for f in files:
                if f[0]!='.' and re.compile(r".+\.(csv)").match(f) and f is not None:
                    flist.append('{}'.format(path+f))
    
    a,f=0,0
    df_all=pd.DataFrame()
    
    for fl in flist:
        f+=1 #files counter
        header=[]
        df=pd.read_csv(fl)
        if columns is None:
            columns=list(df.columns)
            
        for i in df.columns:
            if i in columns:
                header.append(i)
        #for col in crit_col: #use list of criteria
        #    print(col)
            
        if crit_col in header:
            a+=1 #files used counter
            print("--> ",fl.strip(fdir),f"({len(df)}lines)")
            #print("--> ",fl.strip(fdir),'\n\t',header,f'({len(df)} lines)')
            files_interest.append(fl)

            df_all=df_all.append(df[header])
            df_all.reset_index(inplace=True, drop=True)
            #df_all.fillna('', inplace=True)
            
            if 'ID' in df_all.columns:
                df_all['ID']=df_all['ID'].astype(str)
            if 'X' in df_all.columns:
                df_all['X']=df_all['X'].apply(lambda x :\
    x if isinstance(x, float) else float(x.replace(',','.')))
                df_all['Y']=df_all['Y'].apply(lambda x :\
    x if isinstance(x, float) else float(x.replace(',','.')))
                df_all['Z']=df_all['Z'].apply(lambda x :\
    x if isinstance(x, float) else float(x.replace(',','.')))
                
        elif crit_col not in header:
            print(f"criteria column not found in file {f} headers : extraction cancelled !")
    
    #print("\ndataframe lines before _gdf_geom_:", len(df_all))
    if 'X' in df_all.columns:
        df_all=gpd.GeoDataFrame(df_all, geometry=gpd.points_from_xy(df_all.X, df_all.Y, crs=str('EPSG:31370')))
    
    print("\n",f"The overall dataframe contains {len(df_all)} lines.",\
         a,"files used")
    return df_all

def striplog_from_df(df, bh_name=None, litho_col=None, thick_col=None, 
                     lexicon=None, use_default=True, verbose=False, query=True):
    """ 
    creates a Striplog object from a dataframe
    
    Parameters
    ----------
    df : Pandas.DataFrame
        dataframe that contains boreholes data
        
    litho_col : str
        dataframe column that contains lithology or description text (default:None)
    
    thick_col : str
        dataframe column that contains lithology thickness (default:None)
        
    Lexicon : dict
        A vocabulary for parsing lithologic or stratigraphic descriptions
        (set to Lexicon.default() if lexicon is None)
              
    Returns
    -------
    strip : dict of striplog objects
    
    """
    strip={}
    if lexicon is None:
        lexicon = Lexicon.default()
    
    def process(df,bh_name,litho_col,thick_col,lexicon,use_default,verbose,query):
        bh_list=[]
        
        for i in range(0,len(df)):
            if bh_name is not None and bh_name in df.columns:
                bh_id=bh_name
            else:
                bh_id=df.loc[i, 'ID']
                
            if bh_id not in bh_list:
                bh_list.append(bh_id)
                if query:
                    sql=f'ID=="{bh_id}"'
                    tmp=df.query(sql).copy() # divide and work fast ;)
                    tmp.reset_index(drop=True, inplace=True)
                else:
                    tmp=df

                intervals=[]
                for j in range(0,len(tmp)):
                    if litho_col is None:
                        litho='white sand'
                    elif litho_col in list(tmp.columns):
                        litho=tmp.loc[j,litho_col]
                    
                    if thick_col is not None and thick_col in list(tmp.columns):    
                        length=tmp.loc[j, thick_col]
                    else:
                        if use_default:
                            if verbose: print(f"|__ID:'{bh_id}' -- No length provide, treated with default (length=3)")
                            length=3
                        else:
                            length=0

                    if 'Top' in list(tmp.columns):    
                        top=tmp.loc[j, 'Top']
                    else:
                        top=0

                    if 'Base' in list(tmp.columns):    
                        base=tmp.loc[j, 'Base']
                    else:
                        base=length
                    
                    if base!=0:
                        intervals=intervals+[Interval(top=top, base=base, 
                                                  description=litho, 
                                                  lexicon=lexicon)]
                
                if len(intervals)!=0:
                    if verbose: print(f"|__ID:'{bh_id}' -- No lithology data, treated with default ('sand')")  
                    strip.update({bh_id:Striplog(list_of_Intervals=intervals)})
                else:
                    print(f"|__ID:'{bh_id}' -- Cannot create a striplog, no interval (length or base = 0)")
        return strip
    
    if litho_col is None:
        process(df,bh_name,litho_col,thick_col,lexicon,use_default,verbose,query)
    
    if litho_col in list(df.columns):
        process(df,bh_name,litho_col,thick_col,lexicon,use_default,verbose,query)
        
    elif litho_col is not None and litho_col not in list(df.columns):
        print("Error! The dataframe's columns don't match for striplog creation !")
        strip={}

    return strip


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
        #raise

    return strip


def boreholes_from_files(borehole_dict=None, x=None, y=None, verbose=False, use_default=True):
    """Creates a list of BoreholeORM objects from a list of dataframes 
        or dict of boreholes files (flat text or las files)
    
    Parameters
    ----------
    boreholes_dict: dict
    
    x : list of float
        X coordinates
    
    y : list of float
        Y coordinates
    
    verbose : Bool
        allow verbose option if set = True
    
    use_default : Bool
        allow use default when values not available if set = True
                    
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
    df=0
    
    if x is None:
        x = [0., 20., 5, 10] 
    else: 
        x=x
        
    if y is None:
        y = [0., 40., 50, 2] 
    else : 
        y=y  
    
    if (borehole_dict is None): print("Error! Borehole dictionary not given.")

    if isinstance(borehole_dict, dict):
        while (borehole_dict is not None) and bh_id<len(borehole_dict):
            print("\nFile",bh_id,"processing...\n================================")
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
                    top = PositionOrm(id=pos_id, upper=interval.top.upper, 
                                      middle=interval.top.middle,
                                      lower=interval.top.lower, 
                                      x=x[bh_id], y=y[bh_id])

                    base = PositionOrm(id=pos_id + 1, upper=interval.base.upper,
                                       middle=interval.base.middle, 
                                       lower=interval.base.lower, 
                                       x=x[bh_id], y=y[bh_id])

                    d.update({int_id: {'description': interval.description, 
                                       'interval_number': interval_number,
                                       'top': top, 'base': base
                                      }})

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
                if filename is not None or filename!='':
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

                if verbose: print(d,"\n")

                boreholes[bh_id].intervals_values = d
                bh_id += 1 
            components = {v:k for k,v in component_dict.items()}
            
   #-----------------------------------dfs------------------------------------------#  
     
    if isinstance(borehole_dict, list):
        if len(borehole_dict)==0 : print("Error ! Cannot create boreholes with empty list or dict")

        while (borehole_dict is not None) and df<len(borehole_dict):
            print("\nDatraframe",df,"processing...\n================================")
            id_list=[]
            dict_bh=0

            x=borehole_dict[df].X
            y=borehole_dict[df].Y
            if 'Diam' in borehole_dict[df].columns:
                diam=borehole_dict[df].Diam
            elif 'Diameter' in borehole_dict[df].columns:
                diam=borehole_dict[df].Diameter

            if 'Long' in borehole_dict[df].columns:
                length=borehole_dict[df].Long
            elif 'Length' in borehole_dict[df].columns:
                length=borehole_dict[df].Length

            for i,j in borehole_dict[df].iterrows():
                id_=j['ID']

                if id_ not in id_list:
                    id_list.append(id_)
                    interval_number=0

                    sql=f'ID=="{id_}"'
                    tmp=borehole_dict[df].query(sql).copy() # divide and work fast ;)
                    tmp.reset_index(drop=True, inplace=True)
                    strip=striplog_from_df(tmp, bh_name=id_, 
                                           use_default=use_default, 
                                           verbose=verbose,query=False)

                    boreholes.append(BoreholeOrm(id=id_))           

                    for k,v in strip.items():
                        for c in v.components:
                            if c not in component_dict.keys():
                                component_dict.update({c: comp_id})
                                comp_id += 1

                        d = {}

                        for interval in v:
                            #print(interval)
                            top = PositionOrm(id=pos_id, upper=interval.top.upper, 
                                              middle=interval.top.middle,
                                              lower=interval.top.lower,
                                              x=x[dict_bh], y=y[dict_bh]
                                             )

                            base = PositionOrm(id=pos_id + 1, upper=interval.base.upper, 
                                               middle=interval.base.middle, 
                                               lower=interval.base.lower, 
                                               x=x[dict_bh], y=y[dict_bh]
                                              )

                            d.update({int_id: {'description': interval.description, 
                                               'interval_number': interval_number, 
                                               'top': top, 'base': base}
                                     })

                            interval_number += 1
                            int_id += 1
                            pos_id += 2
                        
                        if verbose: print(d,"\n")
                        if dict_bh<len(boreholes): 
                            boreholes[dict_bh].intervals_values = d
                            boreholes[dict_bh].length = length[dict_bh]
                            boreholes[dict_bh].diameter = diam[dict_bh]

                        dict_bh += 1

                else:
                    if verbose:print(f"|__ID '{id_}' already treated, skip")

                components = {v: k for k, v in component_dict.items()}

            print(f"\nEnd of the process : {len(id_list)} unique ID found")
            df+=1

    elif not isinstance(borehole_dict, dict) or isinstance(borehole_dict, list):
        print('Error! Only take a dict or a dataframe to work !')
    

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
        
            
def gdf_viewer(df, rows=10, cols=14, step_r=1, step_c=1, un_val=None):# display dataframes with  a widget
      
    if un_val is None:
        print(f'Rows : {df.shape[0]}, columns : {df.shape[1]}')
    else:
        print(f"Rows : {df.shape[0]}, columns : {df.shape[1]}, Unique on '{un_val}': {len(set(df[un_val]))}")
    
    @interact(last_row=IntSlider(min=min(rows, df.shape[0]),max=df.shape[0],
                                 step=step_r,description='rows',readout=False,
                                 disabled=False,continuous_update=True,
                                 orientation='horizontal',slider_color='blue'),
              last_column=IntSlider(min=min(cols, df.shape[1]),
                                    max=df.shape[1],step=step_c,
                                    description='columns',readout=False,
                                    disabled=False,continuous_update=True,
                                    orientation='horizontal',slider_color='blue')
             )
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
    #geom = gpd.GeoSeries(gdf.apply(lambda x: Point(x['X'], x['Y']),1),crs={'init': 'epsg:31370'})
    #gdf = gpd.GeoDataFrame(gdf, geometry=geom, crs="EPSG:31370")
    
    gdf= gpd.GeoDataFrame(gdf, geometry=gpd.points_from_xy(gdf.X, gdf.Y, crs=str('EPSG:31370')))
    
    return gdf