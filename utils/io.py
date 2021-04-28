import re
from os import walk
import numpy as np
import geopandas as gpd
import pandas as pd
from docutils.nodes import error
from shapely import wkt
from shapely.geometry import Point
from striplog import Striplog, Lexicon, Interval, Component
from core.orm import BoreholeOrm, PositionOrm
from ipywidgets import interact, IntSlider
from IPython.display import display
from utils.config import DEFAULT_BOREHOLE_LENGTH, DEFAULT_BOREHOLE_DIAMETER, DEFAULT_LITHOLOGY


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

        a += 1  # files used counter
        print(f'--> {fl.strip(search_dir)}: ({len(df)} lines)')
        files_interest.append(fl)

        if 'ID' in df.columns:
            df['ID'] = df['ID'].astype(str)
        if 'X' in df_all.columns:
            df['X'] = df['X'].apply(lambda x: x if isinstance(x, float) else float(x.replace(',', '.')))
            df['Y'] = df['Y'].apply(lambda x: x if isinstance(x, float) else float(x.replace(',', '.')))
            df['Z'] = df['Z'].apply(lambda x: x if isinstance(x, float) else float(x.replace(',', '.')))
        df_all = df_all.append(df[header])
        df_all.reset_index(inplace=True, drop=True)
        # df_all.fillna('', inplace=True)

    if 'X' in df_all.columns:
        df_all = gpd.GeoDataFrame(df_all, geometry=gpd.points_from_xy(df_all.X, df_all.Y, crs=str('EPSG:31370')))

    print(f'\nThe overall dataframe contains {len(df_all)} lines. {a} files used')
    return df_all


"""
def files_read(fdir, crit_col, columns=None, verbose=False):

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
    """


def striplog_from_df(df, bh_name=None, litho_col=None, litho_top=None, litho_base=None,
                     length_col=None, lexicon=None, use_default=True, verbose=False,
                     query=True):
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
    
    length_col : str
        dataframe column that contains lithology thickness (default:None)
        
    lexicon : dict
        A vocabulary for parsing lithological or stratigraphic descriptions
        (set to Lexicon.default() if lexicon is None)
              
    Returns
    -------
    strip : dict of striplog objects
    
    """
    strip = {}
    if lexicon is None:
        lexicon = Lexicon.default()

    if litho_col is None or litho_col in list(df.columns):
        bh_list = []

        for i in range(0, len(df)):
            if bh_name is not None and bh_name in df.columns:
                bh_id = bh_name
            else:
                bh_id = df.loc[i, 'ID']

            if bh_id not in bh_list:
                bh_list.append(bh_id)
                if query:
                    sql = df['ID'] == f"{bh_id}"  # f'ID=="{bh_id}"'
                    tmp = df[sql].copy()  # df.query(sql).copy()  # divide and work fast ;)
                    tmp.reset_index(drop=True, inplace=True)
                else:
                    tmp = df

                intervals = []

                for j in range(0, len(tmp)):
                    # lithology processing
                    litho = ''
                    if litho_col is None:
                        litho = DEFAULT_LITHOLOGY
                    elif litho_col in list(tmp.columns):
                        litho = tmp.loc[j, litho_col]

                    # create components from lithological description
                    component = [Component.from_text(litho, lexicon)]
                    # print(component)

                    # length processing
                    if length_col is not None and length_col in list(tmp.columns) \
                            and not pd.isnull(tmp.loc[j, length_col]):
                        length = tmp.loc[j, length_col]
                        if verbose:
                            print(f'length={length:.2f}')
                    else:
                        if use_default:
                            if verbose:
                                print(f'|__ID:\'{bh_id}\' -- No length provided, treated with default '
                                      f'(length={DEFAULT_BOREHOLE_LENGTH})')
                            length = DEFAULT_BOREHOLE_LENGTH
                        else:
                            length = 0.

                    # intervals processing
                    if litho_top is not None and litho_top in list(tmp.columns):
                        top = tmp.loc[j, litho_top]
                    else:
                        top = 0.

                    if litho_base is not None and litho_base in list(tmp.columns):
                        base = tmp.loc[j, litho_base]
                    else:
                        base = length

                    if base != 0.:
                        intervals = intervals + [
                            Interval(top=top, base=base, description=litho, components=component, lexicon=lexicon)]

                    # print(intervals)

                if len(intervals) != 0:
                    if verbose:
                        print(f'|__ID:\'{bh_id}\' -- No lithology data, treated with default (\'{DEFAULT_LITHOLOGY}\')')
                    strip.update({bh_id: Striplog(list_of_Intervals=intervals)})
                    # print(strip[bh_id])

                else:
                    print(f"|__ID:\'{bh_id}\' -- Cannot create a striplog, no interval (length or base = 0)")

        print(strip)

    elif litho_col is not None and litho_col not in list(df.columns):
        print("Error! The dataframe's columns don't match for striplog creation !")
        strip = {}

    return strip


def striplog_from_text(filename, lexicon=None):
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

    if lexicon is None:
        lexicon = Lexicon.default()

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
                         diam_field='Diameter', length_field='Length',
                         litho_field=None, litho_top=None, litho_base=None,
                         lexicon=None, verbose=False, use_default=True):
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

    int_id = 0
    bh_id = 0
    pos_id = 0
    boreholes = []
    components = []
    comp_id = 0
    component_dict = {}
    link_dict = {}
    df = 0

    if x is None:
        x = [0., 20., 5, 10]
    else:
        x = x

    if y is None:
        y = [0., 40., 50, 2]
    else:
        y = y

    if boreholes_dict is None:
        print("Error! Borehole dictionary not given.")

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

                    for i in interval.components:
                        if i != Component({}):
                            link_dict.update({(int_id, component_dict[i]): {'extra_data': ''}})

                    interval_number += 1
                    int_id += 1
                    pos_id += 2

                if verbose:
                    print(f'{d}\n')

                boreholes[bh_id].intervals_values = d
                bh_id += 1
            components = {v: k for k, v in component_dict.items()}

        else:
            # pos = bh_id
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

                    for i in interval.components:
                        if i != Component({}):
                            link_dict.update({(int_id, component_dict[i]): {'extra_data': ''}})

                    interval_number += 1
                    int_id += 1
                    pos_id += 2

                if verbose:
                    print(f'{d}\n')

                boreholes[bh_id].intervals_values = d
                bh_id += 1
            components = {v: k for k, v in component_dict.items()}

    # ----------------------------dfs------------------------------------#

    elif isinstance(boreholes_dict, list):
        if len(boreholes_dict) == 0:
            print("Error ! Cannot create boreholes with empty list or dict")

        while (boreholes_dict is not None) and df < len(boreholes_dict):
            print(f'\nDataframe {df} processing...\n================================')
            id_list = []
            dict_bh = 0

            x = boreholes_dict[df].X
            y = boreholes_dict[df].Y

            if diam_field in boreholes_dict[df].columns:
                diam = boreholes_dict[df][diam_field]
            else:
                if verbose:
                    print(f'|__ID:\'{bh_id}\' -- No borehole diameter provided,'
                          f' treated with default (diameter={DEFAULT_BOREHOLE_DIAMETER})')
                diam = pd.Series([DEFAULT_BOREHOLE_DIAMETER] * len(boreholes_dict[df]))

            if length_field in boreholes_dict[df].columns:
                length = boreholes_dict[df][length_field]
            else:
                length = pd.Series([DEFAULT_BOREHOLE_LENGTH] * len(boreholes_dict[df]))


            for i, j in boreholes_dict[df].iterrows():
                id_ = j['ID']

                if id_ not in id_list:
                    id_list.append(id_)
                    boreholes.append(BoreholeOrm(id=id_))
                    interval_number = 0

                    sql = boreholes_dict[df]['ID'] == f"{id_}"
                    tmp = boreholes_dict[df][sql].copy()
                    #sql = f'ID=="{id_}"'
                    #tmp = boreholes_dict[df].query(sql).copy()
                    tmp.reset_index(drop=True, inplace=True)
                    strip = striplog_from_df(df=tmp, bh_name=id_,litho_col=litho_field,
                                             litho_top=litho_top, litho_base=litho_base,
                                             length_col=length_field,
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
                            # print(interval)
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

                            for i in interval.components:
                                if i != Component({}):
                                    link_dict.update({(int_id, component_dict[i]): {'extra_data': ''}})

                            interval_number += 1
                            int_id += 1
                            pos_id += 2

                        if verbose:
                            print(f'{d}\n')
                        if dict_bh < len(boreholes):
                            boreholes[dict_bh].intervals_values = d
                            boreholes[dict_bh].length = length[dict_bh]
                            if diam[dict_bh] is not None and not pd.isnull(diam[dict_bh]):
                                boreholes[dict_bh].diameter = diam[dict_bh]
                            else:
                                boreholes[dict_bh].diameter = DEFAULT_BOREHOLE_DIAMETER

                        dict_bh += 1

                else:
                    if verbose:
                        print(f"|__ID '{id_}' already treated, skip")

                components = {v: k for k, v in component_dict.items()}

            print(f"\nEnd of the process : {len(id_list)} unique ID found")
            df += 1

    elif not isinstance(boreholes_dict, dict) or isinstance(boreholes_dict, list):
        print('Error! Only take a dict or a dataframe to work !')

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
        print(f"Rows : {df.shape[0]}, columns : {df.shape[1]}, Unique on '{un_val}': {len(set(df[un_val]))}")

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
        # Id=[]
        # for Idx, row in gdf.iterrows():
        # if not pd.isnull(row['Date'].year):
        #     Id.append(str(row['Date'].year)+'-'+str(row[refcol]))
        #  else:
        #       Id.append(row[refcol])

        # gdf[refcol]=Id

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


def gdf_merger(gdf1, gdf2, how='outer', col=None, left_on=None, right_on=None, fcol=None, dist_max=None, err_val=None, non_na=5, col_n=None, scope=globals(), verbose=False, debug=False):
    """ Enhance data merging with automatic actions on dataframe after the merge

    Parameters
    ------------
    gdf1, gdf2 : pandas (Geo)DataFrame

    how: str
    col: str
    left_on: str
    right_on: str
    fcol: str
        name of the column to use as first column in the returned gdf dataframe

    Returns
    --------
    gdf: merged dataframe
    gdf_error: dataframe that contains ambiguous values encounter

    """
    gdf = pd.DataFrame()
    gdf_conflict = pd.DataFrame()

    def var_name(obj, scope=scope):
        if scope is None:
            scope = globals()
        varname = ''
        for name in scope:
            if scope[name] is obj:
                varname = name
                break

        return varname

    def process():  # err_val=err_val):
        gdf_conflict = pd.DataFrame()
        mdf = gdf1.merge(gdf2, how=how, left_on=left, right_on=right)
        mdf.replace('nan', np.nan, inplace=True)
        gdf = mdf.copy()  # to retrieve values for gdf_error

        error = False
        global error_row
        global error_col
        error_col = []
        error_row = []
        dist = 0.

        dble_cols = set([re.sub("_x|_y", "", gdf.columns.to_list()[x]) for x in range(len(gdf.columns)) if
                         re.compile(r"_x|_y").search(gdf.columns.to_list()[x])])

        for i in dble_cols:
            gdf[i] = np.nan # creation of the final column
            if verbose:
                print('\nColumn :', i)

            if debug:
                print('column:', gdf[i + '_x'].name)

            for j in gdf.index:
                distinct_objects = True
                if dist_max is None:
                    distinct_objects = False
                elif 'X' in dble_cols:  # coordinates in both dataframes
                    # compute distance between the points coming from each dataframe
                    pos_x = Point(mdf.loc[j, 'X_x'], mdf.loc[j, 'Y_x'])
                    pos_y = Point(mdf.loc[j, 'X_y'], mdf.loc[j, 'Y_y'])
                    dist = pos_x.distance(pos_y)
                    if dist <= dist_max:  # consider as same object
                        distinct_objects = False

                # If objects are distinct -> compare them and merge values or generate error
                # Else add a new row in gdf to store two distinct object
                if not distinct_objects:  # comparison and merging
                    # if repeated column i contains nan in gdf1 and a value in gdf2 -> keep value in gdf2
                    if pd.isnull(mdf.loc[j, i + '_x']) and not pd.isnull(mdf.loc[j, i + '_y']):
                        gdf.loc[j, i] = mdf.loc[j, i + '_y']
                        gdf.loc[j, i + '_y'] = np.nan
                        if verbose: print('1A')
                    # if repeated column i contains nan in gdf2 and a value in gdf1 -> keep value in gdf1
                    elif pd.isnull(mdf.loc[j, i + '_y']) and not pd.isnull(mdf.loc[j, i + '_x']):
                        gdf.loc[j, i] = mdf.loc[j, i + '_x']
                        gdf.loc[j, i + '_x'] = np.nan
                        if verbose: print('1B')
                    # if repeated columns contain the same value -> keep value in gdf1
                    elif mdf.loc[j, i + '_x'] == mdf.loc[j, i + '_y']:
                        gdf.loc[j, i] = mdf.loc[j, i + '_x']
                        gdf.loc[j, i + '_x'] = np.nan
                        gdf.loc[j, i + '_y'] = np.nan
                        if verbose: print('1C')
                    # if both repeated columns contain nan -> put nan in gdf
                    elif pd.isnull(mdf.loc[j, i + '_x']) and pd.isnull(mdf.loc[j, i + '_y']):
                        gdf.loc[j, i] = np.nan
                        if verbose: print('1D')
                    # if repeated columns contain different values -> handle following dtype
                    else:
                        # if the values are not numeric -> cast to string and compare lowercase; if same -> Capitalize and put in gdf
                        if not re.search('int|float', mdf[i + '_x'].dtype.name) and \
                                str(mdf.loc[j, i + '_x']).lower() == str(mdf.loc[j, i + '_y']).lower():
                            gdf.loc[j, i] = str(mdf.loc[j, i + '_x']).capitalize()
                            gdf.loc[j, i + '_y'] = np.nan
                            if verbose: print('1E')
                        # if the values are numeric or values are not numeric but not considered as the same -> stage to put in gdf_error
                        else:
                            if verbose: print('1F')
                            if i + '_x' not in error_col:
                                error_col = error_col + [i + '_x', i + '_y']
                            if j not in error_row:
                                error_row = error_row + [j]
                            error = True
                else:
                    # distinct_objects_to_add.update({j:{i:gdf.loc[j, i + '_y']}})
                    pass

        if fcol is not None:
            gdf.insert(0, fcol, gdf.pop(fcol))

        if fcol is not None:
            idx_col = gdf.columns.to_list().index(fcol)
        elif col is not None:
            idx_col = gdf.columns.to_list().index(col)
        else:
            idx_col = gdf.columns.to_list().index('ID')

        gdf.insert(0, col, gdf.pop(col))
        if 'X' in gdf.columns:
            gdf.insert(idx_col + 1, 'X', gdf.pop('X'))
        if 'Y' in gdf.columns:
            gdf.insert(idx_col + 2, 'Y', gdf.pop('Y'))
        if 'Z' in gdf.columns:
            gdf.insert(idx_col + 3, 'Z', gdf.pop('Z'))
        if 'Zsol' in gdf.columns:
            gdf.insert(idx_col + 4, 'Zsol', gdf.pop('Zsol'))

        if error:
            gdf_conflict = mdf.loc[error_row, [left] + error_col]
           # if len(gdf_error) >= 1:
           #     print('Ambiguous values in both columns compared, change it manually !')
           #     print('Columns', error_col, 'must be dropped manually !')

        if verbose: print(len(gdf))

        return gdf, gdf_conflict

    if col is None and left_on is not None and right_on is not None:
        left = left_on
        right = right_on
        gdf, gdf_error = process()  # err_val)

    elif col is not None:
        left = col
        right = col
        gdf, gdf_error = process()  # err_val)
    # else:
        # print("error! 'col' cannot be defined with 'left_on' or 'right_on'")

    gdf = na_col_drop(gdf, non_na)
    if col_n is not None:
        gdf = na_line_drop(gdf, col_n=col_n)
    elif col_n is None and col is not None:
        n = gdf.columns.to_list().index(col) + 1
        gdf = na_line_drop(gdf, col_n=n)
    else:
        gdf = na_line_drop(gdf, col_n=0)

    gdf_error = na_line_drop(gdf_error, col_n=1)
    gdf_error = na_col_drop(gdf_error, non_na=1)

    real_error_col = []
    for c in gdf_error.columns:
        if c in gdf.columns:
            real_error_col.append(c)  # error columns to display
            error_view = True
        else:
            error_view = False

    gdf_error = gdf_error[real_error_col]

    if len(gdf_error) >= 1 and len(gdf_error.columns) >=2 and error_view:
        error_csv = f'merging_error_log({var_name(gdf1)}-{var_name(gdf2)})'
        gdf_error.to_csv(f'tmp_files/{error_csv}.csv', index=True)

        print('Ambiguous values in both columns compared, change it manually !')
        print('Columns', real_error_col, 'must be dropped manually !')
        print(f"error file created in 'tmp_files/{error_csv}.csv'")

    return gdf, gdf_error

def na_col_drop(data, non_na=10, drop=True, verbose=False):
    """
    delete NaN columns in the dataframe based on a minimum number of non-NaN values

    """

    drop_cols = []
    if verbose: print('Non-NaN values\n----------------')
    for c in data.columns:
        v = len(data.iloc[:, 0]) - data[c].isnull().sum() # number of non-na values
        if verbose: print(f'{c} --> val: {v} | Nan: {data[c].isnull().sum()}')
        if v < non_na:
            drop_cols.append(c)

    if drop and len(drop_cols) != 0:
        print(f'\nColumns dropped :{drop_cols}\n')
        data.drop(drop_cols, axis=1, inplace=True)

    return data


def na_line_drop(data, col_n=3):
    l1 = len(data)
    data['line_na'] = False

    for i in list(data.index): # range(len(data)):
        #print(i,'/',len(data))
        verif = True
        for j in data.columns.to_list()[col_n:-1]:
            if not pd.isnull(data.loc[i, j]): verif = False

        data.loc[i, 'line_na'] = verif

    data = data.query('line_na==False')
    data.reset_index(drop=True, inplace=True)
    data.drop('line_na', axis=1, inplace=True)
    l2 = len(data)
    nb_lines = l1 - l2
    if nb_lines > 0: print(f'{nb_lines} NaN lines dropped')

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
            print('Error! names list length and columns length are not the same.')

    data.rename(columns=new_name, inplace=True)

    return data