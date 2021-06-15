import re
from os import walk
import numpy as np
import geopandas as gpd
import pandas as pd
from shapely import wkt
from striplog import Striplog, Lexicon, Interval, Component, Position
from utils.lexicon import Lexicon_FR_updated as lexicon_fr
from core.orm import BoreholeOrm, PositionOrm
from ipywidgets import interact, IntSlider
from IPython.display import display
from utils.config import DEFAULT_BOREHOLE_LENGTH, DEFAULT_BOREHOLE_DIAMETER, DEFAULT_LITHOLOGY
from utils.utils import update_dict


def df_from_sources(search_dir, filename, columns=None, verbose=False):
    """
    """

    f_list, files_interest = [], []

    for path, dirs, files in walk(search_dir):
        for f in files:
            if f[0] != '.' and re.compile(f'{filename}\.(csv)').match(f) and f is not None:
                f_list.append(f'{path}/{f}')

    a, f = 0, 0
    df_all = pd.DataFrame()

    for fl in f_list:
        f += 1  # files counter
        header = []
        df = pd.read_csv(fl)
        if columns is None:
            columns = list(df.columns)

        for i in df.columns:
            if i in columns:
                header.append(i)
        # for col in crit_col: #use list of criteria
        #    print(col)
        if verbose:
            print(f'columns in header for file {fl}: {header}')

        print(f'--> {fl.replace(search_dir,"")}: ({len(df)} lines)')
        #files_interest.append(fl)

        if 'ID' in df.columns:
            df['ID'] = df['ID'].astype(str)
        if 'X' in df.columns:
            a += 1  # files used counter
            df['X'] = df['X'].apply(lambda x: x if isinstance(x, float) else float(x.replace(',', '.')))
            df['Y'] = df['Y'].apply(lambda x: x if isinstance(x, float) else float(x.replace(',', '.')))
            df['Z'] = df['Z'].apply(lambda x: x if isinstance(x, float) else float(x.replace(',', '.')))
            df_all = df_all.append(df[header])  # files must contains position to be kept
            df_all.reset_index(inplace=True, drop=True)
            # df_all.fillna('', inplace=True)

    # if 'X' in df_all.columns:
    df_all = gpd.GeoDataFrame(df_all, geometry=gpd.points_from_xy(df_all.X, df_all.Y, crs=str('EPSG:31370')))

    print(f'\nThe overall dataframe contains {len(df_all)} lines. {a} files used')
    return df_all

def read_files(fdir, crit_col, columns=None, verbose=False):

    flist, files_interest = [] , []
    
    for dir, dirs, files in walk(fdir):
            for f in files:
                if f[0] != '.' and re.compile(r".+\.(csv)").match(f) and f is not None:
                    flist.append(f'{dir}/{f}')
    
    a, f = 0, 0
    df_all = pd.DataFrame()
    
    for fl in flist:
        f += 1  # files counter
        header = []
        df = pd.read_csv(fl)
        if columns is None:
            columns = list(df.columns)
            
        for i in df.columns:
            if i in columns:
                header.append(i)
        #for col in crit_col: #use list of criteria
        #    print(col)
        if verbose:
            print(f'columns in header for file {fl}: {header}')
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
            print(f'criteria column not found in file {f} headers : extraction cancelled !')
    
    #print("\ndataframe lines before _gdf_geom_:", len(df_all))
    if 'X' in df_all.columns:
        df_all=gpd.GeoDataFrame(df_all, geometry=gpd.points_from_xy(df_all.X, df_all.Y, crs=str('EPSG:31370')))
    
    print(f'\nThe overall dataframe contains {len(df_all)} lines. {a} files used')
    return df_all


def get_interval_list(bh, lexicon='en'):
    """create a list of interval from a list of boreholeORM ojects

    Parameters
    ----------
    bh: list
        list of boreholeORM
    lexicon : dict
        lexicon to retrieve lithological information from descriptions

    Returns
    -------
    interval_list: list
                   list of Interval objects

    """

    if lexicon == 'en':
        lexicon = Lexicon.default()
    elif lexicon == 'fr':
        lexicon = Lexicon(lexicon_fr.LEXICON)
    elif isinstance(lexicon, Lexicon):
        lexicon = lexicon
    else:
        raise (TypeError(f"Must provide a lexicon, not '{type(lexicon)}', excepted 'en' or 'fr'"))

    interval_list, depth = [], []
    for i in bh.intervals.values():
        top = Position(upper=i.top.upper, middle=i.top.middle, lower=i.top.lower, x=i.top.x, y=i.top.y)
        base = Position(upper=i.base.upper, middle=i.base.middle, lower=i.base.lower, x=i.top.x, y=i.top.y)
        comp = Component.from_text(i.description, lexicon=lexicon)
        interval_list.append(Interval(top=top, base=base, description=i.description, components=[comp]))
        depth.append(i.base.middle)
    return interval_list, max(depth)


def striplog_from_df(df, litho_col, bh_name=None, litho_top_col=None,
                     litho_base_col=None, thick_col=None, color_col=None,
                     lexicon='en', use_default=True, verbose=False, query=True):
    """ 
    creates a Striplog object from a dataframe
    
    Parameters
    ----------
    df : Pandas.DataFrame
        dataframe that contains boreholes data
    bh_name: str
        Borehole name (or ID)
    litho_col : str
        dataframe column that contains lithology or description text (default:None)
    
    thick_col : str
        dataframe column that contains lithology thickness (default:None)
        
    lexicon : dict
        A vocabulary for parsing lithological or stratigraphic descriptions
        (set to Lexicon.default() if lexicon is None)
              
    Returns
    -------
    strip : dict of striplog objects
    
    """
    litho_cdt, litho_top_cdt, litho_base_cdt = False, False, False
    thick_cdt, color_cdt = False, False

    if litho_col is not None and litho_col in list(df.columns):
        litho_cdt = True
    if thick_col is not None and thick_col in list(df.columns):
        thick_cdt = True
    if litho_top_col is not None and litho_top_col in list(df.columns):
        litho_top_cdt = True
    if litho_base_col is not None and litho_base_col in list(df.columns):
        litho_base_cdt = True
    if color_col is not None and color_col in list(df.columns):
        color_cdt = True

    if lexicon == 'en':
        lexicon = Lexicon.default()
    elif lexicon == 'fr':
        lexicon = Lexicon(lexicon_fr.LEXICON)
    elif isinstance(lexicon, Lexicon):
        lexicon = lexicon
    else:
        raise (TypeError(f"Must provide a lexicon, not '{type(lexicon)}', excepted 'en' or 'fr'"))

    strip = {}
    bh_list = []

    for i in df.index:
        if bh_name is not None and bh_name in df.columns:
            bh_id = bh_name
        else:
            bh_id = df.loc[i, 'ID']

        if bh_id not in bh_list:
            print(f"|__ID:\'{bh_id}\'")
            bh_list.append(bh_id)
            if query:
                sql = df['ID'] == f"{bh_id}"  # f'ID=="{bh_id}"'
                tmp = df[sql].copy()  # df.query(sql).copy()  # divide to work fast ;)
                tmp.reset_index(drop=True, inplace=True)
            else:
                tmp = df

            intervals = []

            for j in tmp.index:
                # lithology processing -------------------------------------------
                if litho_cdt and color_cdt :
                    litho = f"{tmp.loc[j, litho_col]} {tmp.loc[j, color_col]}"
                elif litho_cdt :
                    litho = tmp.loc[j, litho_col]
                else:
                    raise(KeyError(f"Error : '{litho_col}' not in the dataframe's columns !"))

                # create components from lithological description
                if Component.from_text(litho, lexicon) == Component({}):  # empty component !
                    print(f"Error : No lithology matching with '{litho}' in given lexicon")
                    if use_default:
                        print(f"Warning : ++ interval's component replaced by default ('{DEFAULT_LITHOLOGY}')")
                        litho = DEFAULT_LITHOLOGY
                        component = Component.from_text(litho, Lexicon.default())
                else:
                    component = Component.from_text(litho, lexicon)

                # length processing -----------------------------------------------
                if thick_cdt and not pd.isnull(tmp.loc[j, thick_col]):
                    thick = tmp.loc[j, thick_col]
                else:
                    if use_default:
                        print(f'Warning : ++ No thickness provided, default is used '
                                  f'(length={DEFAULT_BOREHOLE_LENGTH})')
                        thick = DEFAULT_BOREHOLE_LENGTH
                    else:
                        raise(ValueError('Cannot create interval with null thickness !'))

                # intervals processing ----------------------------------------------
                if litho_top_cdt:
                    top = tmp.loc[j, litho_top_col]
                elif thick_cdt:
                    if j == tmp.index[0]:
                        top = 0
                    else:
                        top += tmp.loc[j-1, thick_col]
                else:
                    raise(ValueError('Cannot retrieve or compute top values. provide thickness values! '))

                if litho_base_cdt:
                    base = tmp.loc[j, litho_base_col]
                else:
                    base = top + thick

                if base != 0.:
                    intervals = intervals + [
                        Interval(top=top, base=base, description=litho, components=[component], lexicon=lexicon)]

            if len(intervals) != 0:
                strip.update({bh_id: Striplog(list_of_Intervals=intervals)})
            else:
                print(f"Error : -- Cannot create a striplog, no interval (length or base = 0)")

    print(f"Summary : {list(strip.values())}")

    return strip


def striplog_from_text(filename, lexicon='en'):
    """ 
    creates a Striplog object from a las or flat text file
    
    Parameters
    ----------
    filename : str name of text file
    lexicon : dict
              A vocabulary for parsing lithologic or stratigraphic descriptions
              (default set to Lexicon.default() if lexicon is None)
              
    Returns
    -------
    strip: striplog object
    
    """

    if lexicon == 'en':
        lexicon = Lexicon.default()
    elif lexicon == 'fr':
        lexicon = Lexicon(lexicon_fr.LEXICON)
    elif isinstance(lexicon, Lexicon):
        lexicon = lexicon
    else:
        raise(TypeError(f"Must provide a lexicon, not '{type(lexicon)}', excepted 'en' or 'fr'"))

    if re.compile(r".+\.las").match(filename):
        # print(f"File {filename:s} OK! Creation of the striplog ...")
        with open(filename, 'r') as las3:
            strip = Striplog.from_las3(las3.read(), lexicon)

    elif re.compile(r".+\.(csv|txt)").match(filename):
        # print(f"File {filename:s} OK! Creation of the striplog ...")
        f = re.DOTALL | re.IGNORECASE
        regex_data = r'start.+?\n(.+?)(?:\n\n+|\n*\#|\n*$)'  # retrieve data of BH

        pattern = re.compile(regex_data, flags=f)
        with open(filename, 'r') as csv:
            text = pattern.search(csv.read()).group(1)
            text = re.sub(r'[\t]+', ';', re.sub(r'(\n+|\r\n|\r)', '\n', text.strip()))
            strip = Striplog.from_descriptions(text, dlm=';', lexicon=lexicon)

    else:
        print("Error! Please check the file extension !")
        # raise

    return strip


def boreholes_from_files(boreholes_dict=None, x=None, y=None,
                         diam_field='Diameter', thick_field='Length', color_field='Color',
                         litho_field=None, litho_top_field=None, litho_base_field=None,
                         lexicon='en', verbose=False, use_default=True):
    """Creates a list of BoreholeORM objects from a list of dataframes 
        or dict of boreholes files (flat text or las files)
    
    Parameters
    ----------
    boreholes_dict: dict A dictionary of boreholes: files
    
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
                dictionary containing ID and component

    """

    int_id = 0  # interval id
    bh_id = 0  # borehole id
    pos_id = 0  # position id
    boreholes = []
    components = []
    comp_id = 0  # component id
    component_dict = {}
    link_dict = {}  # link between intervals and components (<-> junction table)
    df_id = 0  # dataframe id

    # if x is None:
    #     x = [0., 20., 5, 10]
    # else:
    #     x = x
    #
    # if y is None:
    #     y = [0., 40., 50, 2]
    # else:
    #     y = y

    if boreholes_dict is None:
        print("Error! Borehole dictionary not given.")

    # ------------------ argument is a dict of files ---------------------------------------
    if isinstance(boreholes_dict, dict):
        while (boreholes_dict is not None) and bh_id < len(boreholes_dict):
            print(f'\nFile {bh_id} processing...\n================================')
            for bh, filename in boreholes_dict.items():
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

                    for idx in interval.components:
                        if idx != Component({}):
                            link_dict.update({(int_id, component_dict[idx]): {'extra_data': ''}})

                    interval_number += 1
                    int_id += 1
                    pos_id += 2

                if verbose:
                    print(f'{d}\n')

                boreholes[bh_id].intervals_values = d
                bh_id += 1
            components = {v: k for k, v in component_dict.items()}

        else:
            for pos in np.arange(bh_id, len(x)):
                bh = f'F{bh_id + 1}'
                print(f'bh: {bh}, pos: {pos}')

                filename = boreholes_dict.setdefault('F1')  # default filename used

                interval_number = 0
                boreholes.append(BoreholeOrm(id=bh))

                if filename is not None and filename != '':
                    strip = striplog_from_text(filename, lexicon)
                else:
                    strip = None

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
                                       'top': top, 'base': base}
                              })

                    for idx in interval.components:
                        if idx != Component({}):
                            link_dict.update({(int_id, component_dict[idx]): {'extra_data': ''}})

                    interval_number += 1
                    int_id += 1
                    pos_id += 2

                if verbose:
                    print(f'{d}\n')

                boreholes[bh_id].intervals_values = d
                bh_id += 1
            components = {v: k for k, v in component_dict.items()}

    # ----------------------------argument is a list of dataframes------------------------------------

    elif isinstance(boreholes_dict, list):
        if len(boreholes_dict) == 0:
            print("Error ! Cannot create boreholes with empty list or dict")

        while (boreholes_dict is not None) and df_id < len(boreholes_dict):
            print(f'\nDataframe {df_id} processing...\n================================')
            bh_id_list = []  #
            bh_idx = 0  # borehole index in the current dataframe

            #x = boreholes_dict[df_id].X
            #y = boreholes_dict[df_id].Y

            if diam_field in boreholes_dict[df_id].columns:
                diam = boreholes_dict[df_id][diam_field]
            else:
                diam = pd.Series([DEFAULT_BOREHOLE_DIAMETER] * len(boreholes_dict[df_id]))
                if verbose:
                    print(f'Warning : -- No borehole diameter, default is used (diameter={DEFAULT_BOREHOLE_DIAMETER})')

            for idx, row in boreholes_dict[df_id].iterrows():
                bh_name = row['ID']

                if bh_name not in bh_id_list:
                    bh_id_list.append(bh_name)
                    boreholes.append(BoreholeOrm(id=bh_name))
                    interval_number = 0

                    bh_selection = boreholes_dict[df_id]['ID'] == f"{bh_name}"
                    tmp = boreholes_dict[df_id][bh_selection].copy()
                    tmp.reset_index(drop=True, inplace=True)
                    strip = striplog_from_df(df=tmp, bh_name=bh_name, litho_col=litho_field,
                                             litho_top_col=litho_top_field,
                                             litho_base_col=litho_base_field,
                                             thick_col=thick_field,
                                             color_col=color_field,
                                             use_default=use_default,
                                             verbose=verbose, lexicon=lexicon,
                                             query=False)

                    for v in strip.values():
                        for c in v.components:
                            if c not in component_dict.keys():
                                component_dict.update({c: comp_id})
                                comp_id += 1

                        d = {}

                        # ORM processing
                        for interval in v:
                            top = PositionOrm(id=pos_id, upper=interval.top.upper,
                                              middle=interval.top.middle,
                                              lower=interval.top.lower,
                                              x=row['X'], y=row['Y']
                                              )

                            base = PositionOrm(id=pos_id + 1, upper=interval.base.upper,
                                               middle=interval.base.middle,
                                               lower=interval.base.lower,
                                               x=row['X'], y=row['Y']
                                               )

                            d.update({int_id: {'description': interval.description,
                                               'interval_number': interval_number,
                                               'top': top, 'base': base}
                                      })

                            for idx in interval.components:
                                if idx != Component({}):
                                    link_dict.update({(int_id, component_dict[idx]): {'extra_data': ''}})

                            interval_number += 1
                            int_id += 1
                            pos_id += 2

                        if verbose:
                            print(f'{d}\n')
                        if bh_idx < len(boreholes):
                            boreholes[bh_idx].intervals_values = d
                            boreholes[bh_idx].length = tmp[thick_field].cumsum().max()
                            if diam[bh_idx] is not None and not pd.isnull(diam[bh_idx]):
                                boreholes[bh_idx].diameter = tmp[diam_field][0]
                            else:
                                boreholes[bh_idx].diameter = DEFAULT_BOREHOLE_DIAMETER

                        bh_idx += 1

                else:
                    pass

                components = {v: k for k, v in component_dict.items()}

            print(f"\nEnd of the process : {len(bh_id_list)} unique ID found")
            df_id += 1

    elif not isinstance(boreholes_dict, dict) or isinstance(boreholes_dict, list):
        raise(TypeError('Error! use a dict or a dataframe !'))

    return boreholes, components, link_dict


def read_gdf_file(filename=None, epsg=None, to_epsg=None, interact=False):  # file_dir=None,
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

    
    Returns
    ---------
    geodataframe object
    
    """

    if filename is None:
        filename = str(input("File name and extension (.json, .gpkg, .csv) ? : "))

    # if file_dir == None :
    #   file_dir = ROOT_DIR + '/playground/TFE_test/tmp_files/'
    #  filename=file_dir+filename

    gdf = gpd.GeoDataFrame()

    if re.compile(r".+\.json").match(filename):
        with open(filename, 'r'):
            gdf = gpd.read_file(filename)

    if re.compile(r".+\.gpkg").match(filename):
        with open(filename, 'r'):
            gdf = gpd.read_file(filename)

    if re.compile(r".+\.csv").match(filename):
        if epsg is None:
            epsg = input("data EPSG (a number) ? : ")

        with open(filename, 'r'):
            df = pd.read_csv(filename, header=0, sep=',')

            if 'geometry' in df.columns:
                df['geometry'] = df['geometry'].apply(wkt.loads)
                gdf = gpd.GeoDataFrame(df, geometry='geometry', crs=str("EPSG:{}".format(epsg)))

            elif ('Longitude' and 'Latitude' in df.columns) or ('longitude' and 'latitude' in df.columns):
                df = df.rename(columns={'longitude': 'Longitude', 'latitude': 'Latitude'})
                gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.Longitude, df.Latitude,
                                                                       crs=str("EPSG {}".format(epsg))))

            elif ('X' and 'Y' in df.columns) or ('x' and 'y' in df.columns):
                df = df.rename(columns={'x': 'X', 'y': 'Y', 'Altitude': 'Z'})

                if 'altitude' in df.columns or 'Altitude' in df.columns:
                    df = df.rename(columns={'altitude': 'Z', 'Altitude': 'Z'})

                gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.X, df.Y, crs=str("EPSG:{}".format(epsg))))
            else:
                print("Error, the input dataframe does not have the correct coordinates fields !!")

    # EPSG conversion 

    if to_epsg is not None and interact:
        gdf.to_crs(epsg=to_epsg, inplace=True)

        while True:
            resp = str(input(
                "Last step before create the geodataframe\n "
                "Overwrite X,Y coordinates fields ? (y/n) : ")).strip().lower()

            if resp == 'y':
                gdf = gdf.drop(['Longitude', 'Latitude', 'X', 'Y'], axis=1, errors='ignore')
                gdf.insert(0, 'X', [row.geometry.x for idx, row in gdf.iterrows()])
                gdf.insert(1, 'Y', [row.geometry.y for idx, row in gdf.iterrows()])
                break
            elif resp == 'n':
                break
            print(f'{resp} is invalid, please try again...')

    elif to_epsg is not None and interact is False:
        gdf.to_crs(epsg=to_epsg, inplace=True)
        gdf = gdf.drop(['Longitude', 'Latitude', 'X', 'Y'], axis=1, errors='ignore')
        gdf.insert(0, 'X', [row.geometry.x for idx, row in gdf.iterrows()])
        gdf.insert(1, 'Y', [row.geometry.y for idx, row in gdf.iterrows()])

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

    if save_name is None:
        save_name = str(input("File name and extension (.json, .gpkg, .csv) ? : "))

    gdf.to_crs(epsg=str(epsg), inplace=True)

    ext = save_name[save_name.rfind('.') + 1:]

    if ext == 'json':
        gdf.to_file(f'{save_name}', driver="GeoJSON")
        print(f'{save_name}' + " has been saved !")

    elif ext == 'gpkg':
        gdf.to_file(f'{save_name}', driver="GPKG", layer="Boreholes")
        print(f'{save_name}' + " has been saved !")

    elif ext == 'csv':
        if 'X' in gdf.columns:
            gdf = gdf.drop(['X'], axis=1)
            gdf.insert(0, 'X', gdf.geometry.x)
        else:
            gdf.insert(0, 'X', gdf.geometry.x)

        if 'Y' in gdf.columns:
            gdf = gdf.drop(['Y'], axis=1)
            gdf.insert(1, 'Y', gdf.geometry.y)
        else:
            gdf.insert(1, 'Y', gdf.geometry.y)

        gdf.to_csv(f'{save_name}', index_label="Id", index=False, sep=',')
        print(f'{save_name}' + " has been saved !")
    else:
        print(f'file\'s name extension not given or incorrect, please choose (.json, .gpkg, .csv)')


def gdf_viewer(df, rows=10, cols=12, step_r=1, step_c=1, un_val=None, view=True):  # display dataframes with  a widget

    if un_val is None:
        print(f'Rows : {df.shape[0]}, columns : {df.shape[1]}')
    else:
        print(f"Rows : {df.shape[0]}, columns : {df.shape[1]}, Unique col '{un_val}': {len(set(df[un_val]))}")

    if view:
        @interact(last_row=IntSlider(min=min(rows, df.shape[0]), max=df.shape[0],
                                     step=step_r, description='rows', readout=False,
                                     disabled=False, continuous_update=True,
                                     orientation='horizontal', slider_color='blue'),
                  last_column=IntSlider(min=min(cols, df.shape[1]),
                                        max=df.shape[1], step=step_c,
                                        description='columns', readout=False,
                                        disabled=False, continuous_update=True,
                                        orientation='horizontal', slider_color='blue')
                  )
        def _freeze_header(last_row, last_column):
            display(df.iloc[max(0, last_row - rows):last_row,
                    max(0, last_column - cols):last_column])


def gen_id_dated(gdf, ref_col='Ref', date_col=None, date_ref='No_date'):
    """
    Generate a Id-dated reference for a (geo)dataframe
    
    Parameters
    -----------

    gdf : pandas.(Geo)Dataframe
    ref_col : Reference column
    date_ref : Default data's date
    date_col: Column containing dates
    """
    print('Generation of ID-dated...')

    if 'Date' in gdf.columns and date_ref == 'No_date' and date_col is None:
        print("Using 'Date' column in the (geo)dataframe !")
        gdf[ref_col] = gdf['Date'].apply(lambda x: str(x.year) + '-' if not pd.isnull(x) else '') + gdf[ref_col].apply(
            lambda x: str(x) if not pd.isnull(x) else '')

        gdf['ID_date'] = gdf[date_col].apply(lambda x: str(x.year) + '-' if not pd.isnull(x) else '') + gdf[
            ref_col].apply(lambda x: str(x) if not pd.isnull(x) else '')
        first_column = gdf.pop('ID_date')
        gdf.insert(0, 'ID_date', first_column)
        print('Process ended, check the (geo)dataframe')

    elif date_ref != 'No_date':
        print("Using default date given !")
        gdf['ID_date'] = date_ref + '-' + gdf[ref_col].apply(lambda x: str(x) if not pd.isnull(x) else '')
        first_column = gdf.pop('ID_date')
        gdf.insert(0, 'ID_date', first_column)
        print('Process ended, check the (geo)dataframe')

    elif date_col is not None:
        print("Using column '", date_col, "' in the (geo)dataframe !")
        gdf['ID_date'] = gdf[date_col].apply(lambda x: str(x.year) + '-' if not pd.isnull(x) else '') + gdf[
            ref_col].apply(lambda x: str(x) if not pd.isnull(x) else '')
        first_column = gdf.pop('ID_date')
        gdf.insert(0, 'ID_date', first_column)
        print('Process ended, check the (geo)dataframe')

    else:
        print("No date given and no column 'Date' is the (geo)dataframe, Process cancelled !")

    # return gdf[refcol]


def gdf_geom(gdf):
    # geom = gpd.GeoSeries(gdf.apply(lambda x: Point(x['X'], x['Y']),1),crs={'init': 'epsg:31370'})
    # gdf = gpd.GeoDataFrame(gdf, geometry=geom, crs="EPSG:31370")

    gdf = gpd.GeoDataFrame(gdf, geometry=gpd.points_from_xy(gdf.X, gdf.Y, crs=str('EPSG:31370')))

    return gdf


def gdf_merger(gdf1, gdf2, how='outer', on=None, dist_max=None, date_col=None, drop_duplicates=False, verbose=False):
    """ Enhance data merging with automatic actions on dataframe after the merge

    Parameters
    ------------
    gdf1, gdf2 : pandas (Geo)DataFrame

    how: str
    on: str
    dist_max: float
    date_col: str
    drop_duplicates: bool
    verbose: bool

    Returns
    --------
    gdf: merged dataframe
    gdf_error: dataframe that contains ambiguous values encounter

    """

    distinct_objects_to_add = {}
    idx_distinct_obj = 0

    mdf = gdf1.merge(gdf2, how=how, on=on)
    mdf.reset_index(drop=True, inplace=True)
    mdf.replace('nan', np.nan, inplace=True)
    k = 0
    for idx in mdf.query(f'{on}!={on}').index:
        mdf.loc[idx, 'ID'] = f'?{k}'
        k += 1

    gdf = mdf.copy()
    gdf_conflict = pd.DataFrame()

    conflict_row = []
    conflict_col = []
    conflict_idx_col = {}  # to specify the type of the conflict (column) for each row in gdf_conflict
    conflict = False

    single_cols = list(set([re.sub("_x|_y", "", gdf.columns.to_list()[x]) for x in range(len(gdf.columns)) if not
                            re.compile(r"_x|_y").search(gdf.columns.to_list()[x])]))

    dble_cols = list(set([re.sub("_x|_y", "", gdf.columns.to_list()[x]) for x in range(len(gdf.columns)) if
                          re.compile(r"_x|_y").search(gdf.columns.to_list()[x])]))

    if 'X' not in dble_cols:
        dist_max = None  # avoid error due to dist_max definition without position data

    for col_i in dble_cols:
        gdf[col_i] = np.nan  # creation of the definitive column
        if verbose: print('\nColumn :', col_i)

    for idx in mdf.index:
        distinct_objects = True
        row_conf_cols = []  # conflictual columns for each row
        dist = 0

        # put this here to avoid to duplicate many lines below
        if 'X' in dble_cols:  # coordinates in both dataframes
            # compute distance between the points coming from each dataframe
            if not pd.isnull(mdf.loc[idx, 'X_x']) and not pd.isnull(mdf.loc[idx, 'X_y']):
                dist = (mdf.loc[idx, 'X_x'] - mdf.loc[idx, 'X_y']) ** 2 + (
                        mdf.loc[idx, 'Y_x'] - mdf.loc[idx, 'Y_y']) ** 2
            else:
                distinct_objects = False

        if dist_max is None or date_col is None:
            distinct_objects = False

        elif date_col is not None and date_col in dble_cols:  # compare temporal data
            if not pd.isnull(mdf.loc[idx, date_col+'_x']) and not pd.isnull(mdf.loc[idx, date_col+'_y']):
                if mdf.loc[idx, date_col+'_x'] == mdf.loc[idx, date_col+'_y']:
                    distinct_objects = False
                    # if dates are the same, but coordinates are different
                    if dist <= dist_max ** 2:  # considered as same object
                        distinct_objects = False
            else:
                distinct_objects = False

        elif dist_max is not None and 'X' in dble_cols:
            if dist <= dist_max ** 2:  # considered as same object
                distinct_objects = False

        if verbose: print(idx, 'distinct: ', distinct_objects)
        # If objects are not distinct -> compare them and merge values or generate conflict
        # else add a new row in gdf to store two distinct object
        if not distinct_objects:  # comparison and merging
            for col_i in dble_cols:
                # print(idx, col_i)
                # if repeated column i contains nan in gdf1 and a value in gdf2 -> keep value in gdf2
                if pd.isnull(mdf.loc[idx, col_i + '_x']) and not pd.isnull(mdf.loc[idx, col_i + '_y']):
                    gdf.loc[idx, col_i] = mdf.loc[idx, col_i + '_y']
                    gdf.loc[idx, col_i + '_y'] = np.nan
                    if verbose: print('1A')
                # if repeated column i contains nan in gdf2 and a value in gdf1 -> keep value in gdf1
                elif pd.isnull(mdf.loc[idx, col_i + '_y']) and not pd.isnull(mdf.loc[idx, col_i + '_x']):
                    gdf.loc[idx, col_i] = mdf.loc[idx, col_i + '_x']
                    gdf.loc[idx, col_i + '_x'] = np.nan
                    if verbose: print('1B')
                # if repeated columns contain the same value -> keep value in gdf1
                elif mdf.loc[idx, col_i + '_x'] == mdf.loc[idx, col_i + '_y']:
                    gdf.loc[idx, col_i] = mdf.loc[idx, col_i + '_x']
                    gdf.loc[idx, col_i + '_x'] = np.nan
                    gdf.loc[idx, col_i + '_y'] = np.nan
                    if verbose: print('1C')
                # if both repeated columns contain nan -> put nan in gdf
                elif pd.isnull(mdf.loc[idx, col_i + '_x']) and pd.isnull(mdf.loc[idx, col_i + '_y']):
                    gdf.loc[idx, col_i] = np.nan
                    if verbose: print('1D')
                # if repeated columns contain different values -> handle following dtype
                else:
                    # always keep one single object position values because not distinct objects
                    if col_i == 'X' or col_i == 'Y' or col_i == 'Z':
                        gdf.loc[idx, col_i] = mdf.loc[idx, col_i + '_x']
                        gdf.loc[idx, col_i + '_x'] = np.nan
                        gdf.loc[idx, col_i + '_y'] = np.nan

                    # if the values are not numeric -> cast to string and compare lowercase;
                    # if same -> Capitalize and put in gdf
                    elif pd.api.types.infer_dtype(mdf[col_i + '_x']) != 'floating' or \
                            pd.api.types.infer_dtype(mdf[col_i + '_y']) != 'floating':
                        if str(mdf.loc[idx, col_i + '_x']).lower() == str(mdf.loc[idx, col_i + '_y']).lower():
                            gdf.loc[idx, col_i] = str(mdf.loc[idx, col_i + '_x']).capitalize()
                            gdf.loc[idx, col_i + '_x'] = np.nan
                            gdf.loc[idx, col_i + '_y'] = np.nan
                            if verbose: print('1E')
                        elif str(mdf.loc[idx, col_i + '_x']).lower() == '' or str(mdf.loc[idx, col_i + '_x']).lower() == 'nan':
                            gdf.loc[idx, col_i] = str(mdf.loc[idx, col_i + '_y']).capitalize()
                            gdf.loc[idx, col_i + '_x'] = np.nan
                            gdf.loc[idx, col_i + '_y'] = np.nan
                            if verbose: print('1F')
                        elif str(mdf.loc[idx, col_i + '_y']).lower() == '' or str(mdf.loc[idx, col_i + '_y']).lower() == 'nan':
                            gdf.loc[idx, col_i] = str(mdf.loc[idx, col_i + '_x']).capitalize()
                            gdf.loc[idx, col_i + '_x'] = np.nan
                            gdf.loc[idx, col_i + '_y'] = np.nan
                            if verbose: print('1G')
                        else:
                            # TODO : Implemented  a test to check whether the values are equivalent (close enough)
                            gdf.loc[idx, col_i] = '#conflict'
                            if col_i + '_x' not in conflict_col:
                                conflict_col = conflict_col + [col_i + '_x', col_i + '_y']
                            if idx not in conflict_row:
                                conflict_row = conflict_row + [idx]
                            conflict = True
                            row_conf_cols.append(col_i)
                            update_dict(conflict_idx_col, {idx: row_conf_cols})

                    # if the values are not considered as the same -> stage to put in gdf_conflict
                    else:
                        if verbose: print('1H')
                        gdf.loc[idx, col_i] = np.nan
                        if col_i + '_x' not in conflict_col:
                            conflict_col = conflict_col + [col_i + '_x', col_i + '_y']
                        if idx not in conflict_row:
                            conflict_row = conflict_row + [idx]
                        conflict = True
                        row_conf_cols.append(col_i)
                        update_dict(conflict_idx_col, {idx: row_conf_cols})
        else:
            if verbose: print('2A')
            distinct_objects_to_add.update({idx_distinct_obj: {i: mdf.loc[idx, i] for i in single_cols}})
            distinct_objects_to_add[idx_distinct_obj][on] = '_' + str(distinct_objects_to_add[idx_distinct_obj][on]) + '_'
            update_dict(distinct_objects_to_add, {idx_distinct_obj: {i: mdf.loc[idx, i+'_x'] for i in dble_cols}})
            idx_distinct_obj += 1
            distinct_objects_to_add.update({idx_distinct_obj: {i: mdf.loc[idx, i] for i in single_cols}})
            update_dict(distinct_objects_to_add, {idx_distinct_obj: {i: mdf.loc[idx, i + '_y'] for i in dble_cols}})
            idx_distinct_obj += 1
            gdf.drop(idx, axis='index', inplace=True)  # drop original line used to create 2 distinct objects

    distinct_objects_df = pd.DataFrame.from_dict(distinct_objects_to_add, orient='index')
    gdf['split_distinct'] = False
    distinct_objects_df['split_distinct'] = True
    gdf = pd.concat([gdf, distinct_objects_df], ignore_index=False)
    gdf = gdf[single_cols + dble_cols + ['split_distinct']]
    gdf.reset_index(drop=False, inplace=True)
    gdf.loc[gdf['split_distinct'] == True, 'index'] = np.nan
    gdf.drop('split_distinct', axis='columns', inplace=True)

    gdf.insert(0, on, gdf.pop(on))
    if date_col is not None and date_col in gdf.columns:
        col_pos = 1
        gdf.insert(col_pos, date_col, gdf.pop(date_col))
    else:
        col_pos = 0
    if 'X' in gdf.columns: gdf.insert(col_pos+1, 'X', gdf.pop('X'))
    if 'Y' in gdf.columns: gdf.insert(col_pos+2, 'Y', gdf.pop('Y'))
    if 'Z' in gdf.columns: gdf.insert(col_pos+3, 'Z', gdf.pop('Z'))

    if conflict:
        gdf_conflict = mdf.loc[conflict_row, [on] + conflict_col]
        for r, c in conflict_idx_col.items():
            gdf_conflict.loc[r, 'Check_col'] = str(c).strip('"[]').replace("'", "")
        gdf_conflict.insert(0, 'Check_col', gdf_conflict.pop('Check_col'))
        print('Conflict values present. Please resolve this manually !')
    else:
        gdf.drop(['index'], axis='columns', inplace=True)

    if drop_duplicates:
        idx_to_drop = []
        gdf.drop_duplicates(subset=[c for c in gdf.columns if c != 'index'], inplace=True)
        if 'index' in gdf.columns and conflict:
            old_idx = gdf['index']
            idx_to_drop = [i for i in gdf_conflict.index if i not in old_idx]
        if len(idx_to_drop) > 0:
            gdf_conflict.drop(index=idx_to_drop, inplace=True)
        gdf.reset_index(drop=True, inplace=True)

    return gdf, gdf_conflict


def data_validation(overall_data, conflict_data, valid_dict, index_col='index', verbose=False):
    """
    Validate correct data in a conflictual dataframe after merging

    Parameters:
    -------------
    overall_data : Pandas.DataFrame
        Dataframe where the conflict must be fixed
    conflict_data : Pandas.DataFrame
        Dataframe that contains the conflictual values
    valid_dict : dict
        Dictionary of columns and (list of) index(es) that specify which values are correct in the conflict_data

    """
    # TODO : possibility to add a new line when suppose no real conflict (confirm with yes or no)
    for valid_col, idx in valid_dict.items():
        col = re.sub("_x|_y", "", valid_col)
        q = list(overall_data.query(f'{index_col}=={idx}').index)
        if verbose:
            print(q, idx, '---', overall_data.loc[q, col], conflict_data.loc[idx, valid_col])
        overall_data.loc[q, col] = conflict_data.loc[idx, valid_col]
        conflict_data.loc[idx, [col+'_x', col+'_y']] = 'Done'

    for i, r in conflict_data.iterrows():
        if sum(x == 'Done' for x in r) == 2 * len(conflict_data.loc[i, 'Check_col'].split(',')):
            conflict_data.drop(index=i, inplace=True)

    if len(conflict_data) == 0:
        overall_data.drop(columns=index_col, inplace=True)
        print("all conflicts have been fixed!")
    else:
        print(f"Validation done, but conflicts remain!")


def na_col_drop(data, col_non_na=10, drop=True, verbose=False):
    """
    Delete columns in the dataframe where the count of non-NaN values is lower than col_non_na

    """

    drop_cols = []
    if verbose: print('Non-NaN values\n----------------')
    for c in data.columns:
        if verbose: print(f'{c} --> val: {data[c].notnull().sum()} | Nan: {data[c].isnull().sum()}')
        if data[c].notnull().sum() < col_non_na:
            drop_cols.append(c)

    if drop and len(drop_cols) != 0:
        print(f'\nColumns dropped :{drop_cols}\n')
        data.drop(drop_cols, axis=1, inplace=True)

    return data


def fix_duplicates(df1, df2, id_col='ID', x_gap=.8, y_gap=.8, drop_old_id=True):
    """ find nearest object by position and set same ID (to treat same position but different names cases)
    x_gap : float
        gap between X coordinates of an object in df1 and df2
    y_gap : float
        gap between Y coordinates of an object in df1 and df2
    """

    if len(df1) < len(df2):  # loop on the smallest dataframe to avoid over-looping
        data1 = df1
        data2 = df2
    else:
        data1 = df2
        data2 = df1

    # retrieve IDs before changing them
    data1[f'new_{id_col}'] = data1[id_col]
    data2[f'new_{id_col}'] = data2[id_col]

    if 'X' not in data1.columns or 'X' not in data2.columns:
        raise (KeyError('No coordinates (X,Y) found in one of the dataframes !'))

    cnt = 0  # counter
    for idx in data1.index:
        x, y = data1.loc[idx, 'X'], data1.loc[idx, 'Y']
        q = list(data2.query(f"X <= {x + x_gap} and X >= {x} and Y <= {y + y_gap} and Y >= {y}").index)

        cnt += len(q)
        if len(q) != 0:
            # same object, keep one ID
            data1.loc[idx, f'new_{id_col}'] = data1.loc[idx, id_col]
            data2.loc[q, f'new_{id_col}'] = data1.loc[idx, id_col]
        else:
            # distinct object, keep original ID
            data1.loc[idx, f'new_{id_col}'] = data1.loc[idx, id_col]
            data2.loc[q, f'new_{id_col}'] = data2.loc[idx, id_col]

    print(f"{cnt} duplicate objects fixed!")
    data1.rename(columns={id_col: f'Old_{id_col}', f'new_{id_col}': id_col}, inplace=True)
    data2.rename(columns={id_col: f'Old_{id_col}', f'new_{id_col}': id_col}, inplace=True)
    data1.insert(0, id_col, data1.pop(id_col))
    data2.insert(0, id_col, data2.pop(id_col))

    if drop_old_id:
        data1.drop(columns=f'Old_{id_col}', inplace=True)
        data2.drop(columns=f'Old_{id_col}', inplace=True)


def gdf_filter(data, position=True, id_col='ID', expression=None, regex=None, bypass_col=['Old_ID', 'exp_ID'],
               dist_max=1, val_max=1.5, drop=False, drop_old_id=True, verbose=False):
    """
    filter duplicates from a dataframe, considering ID, position, and/or an expression)
    expression: str
        expression (words) to strip from a string and regularize it
    """

    drop_idx = []
    check_idx = []
    check_dict = {}
    id_list = []
    cols = data.columns.to_list()
    reg = None

    # remove some words in expression or based on regex from each id_col values
    if expression is not None:
        if len(expression.split('|')) > 2:
            raise(ValueError("Expression can contains only one '|' (2 different words)"))  # can be improve after
        e = expression.split('|')
        reg = ".*\d+(?P<A>.*" + f'{e[0]}' + ".*)|.*\d+(?P<B>.*" + f'{e[1]}' + ".*)"
    elif regex is not None:
        reg = regex

    if reg is not None:
        data[f'new_{id_col}'] = data[id_col]  # copy all values before modifying
        for idx, row in data.iterrows():
            r = re.search(reg, row[id_col], re.I)
            if r:
                groupA = r.group('A')
                groupB = r.group('B')
                if groupA is not None:
                    sub = f"{groupA.lower()}"
                elif groupB is not None:
                    sub = f"{groupB.lower()}"
                else:
                    sub = ''
                data.loc[idx, f'new_{id_col}'] = re.sub(sub, '', row[id_col].lower(), re.I).upper().replace(' ', '')
        data.rename(columns={f'{id_col}': 'exp_ID', f'new_{id_col}': 'ID'}, inplace=True)

    # filtering
    for i in data.index:
        uid = data.loc[i, id_col]
        tmp = data[data[id_col] == f"{uid}"]

        if position:  # use position XY
            pos_1 = [data.loc[i, 'X'], data.loc[i, 'Y']]
            if uid not in id_list and len(tmp) >= 2:
                id_list.append(uid)
                for j in tmp.index:  # retrieve duplicates ID index
                    if j != i:
                        pos_2 = [data.loc[j, 'X'], data.loc[j, 'Y']]
                        distinct = not ((pos_1[0] - pos_2[0]) ** 2 + (pos_1[1] - pos_2[1]) ** 2 <= dist_max ** 2)
                        if not distinct:
                            bypass_col += ['X', 'Y', 'ID']
                            if j not in drop_idx:
                                for c in range(len(data.columns)-1):
                                    if cols[c] not in bypass_col:
                                        if data.iloc[i, c] == data.iloc[j, c]:  # all values (str, numeric) are equals
                                            same = True
                                        elif data.iloc[i, c] != data.iloc[j, c] and \
                                                re.search('int|float', data[cols[c]].dtype.name):
                                            val = abs(data.iloc[i, c] - data.iloc[j, c]) / abs(np.nanmedian(data.iloc[:, c]))
                                            if val <= val_max:
                                                same = True
                                            else:
                                                same = False
                                                if cols[c] in check_dict.keys():
                                                    idxs = check_dict[cols[c]] + [j]
                                                else:
                                                    idxs = [j]
                                                update_dict(check_dict, {cols[c]: idxs})
                                                if j not in check_idx: check_idx.append(j)
                                        else:  # str values
                                            same = False
                                            if cols[c] in check_dict.keys():
                                                idxs = check_dict[cols[c]] + [j]
                                            else:
                                                idxs = [j]
                                            update_dict(check_dict, {cols[c]: idxs})
                                            if j not in check_idx: check_idx.append(j)
                                if same: drop_idx.append(j)  # same objet -> most be dropped

        else:  # without position XY, use ID
            if uid not in id_list and len(tmp) >= 2:
                id_list.append(uid)
                for j in tmp.index:
                    if j != i:
                        bypass_col += ['X', 'Y', 'ID']
                        if j not in drop_idx:
                            for c in range(len(data.columns)-1):
                                if cols[c] not in bypass_col:
                                    if data.iloc[i, c] == data.iloc[j, c]:
                                        same = True
                                    elif data.iloc[i, c] != data.iloc[j, c] and re.search('int|float', data[cols[c]].dtype.name):
                                        #val = max(data.iloc[i, c], data.iloc[j, c]) / min(data.iloc[i, c], data.iloc[j, c])
                                        val = abs(data.iloc[i, c] - data.iloc[j, c]) / abs(np.nanmedian(data.iloc[:, c]))
                                        if val <= val_max:
                                            same = True
                                        else:
                                            same = False
                                            if cols[c] in check_dict.keys():
                                                idxs = check_dict[cols[c]] + [j]
                                            else:
                                                idxs = [j]
                                            update_dict(check_dict, {cols[c]: idxs})
                                            if j not in check_idx: check_idx.append(j)
                                    else:
                                        same = False
                                        if cols[c] in check_dict.keys():
                                            idxs = check_dict[cols[c]] + [j]
                                        else:
                                            idxs = [j]
                                        update_dict(check_dict, {cols[c]: idxs})
                                        if j not in check_idx: check_idx.append(j)
                            if same:
                                drop_idx.append(j)  # same objet -> most be dropped

    check_data = data.loc[check_idx, list(check_dict.keys())]
    if len(check_data) > 0:
        pass
        #print(f"some data must be checked , look at indices : {check_dict.values()}\n")

    if len(drop_idx) > 0:
        print(f"same objects at indices:{drop_idx}, will be dropped if drop is set True!")

    data.rename(columns={'ID': 'Old_ID'}, inplace=True)
    data.insert(0, 'ID', data['Old_ID'].apply(lambda x: re.sub(f"{expression}|' '", "", str(x))))

    if drop:
        data.drop(index=drop_idx, inplace=True)
        data.reset_index(drop=True, inplace=True)
    if drop_old_id:
        data.drop(columns='Old_ID', inplace=True)

    print(f"Rows : {data.shape[0]} ; Columns : {data.shape[1]} ; Unique on '{id_col}' : {len(set(data[id_col]))} ; ")

    return data, check_data


def na_line_drop(data, col_n=3, line_non_na=0, drop_by_position=False, old_idx=False, verbose=False):
    """
    Delete rows in the dataframe where the count of non-NaN values is lower than rows_non_na

    """

    l1 = len(data)
    no_pos = []
    data['line_na'] = False

    # drop if no position coordinates
    if drop_by_position and 'X' in data.columns:
        no_pos = data.query('X.isnull() and Y.isnull()').index
        data.drop(index=no_pos, inplace=True)
        print(f"{len(no_pos)} without position -> lines dropped !")

    for i in range(len(data)): # data.index:
        if verbose : print(i)

        if line_non_na >= data.iloc[i, col_n:-1].notnull().sum():
            data.loc[i, 'line_na'] = True

    data = data.query('line_na==False')
    data.reset_index(drop=(not old_idx), inplace=True)
    data.drop(columns='line_na', inplace=True)
    l2 = len(data)
    nb_lines = l1 - l2
    if nb_lines > 0 and nb_lines != len(no_pos): print(f'{nb_lines} NaN lines dropped')

    return data


def dble_col_drop(data, drop=True):
    twins = {}
    idx_drop = {}
    for i in range(len(data.columns)):  # locate double columns
        c = data.columns[i]
        if c not in twins.keys():
            twins.update({c: i})
        # elif data.iloc[:,i].isnull().sum()<data.iloc[:,twins[c]].isnull().sum():
        #    idx_drop.update({twins[c]:i})
        #    twins.update({c:i})
        else:
            idx_drop.update({i: c})

    for i in range(len(data.columns)):  # attempt to collect data if exist in double columns
        for k, v in idx_drop.items():
            if data.columns[i] == v:
                for j in data.index:
                    if pd.isnull(data.iloc[j, i]):
                        data.iloc[j, i] = data.iloc[j, k]
                    elif not isinstance(data.iloc[j, i], str) and not isinstance(data.iloc[j, k], str):
                        data.iloc[j, i] = max(data.iloc[j, i], data.iloc[j, k])

    print(f"column(s) dropped: {[f'{x}:{y}' for x, y in idx_drop.items()]}")
    new_col = list(set(range(len(data.columns))) - set(idx_drop.keys()))
    if drop: data = data.iloc[:, new_col]

    return data


def col_ren(data, line_to_col=1, mode=0, name=[]):
    """
    mode: int
        set 0 to rename columns with a line, set 1 if provide name list or dict
    """
    new_name = {}

    if mode != 0 and mode != 1:
        print("Error! Parameter \'Mode\' must be 0 or 1 (if 1, colums length must be equal to name length)")

    elif mode == 0:
        for i in data.columns:
            col = str(data.iloc[line_to_col, i])
            if re.search('nan', col, flags=re.IGNORECASE):
                new_name.update({i: f'col_{i}'})
            else:
                new_name.update({i: col})

        data.drop([line_to_col], axis=0, inplace=True)
        data.reset_index(drop=True, inplace=True)

    elif mode == 1:
        if isinstance(name, list) and len(name) == len(data.columns):
            for i in range(len(name)):
                new_name.update({data.columns[i]: name[i]})

        elif isinstance(name, dict):
            strp = ',| |>|<|-|\n|_|\(|\.|\)'

            for i in range(len(data.columns)):
                keys = list(name.keys())
                old = data.columns[i]

                for k in keys:
                    if re.match(f"{re.sub(strp, '', k)}", re.sub(strp, '', old), flags=re.I):
                        new_name.update({old: name[k]})

        elif isinstance(name, list) and len(name) != len(data.columns):
            #print('Error! names list length and columns length are not the same.')
            raise(TypeError('Error! names list length and columns length are not the same.'))

    data.rename(columns=new_name, inplace=True)

    return data


def compute_BH_length(df, length_col_name='Profondeur', top_col='Litho_top', base_col='Litho_base', verbose=False):
    """

    """
    for i in df.index:
        try:
            float(df.loc[i, top_col])
        except ValueError:
            df.loc[i, top_col] = np.nan

        try:
            float(df.loc[i, base_col])
        except ValueError:
            df.loc[i, base_col] = np.nan

    df[top_col] = df[top_col].astype('float64')
    df[base_col] = df[base_col].astype('float64')

    # compute length based on litho_top and litho_base
    id_list = []

    for i in df.index:
        id_ = df.loc[i, 'ID']

        if verbose: print(i, id_, df.loc[i, top_col], df.loc[i, base_col])
        if id_ not in id_list:
            id_list.append(id_)
            if isinstance(id_, str):
                sql_id = f"{id_}"
            elif isinstance(id_, float) or isinstance(id_, int):
                sql_id = id_

            tmp = df[df['ID'] == sql_id]

            if verbose: print(len(tmp))
            # if len(tmp) > 0:
            df.loc[tmp.index, length_col_name] = float(max(tmp[base_col])) - float(min(tmp[top_col]))

    df.drop(index=df.query(f'{base_col}.isnull() and {top_col}.isnull()').index, inplace=True)
    df.insert(df.columns.to_list().index('ID') + 1, length_col_name, df.pop(length_col_name))
    # df.reset_index(drop=True, inplace=True)

