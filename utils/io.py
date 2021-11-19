import collections.abc
import os
import re
from difflib import get_close_matches
from os import walk
import numpy as np
import geopandas as gpd
import pandas as pd
import datetime
from shapely import wkt
from ipywidgets import interact, IntSlider
from IPython.display import HTML, display
from utils.config import WARNING_TEXT_CONFIG


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


def read_geodf_file(filename=None, epsg=None, to_epsg=None, interact=False):  # file_dir=None,
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
        filename = str(input("File name and extension (.shp, .json, .gpkg, .csv) ? : "))

    # if file_dir is None :
    #   file_dir = ROOT_DIR + '/playground/TFE_test/tmp_files/'
    #  filename=file_dir+filename

    gdf = gpd.GeoDataFrame()

    if re.compile(r".+\.json|.+\.gpkg|.+\.shp").match(filename):
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
                gdf.insert(0, 'X', [row._geometry.x for idx, row in gdf.iterrows()])
                gdf.insert(1, 'Y', [row._geometry.y for idx, row in gdf.iterrows()])
                break
            elif resp == 'n':
                break
            print(f'{resp} is invalid, please try again...')

    elif to_epsg is not None and interact is False:
        gdf.to_crs(epsg=to_epsg, inplace=True)
        gdf = gdf.drop(['Longitude', 'Latitude', 'X', 'Y'], axis=1, errors='ignore')
        gdf.insert(0, 'X', [row._geometry.x for idx, row in gdf.iterrows()])
        gdf.insert(1, 'Y', [row._geometry.y for idx, row in gdf.iterrows()])

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
            gdf.insert(0, 'X', gdf._geometry.x)
        else:
            gdf.insert(0, 'X', gdf._geometry.x)

        if 'Y' in gdf.columns:
            gdf = gdf.drop(['Y'], axis=1)
            gdf.insert(1, 'Y', gdf._geometry.y)
        else:
            gdf.insert(1, 'Y', gdf._geometry.y)

        gdf.to_csv(f'{save_name}', index_label="Id", index=False, sep=',')
        print(f'{save_name}' + " has been saved !")
    else:
        print(f'file\'s name extension not given or incorrect, please choose (.json, .gpkg, .csv)')


def dataframe_viewer(df, rows=10, cols=12, step_r=1, step_c=1, un_val=None, view=True):
    # display dataframes with  a widget

    if un_val is None:
        print(f'Rows : {df.shape[0]}, columns : {df.shape[1]}')
    else:
        if isinstance(un_val, str):
            un_val = [un_val]

        for c in un_val:
            if c in df.columns:
                len(set(df[c]))
        print(f"Rows : {df.shape[0]}, columns : {df.shape[1]}, "
              f"Unique values on cols: {dict({c: len(set(df[c])) if c in df.columns else 'NA' for c in un_val})}")

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


def gen_id_from_ech(df, id_ech_col='ID_ech', id_col='ID', suffixes=None, prefixes=None, capture_regex=None, verbose=False):
    """ Generate boreholes ID ('ID) from sample ID ('ID_ech'), by removing suffixes.
    """

    if suffixes is None and prefixes is None and capture_regex is None:
        raise(ValueError("one of these 3 parameters (suffixes, prefixes or capture_regex) must be given!"))
    pref, suf = [], []
    capture = False
    presuf = False
    data = df.copy()
    if id_ech_col == 'ID':
        id_col = 'ID'
        id_ech_col = 'ID_ech'
        data.rename(columns={id_col: id_ech_col}, inplace=True)

    data[id_col] = data[id_ech_col]
    if suffixes is not None:
        assert isinstance(suffixes, list)
        suf = '|'.join(suffixes)
    if prefixes is not None:
        assert isinstance(prefixes, list)
        pref = '|'.join(prefixes)
    if capture_regex is not None:
        assert isinstance(capture_regex, str)
        capture = True
    if pref or suf: presuf = True

    strp = pref + '|' + suf
    for i in data.index:
        val = str(data.loc[i, id_ech_col])
        if capture and presuf and re.search(pref + capture_regex + suf, val, re.I):
            data.loc[i, id_col] = re.search(capture_regex, val, re.I).group(1)
        elif capture and re.search(capture_regex, val, re.I):
            data.loc[i, id_col] = re.search(capture_regex, val, re.I).group(1)
        else:
            data.loc[i, id_col] = re.sub(strp, '', val, re.I)

        if verbose:
            print(f"{id_col}: {val} --> {data.loc[i, id_col]}")

    return data


def gen_dated_id(gdf, ref_col='Ref', date_col=None, date_ref='No_date'):
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


def gen_geodf_geom(gdf):
    # geom = gpd.GeoSeries(gdf.apply(lambda x: Point(x['X'], x['Y']),1),crs={'init': 'epsg:31370'})
    # gdf = gpd.GeoDataFrame(gdf, geometry=geom, crs="EPSG:31370")

    gdf = gpd.GeoDataFrame(gdf, geometry=gpd.points_from_xy(gdf.X, gdf.Y, crs=str('EPSG:31370')))

    return gdf


def data_slicer(df, coi_dict, crit_col_dict=None, unknow_kw='Inconnu', verbose=False):
    """ create many dataframes based on data type, according to the columns given for each type of data, if there are present in the initial dataframe.

    df: Pandas.Dataframe
    coi_dict: dict
        dict containing a list of columns of interest, for each type of data.
    crit_col_dict: dict
        dict containing a list of specific columns that characterize a type of data and allow the creation of this data's dataframe.
        e.g: for 'lithology' data, specific columns are at least ['Intv_top', 'Intv_base']
    """
    df_dict = {}
    crit_found = {}
    data = df.copy()
    msg = ''
    remain_cols = list(df.columns)

    assert isinstance(coi_dict, dict)
    if crit_col_dict is not None:
        assert isinstance(crit_col_dict, dict)
        for k, v_cols in crit_col_dict.items():
            crit_cols = []
            for c in v_cols:
                if c in df.columns:
                    crit_cols.append(c)

            if len(crit_cols) >= 2:  # at least 2 criteria satisfied
                found = True
            else:
                found = False
            crit_found.update({k: found})

    for k, v_cols in coi_dict.items():
        no_real_cols = []
        real_cols = []
        for c in v_cols:
            if c in data.columns:
                real_cols.append(c)
            else:
                no_real_cols.append(c)
        if verbose and no_real_cols:
            print(f"For '{k}', {no_real_cols} not found in the dataframe\n")

        tmp_df = data[real_cols]
        if crit_found and crit_found[k]:
            if k.lower() in ['unknown', 'inconnu'] and 'Type' in tmp_df.columns:
                tmp_df = tmp_df.query(f'Type=="{unknow_kw}"')
            elif k.lower() in ['unknown', 'inconnu'] and 'Type' not in tmp_df.columns:
                tmp_df = pd.DataFrame()
        else:
            tmp_df = pd.DataFrame()
        df_dict.update({k: tmp_df})
        msg += f"{k}: {len(df_dict[k])} ; "

        for cl in tmp_df.columns:
            if cl in remain_cols:
                remain_cols.remove(cl)

    print(msg)
    if remain_cols:
        print(f"\n{WARNING_TEXT_CONFIG['green']}Not used columns:{WARNING_TEXT_CONFIG['off']}\n {remain_cols}")
    return df_dict


def data_merger(gdf1, gdf2, how='outer', on=None, dist_max=None, crit_2nd_col=None,
                error_tol_dict={0.1:['Diam_for', 'Long_for'], 0.01:['Z']}, drop_skip_col=None,
                verbose=False):
    """ Enhance data merging with automatic actions on dataframe after the merge

    Parameters
    ------------
    gdf1, gdf2 : pandas (Geo)DataFrame

    how: str
        the way to merge data (default= 'outer')
    on: str
        column use as primary criteria for merging and object distinction
    dist_max: float
        maximum distance between 2 objects
    crit_2nd_col: str
        column that contains dates as secondary criteria to distinguish objects.
        Effective when data have coordinates, otherwise better to give a list of columns to parameter 'on'
    drop_skip_col: list
        list of columns to ignore when drop duplicates
    error_tol_dict : dict
        dictionary of tolerance on value error for a list of columns
    verbose: bool

    Returns
    --------
    gdf: merged dataframe
    gdf_error: dataframe that contains ambiguous values encounter

    """

    distinct_objects_to_add = {}
    idx_distinct_obj = 0

    mdf = pd.merge(gdf1, gdf2, how=how, on=on)
    mdf.reset_index(drop=True, inplace=True)
    mdf.replace('nan', np.nan, inplace=True)
    k = 0

    if not isinstance(on, list):
        id_col = on
        for idx in mdf.query(f'{on}!={on}').index:
            mdf.loc[idx, 'ID'] = f'?{k}'
            k += 1
    else:
        id_col = on[0]  # use for ID column when we create a new line (see below)

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
    if crit_2nd_col not in dble_cols:
        crit_2nd_col = None  # avoid error due to column not in merged dataframe

    for col_i in dble_cols:
        gdf[col_i] = np.nan  # creation of the definitive column
        if verbose: print('\nColumn :', col_i)

    for idx in mdf.index:
        distinct_objects = True
        row_conf_cols = []  # conflictual columns for each row
        dist = 0

        if 'X' in dble_cols:  # coordinates in both dataframes
            # compute distance between the points coming from each dataframe
            if not pd.isnull(mdf.loc[idx, 'X_x']) and not pd.isnull(mdf.loc[idx, 'X_y']):
                for t in ['X_x', 'X_y', 'Y_x', 'Y_y']:
                    if isinstance(mdf.loc[idx, t], str) and re.search(',', mdf.loc[idx, t]):
                        mdf.loc[idx, t] = float(re.sub(',', '.', mdf.loc[idx, t]))
                    elif isinstance(mdf.loc[idx, t], str):
                        mdf.loc[idx, t] = float(mdf.loc[idx, t])

                dist = (mdf.loc[idx, 'X_x'] - mdf.loc[idx, 'X_y']) ** 2 + (
                        mdf.loc[idx, 'Y_x'] - mdf.loc[idx, 'Y_y']) ** 2
            else:
                distinct_objects = False

        if dist_max is None and crit_2nd_col is None:
            distinct_objects = False

        # compare with secondary criteria (e.g: date/time for temporal data)
        elif crit_2nd_col is not None and crit_2nd_col in dble_cols:
            # print('HERE')
            if not pd.isnull(mdf.loc[idx, crit_2nd_col + '_x']) and not pd.isnull(mdf.loc[idx, crit_2nd_col + '_y']):
                if mdf.loc[idx, crit_2nd_col + '_x'] == mdf.loc[idx, crit_2nd_col + '_y']:
                    distinct_objects = False
                    # if dates are the same, but coordinates are different
                    if dist_max is not None and dist <= dist_max ** 2:  # considered as same object
                        distinct_objects = False
                    elif dist_max is not None and dist >= dist_max ** 2:
                        distinct_objects = True
            else:
                distinct_objects = False

        elif dist_max is not None and 'X' in dble_cols:
            if dist <= dist_max ** 2:  # considered as same object
                distinct_objects = False

        if verbose: print(idx, 'distinct: ', distinct_objects)
        # print(idx, 'distinct: ', distinct_objects)

        # If objects are not distinct -> compare them and merge values or generate conflict
        # else add a new row in gdf to store two distinct object
        if not distinct_objects:  # comparison and merging
            for col_i in dble_cols:
                #print(idx, col_i, mdf.loc[idx, col_i + '_x'])
                # if repeated column i contains nan in gdf1 and a value in gdf2 -> keep value in gdf2
                if pd.isnull(mdf.loc[idx, col_i + '_x']) and not pd.isnull(mdf.loc[idx, col_i + '_y']):
                    gdf.loc[idx, col_i] = mdf.loc[idx, col_i + '_y']
                    gdf.loc[idx, col_i + '_y'] = np.nan
                    if verbose: print('1A')
                # if repeated column i contains nan in gdf2 and a value in gdf1 -> keep value in gdf1
                elif not pd.isnull(mdf.loc[idx, col_i + '_x']) and pd.isnull(mdf.loc[idx, col_i + '_y']):
                    gdf.loc[idx, col_i] = mdf.loc[idx, col_i + '_x']
                    gdf.loc[idx, col_i + '_x'] = np.nan
                    if verbose: print('1B')
                # if repeated columns contain the same value -> keep value in gdf1
                elif mdf.loc[idx, col_i + '_x'] == mdf.loc[idx, col_i + '_y']:
                    gdf.loc[idx, col_i] = mdf.loc[idx, col_i + '_x']
                    gdf.loc[idx, col_i + '_x'] = np.nan
                    gdf.loc[idx, col_i + '_y'] = np.nan
                    if verbose: print('1D')
                # if both repeated columns contain nan -> put nan in gdf
                elif pd.isnull(mdf.loc[idx, col_i + '_x']) and pd.isnull(mdf.loc[idx, col_i + '_y']):
                    gdf.loc[idx, col_i] = np.nan
                    if verbose: print('1C')
                # if repeated columns contain different values -> handle following dtype
                else:
                    # always keep one single object position values because not distinct objects
                    if col_i == 'X' or col_i == 'Y':  # or col_i == 'Z':
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
                            gdf.loc[idx, col_i] = '#conflict'
                            if col_i + '_x' not in conflict_col:
                                conflict_col = conflict_col + [col_i + '_x', col_i + '_y']
                            if idx not in conflict_row:
                                conflict_row = conflict_row + [idx]
                            conflict = True
                            row_conf_cols.append(col_i)
                            update_dict(conflict_idx_col, {idx: row_conf_cols})
                            if verbose: print('1H')

                    # if the values are not considered as the same
                    # check if values are close enough (according to error_tolerance)
                    else:
                        close_values = False
                        if error_tol_dict is not None:
                            a = mdf.loc[idx, col_i + '_x']
                            b = mdf.loc[idx, col_i + '_y']
                            for tol, cols in error_tol_dict.items():
                                if col_i in cols:
                                    tolerance_on_min = min(a, b) + min(a, b) * tol
                                    # values are close, choose the maximum
                                    if tolerance_on_min >= max(a, b):
                                        gdf.loc[idx, col_i] = max(a, b)
                                        close_values = True
                            # print(close_values, tolerance_on_min, max(a, b))
                            if verbose: print('1I')

                        # values are very different -> put in gdf_conflict

                        if not close_values:
                            gdf.loc[idx, col_i] = np.nan
                            if col_i + '_x' not in conflict_col:
                                conflict_col = conflict_col + [col_i + '_x', col_i + '_y']
                            if idx not in conflict_row:
                                conflict_row = conflict_row + [idx]
                            conflict = True
                            row_conf_cols.append(col_i)
                            update_dict(conflict_idx_col, {idx: row_conf_cols})
                        if verbose: print('1J')
        else:
            if verbose: print('2A')
            distinct_objects_to_add.update({idx_distinct_obj: {i: mdf.loc[idx, i] for i in single_cols}})
            distinct_objects_to_add[idx_distinct_obj][id_col] = '_' + str(distinct_objects_to_add[idx_distinct_obj][id_col]) + '_'
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

    if not isinstance(on, list):
        on = [on]
    a = 0
    for c in on:
        gdf.insert(a, c, gdf.pop(c))
        a += 1

    if conflict:
        gdf_conflict = mdf.loc[conflict_row, on + conflict_col]
        for r, c in conflict_idx_col.items():
            gdf_conflict.loc[r, 'Check_col'] = str(c).strip('"[]').replace("'", "")
        gdf_conflict.insert(0, 'Check_col', gdf_conflict.pop('Check_col'))
        print('Conflict values present. Please resolve this manually !')
    else:
        gdf.drop(['index'], axis='columns', inplace=True)

    if crit_2nd_col is not None and crit_2nd_col in gdf.columns:
        col_pos = 1
        gdf.insert(col_pos, crit_2nd_col, gdf.pop(crit_2nd_col))
    else:
        col_pos = 0
    if 'X' in gdf.columns: gdf.insert(col_pos+1, 'X', gdf.pop('X'))
    if 'Y' in gdf.columns: gdf.insert(col_pos+2, 'Y', gdf.pop('Y'))
    if 'Z' in gdf.columns: gdf.insert(col_pos+3, 'Z', gdf.pop('Z'))

    if drop_skip_col is not None:
        idx_to_drop = []
        gdf.drop_duplicates(subset=[c for c in gdf.columns if c not in drop_skip_col], inplace=True)
        if 'index' in gdf.columns and conflict:
            old_idx = gdf['index']
            idx_to_drop = [i for i in gdf_conflict.index if i not in old_idx]
        if len(idx_to_drop) > 0:
            gdf_conflict.drop(index=idx_to_drop, inplace=True)
        gdf.reset_index(drop=True, inplace=True)

    return gdf, gdf_conflict


def data_validation(overall_data, conflict_data, valid_dict=None, index_col='index', pass_col=['Origin_ID'],
                    valid_all=False, verbose=False):
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
    valid_all: bool
        use it when all conflict values are correct. this creates new rows to add values_y
    """

    check_cols = []
    conflict_cols_list = pd.unique(', '.join([x for x in pd.unique(conflict_data['Check_col'])]).split(', '))
    # add a new line when suppose no real conflict
    if valid_all:
        check_cols = [c for c in list(conflict_data.columns[2:])]
        id_col = conflict_data.columns[1]
        idx1 = conflict_data.index
        idx2 = pd.Index([len(overall_data)+i for i in range(len(idx1))])
        cols = pd.unique([re.sub('_x|_y', '', c) for c in list(conflict_data.columns[2:])])
        rows_val = overall_data.loc[idx1, :].copy()
        overall_data = overall_data.append(rows_val, ignore_index=True)
        overall_data.loc[idx2, id_col] = ['_' + v + '_' for v in conflict_data.loc[idx1, id_col]]

        for c in cols:
            overall_data.loc[idx2, c] = [v for v in conflict_data[c + '_y']]
            overall_data.loc[idx1, c] = [v for v in conflict_data[c + '_x']]
        # print('x1:', overall_data.loc[idx2, cols], '\n\ny1:', overall_data.loc[idx1, cols])
        conflict_data.loc[:, check_cols] = 'Done'

    # change conflictual values
    elif valid_dict is not None:
        for valid_col, idx in valid_dict.items():
            col = re.sub("_x|_y", "", valid_col)
            check_cols = check_cols + [col+'_x', col+'_y']
            q_idx = list(overall_data.query(f'{index_col}=={idx}').index)
            if verbose:
                print(f'{valid_col} : {idx}\n{col} : {q_idx}')
            overall_data.loc[q_idx, col] = conflict_data.loc[idx, valid_col]
            conflict_data.loc[idx, [col+'_x', col+'_y']] = 'Done'
    else:
        raise(ValueError('"valid_dict" cannot be None if "valid_all" not set True!'))

    # conflict_data cleaning after validation
    for i, r in conflict_data.iterrows():
        cols = r['Check_col'].split(', ')
        if len(cols) >= 1:
            for col in cols:
                if r[col + '_x'] == r[col + '_y']:
                    cols.remove(col)
                    # update check_col column values
                    conflict_data.loc[i, 'Check_col'] = ', '.join(cols)

    v_cols = []
    for l in conflict_cols_list:
        v_cols = v_cols + [l + '_x', l + '_y']
    # indices of rows where all correction have been done
    indices = conflict_data[conflict_data.loc[:, v_cols].isin(['Done']).all(axis=1)].index
    conflict_data.loc[indices, 'Check_col'] = ''

    index_to_drop = conflict_data.query('Check_col==""').index
    conflict_data.drop(index=index_to_drop, inplace=True)

    if len(conflict_data) == 0:
        if index_col in overall_data.columns:
            overall_data.drop(columns=index_col, inplace=True)
        conflict_data.drop(columns=list(conflict_data.columns), inplace=True)
        print("all conflicts have been fixed!")
    else:
        print(f"Validation done, but conflicts remain!")

    if valid_all:
        return overall_data


def replicate_values(data, id_col, cols_to_replicate, suffix=None, replace_id=False, criteria=None, verbose=False):
    """ Replicate values of a column to the same column of another row, if same ID and criteria is satisfied.

    id_col : str
        name of the column used as an ID
    cols_to_replicate : list
        list of columns to consider in replication
    suffix : list
        list of suffixes that can be removed from IDs
    replace_id : bool
        if true, replace ID values by values without suffixes
    criteria: dict
        dict of criteria for replicate values like {column:value}. If None, replicate values basis on same ID only
    """

    df = data.copy()
    id_list = []
    global_dict = {}
    v_dict = {}
    id_save = {}
    df['ID_copy'] = df[id_col]

    cols_to_replicate += [id_col]
    if suffix is not None:
        if not isinstance(suffix, list):
            raise (TypeError("suffix parameter must be a list of columns' name"))
        for i in df.index:
            for s in suffix:
                df.loc[i, 'ID_copy'] = re.sub(s, '', df.loc[i, 'ID_copy'], re.I) if not pd.isnull(df.loc[i, 'ID_copy']) else df.loc[i, 'ID_copy']

    for i in df.index:
        bh_id = df.loc[i, 'ID_copy']
        if bh_id not in id_list:
            id_list.append(bh_id)
            if criteria is not None:
                text = ''
                assert isinstance(criteria, dict)
                for k, v in criteria.items():
                    if isinstance(v, str):
                        v = f"'{v}'"
                    if text != '':
                        text += f" and {k}=={v}"
                    else:
                        text += f"{k}=={v}"
                q = df.query(f'ID_copy=="{bh_id} and {text}"').copy()
            else:
                q = df.query(f'ID_copy=="{bh_id}"').copy()

            q_idx = tuple(q.index)
            for c in cols_to_replicate:
                # looking for not-null value in the column
                val = np.nan
                for p, r in q.iterrows():
                    if not pd.isnull(r[c]):
                        if c == id_col and replace_id:
                            val = q.loc[p, 'ID_copy']
                        elif c == id_col:
                            update_dict(id_save, {p: r[c]})
                        else:
                            val = r[c]

                    if verbose:
                        if not pd.isnull(val) and val != r[c]:
                            print(f'-- different values : {p}, {c}: {val} | {r[c]}')
                        print(f'value kept for {c}:', val)

                v_dict.update({c: val})
            update_dict(global_dict, {q_idx: v_dict})

    for k, v_dict in global_dict.items():
        cols = [c for c in v_dict.keys()]
        vals = [v for v in v_dict.values()]
        df.loc[list(k), cols] = vals

    if replace_id:
        if id_col in df.columns:
            df.drop(columns=id_col, inplace=True)
        df.insert(0, id_col, df.pop('ID_copy'))
    else:
        idx = [k for k in id_save.keys()]
        ids = [v for v in id_save.values()]
        df.loc[idx, id_col] = ids
        df.drop(columns='ID_copy', inplace=True)

    return df


def na_col_drop(df, col_non_na=10, drop=True, verbose=False):
    """
    Delete columns in the dataframe where the count of non-NaN values is lower than col_non_na

    """
    data = df.copy()
    drop_cols = []
    if verbose: print('Non-NaN values\n----------------')
    for c in data.columns:
        if verbose: print(f'{c} --> val: {data[c].notnull().sum()} | Nan: {data[c].isnull().sum()}')
        if data[c].notnull().sum() < col_non_na:
            drop_cols.append(c)

    if drop and drop_cols:
        print(f'Columns dropped :{drop_cols}\n')
        data.drop(drop_cols, axis=1, inplace=True)

    return data


def collect_time_data(df, regex=None, sort_values_by='Date_mes'):
    """create a new line of values according to the date found in columns name. like 'Colx_08/09/2010'

    df : Pandas.Dataframe
    regex: str
        string that contains named regex group to retrieve date and column name. 
        e.g: '(?P<col>\w+)_(?P<date>\d+/\d+/\d+)'
    sort_values_by: str
        sort the dataframe's values by a column

    """

    data = df.copy()
    cols = list(data.columns)
    dates = []
    cols_to_drop = []
    no_copy_col = ['Date_mes']
    cols_with_dates = []

    if regex is None:
        regex = '(?P<col>\w+)_(?P<date>\d+/\d+/\d+)'

    for c in cols:
        if re.search(regex, c, re.I):
            dates.append(re.search(regex, c, re.I).group(2))
            cols_with_dates.append(c)
    dates = list(set(dates))

    # move colums with date to the end
    for c in cols_with_dates:
        cols.remove(c)
    cols += cols_with_dates

    for i in data.index:
        for c in cols:
            col = c
            mes_id = i

            if re.search('\d+/\d+/\d+', c, re.I):
                if c not in cols_to_drop:
                    cols_to_drop.append(c)
                col = re.search(regex, c, re.I).group(1)
                if col not in no_copy_col:
                    no_copy_col.append(col)

                d = re.search(regex, c, re.I).group(2)
                dt = d.split('/')
                mes_id = i + dates.index(d) / 10  # generate indexes 1.1, 1.2, ... 
                data.loc[mes_id, :] = data.loc[i, :]  # replicate the row data to the new row
                data.loc[mes_id, 'Date_mes'] = datetime.date(int(dt[2]), int(dt[1]), int(dt[0]))
                data.loc[mes_id, col] = data.loc[i, c]

            data.loc[mes_id, col] = data.loc[i, c]

    data = data.query('Date_mes == Date_mes')
    data.drop(columns=cols_to_drop, inplace=True)
    data.sort_values(sort_values_by, inplace=True)
    data.reset_index(drop=True, inplace=True)
    print('dates found:', dates)

    return data


def collect_measure(df, params_kw, params_col='Params', alter_df=False, verbose=False):
    data = df.copy()
    val_dict = {}
    cols_to_drop = []
    data[params_col] = np.nan

    for i in data.index:
        for c in data.columns:
            for p in params_kw:
                if re.search(p, c, re.I):
                    if not pd.isnull(data.loc[i, c]):
                        val_dict.update({c: data.loc[i, c]})
                        if verbose: print(val_dict)
                    cols_to_drop.append(c)

        data.loc[i, params_col] = str(val_dict)

    cols_to_drop = list(set(cols_to_drop))

    if alter_df:
        data.drop(columns=cols_to_drop, inplace=True)
        print('columns droped :', cols_to_drop)
    else:
        print('Set "alter_df=True", if columns must be droped :', cols_to_drop)

    return data


def fix_duplicates(df1, df2, id_col='ID', crit_2nd_col=None, x_gap=.8, y_gap=.8, drop_old_id=True):
    """ Look for nearest objects in 2 dataframes, by position, and set same ID
    (to treat same position but different names cases)

    Parameters
    ------------
    x_gap : float
        gap between X coordinates of an object in df1 and df2
    y_gap : float
        gap between Y coordinates of an object in df1 and df2
    crit_2nd_col : str
        Secondary criteria. e.g: Objects must be the same type (e.g: 'soil', 'piezo') for comparison
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
        q_idx = list(data2.query(f"X <= {x + x_gap} and X >= {x} and Y <= {y + y_gap} and Y >= {y}").index)
        same_obj = False

        if q_idx:
            same_obj = True
            if crit_2nd_col is not None and data1.loc[idx, crit_2nd_col] != data2.loc[idx, crit_2nd_col]:
                same_obj = False

        if same_obj:  # same object, check type and keep one ID
            cnt += len(q_idx)
            data1.loc[idx, f'new_{id_col}'] = data1.loc[idx, id_col]
            data2.loc[q_idx, f'new_{id_col}'] = data1.loc[idx, id_col]
        else:  # distinct object, keep original ID
            data1.loc[idx, f'new_{id_col}'] = data1.loc[idx, id_col]
            data2.loc[q_idx, f'new_{id_col}'] = data2.loc[idx, id_col]

    print(f"{cnt} duplicate objects fixed!")
    data1.rename(columns={id_col: f'Old_{id_col}', f'new_{id_col}': id_col}, inplace=True)
    data2.rename(columns={id_col: f'Old_{id_col}', f'new_{id_col}': id_col}, inplace=True)
    data1.insert(0, id_col, data1.pop(id_col))
    data2.insert(0, id_col, data2.pop(id_col))

    if drop_old_id:
        data1.drop(columns=f'Old_{id_col}', inplace=True)
        data2.drop(columns=f'Old_{id_col}', inplace=True)


def data_filter(data, position=True, id_col='ID', expression=None, regex=None,
                bypass_col=['Old_ID', 'Origin_ID'], dist_max=1, drop=False, drop_old_id=True,
                error_max_dict={0.1:['Diam_for', 'Long_for'], 0.01:['Z']}):
    """
    filter duplicates in dataframe rows, considering ID, position, and/or an expression)

    Parameters
    ------------
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
        data.rename(columns={f'{id_col}': 'Origin_ID', f'new_{id_col}': id_col}, inplace=True)

    if 'X' not in data:
        position = False  # avoid error due to dist_max definition without position data

    # filtering
    for i in data.index:
        uid = data.loc[i, id_col]
        tmp = data[data[id_col] == f"{uid}"]

        if uid not in id_list and len(tmp) >= 2:
            id_list.append(uid)  # list of ID already treated
            drop_dict = {}
            for j in tmp.index:  # retrieve duplicates ID index
                if j != i:
                    if position:   # use position XY
                        pos_1 = [data.loc[i, 'X'], data.loc[i, 'Y']]
                        pos_2 = [data.loc[j, 'X'], data.loc[j, 'Y']]
                        distinct = not ((pos_1[0] - pos_2[0]) ** 2 + (pos_1[1] - pos_2[1]) ** 2 <= dist_max ** 2)
                        if not distinct:
                            bypass_col += ['X', 'Y', id_col]
                    else:
                        bypass_col += ['X', 'Y', id_col]
                    if j not in drop_idx:
                        same_state_list = []
                        same = False
                        for c in range(len(data.columns) - 1):
                            if cols[c] not in bypass_col:
                                if data.iloc[i, c] == data.iloc[j, c]:  # all values (str, numeric) are equals
                                    same = True
                                # numeric values
                                elif data.iloc[i, c] != data.iloc[j, c] and re.search('int|float',
                                                                        data[cols[c]].dtype.name):
                                    a = data.iloc[i, c]
                                    b = data.iloc[j, c]
                                    for tol, tol_cols in error_max_dict.items():
                                        if cols[c] in tol_cols:
                                            tolerance_on_min = min(a, b) + min(a, b) * tol
                                            if tolerance_on_min < max(a, b):
                                                same = False
                                                if cols[c] in check_dict.keys():
                                                    idxs = check_dict[cols[c]] + [j]
                                                else:
                                                    idxs = [j]
                                                update_dict(check_dict, {cols[c]: idxs})
                                                if j not in check_idx: check_idx.append(j)
                                            else:
                                                same = True

                                else:  # str values
                                    same = False
                                    if cols[c] in check_dict.keys():
                                        idxs = check_dict[cols[c]] + [j]
                                    else:
                                        idxs = [j]
                                    update_dict(check_dict, {cols[c]: idxs})
                                    if j not in check_idx: check_idx.append(j)

                            same_state_list.append(same)

                    if False not in same_state_list:
                        print('AA')
                        if j not in drop_idx:
                            drop_idx.append(j)
                        # count NaN values on row
                        # drop_dict.update({j: data.loc[j, :].isnull().sum()})
            """
            # keep the best row based on less NaN values
            best_row = [k for k, v in drop_dict.items() if v == min(drop_dict.values())]
            # print(i, best_row, drop_dict, data.loc[i, 'ID'])
            if len(best_row) == 0 or (data.loc[i, :].isnull().sum() < drop_dict[best_row[0]]):
                best_row = [i]
            else:
                drop_dict.update({i: data.loc[i, :].isnull().sum()})
            if best_row[0] in drop_dict.keys():
                drop_dict.pop(best_row[0])
                drop_idx = drop_idx + list(drop_dict.keys())
            """

    check_data = data.loc[check_idx, [id_col] + list(check_dict.keys())]
    check_data.insert(0, 'Check_col', '')
    for key, val in check_dict.items():
        for v in val:
            if check_data.loc[v, 'Check_col'] == '':
                check_data.loc[v, 'Check_col'] = key
            else:
                check_data.loc[v, 'Check_col'] = ', '.join([check_data.loc[v, 'Check_col']] + [key])

    if len(check_data) > 0:
        print("some data must be checked !")
        # print(f"some data must be checked , look at indices : {check_dict.values()}\n")
        pass

    if len(drop_idx) > 0:
        print(f"same objects at indices:{drop_idx}, will be dropped if drop is set True!")

    if expression is not None:
        data.rename(columns={id_col: 'Old_ID'}, inplace=True)
        data.insert(0, id_col, data['Old_ID'].apply(lambda x: re.sub(f"{expression}|' '", "", str(x))))

    if drop:
        data.drop(index=drop_idx, inplace=True)
        data.reset_index(drop=True, inplace=True)
    if drop_old_id and reg is not None:
        data.drop(columns='Old_ID', inplace=True)
        data.drop(columns='Origin_ID', inplace=True)

    print(f"Rows : {data.shape[0]} ; Columns : {data.shape[1]} ; Unique on '{id_col}' : {len(set(data[id_col]))} ; ")

    return data, check_data


def na_line_drop(df, col_n=3, line_non_na=0, drop_by_position=False,
                 old_idx=False, verbose=False):
    """
    Delete rows in the dataframe where the count of non-NaN values is lower than rows_non_na

    """

    data = df.copy()
    l1 = len(data)
    no_pos = []
    data['line_na'] = False

    # drop if no position coordinates
    if drop_by_position and 'X' in data.columns:
        no_pos = data.query('X.isnull() and Y.isnull()').index
        data.drop(index=no_pos, inplace=True)
        print(f"{len(no_pos)} without position -> lines dropped !")

    for i in range(len(data)): # data.index:
        if verbose: print(i)

        if line_non_na >= data.iloc[i, col_n:-1].notnull().sum():
            data.loc[i, 'line_na'] = True

    data = data.query('line_na==False')
    data.reset_index(drop=(not old_idx), inplace=True)
    data.drop(columns='line_na', inplace=True)
    l2 = len(data)
    nb_lines = l1 - l2
    if nb_lines > 0 and nb_lines != len(no_pos): print(f'{nb_lines} NaN lines dropped')

    return data


def dble_col_drop(data, drop=True, keep_max=True):
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
                        if keep_max:
                            data.iloc[j, i] = max(data.iloc[j, i], data.iloc[j, k])
                        else:
                            data.iloc[j, i] = min(data.iloc[j, i], data.iloc[j, k])

    print(f"column(s) dropped: {[f'{x}:{y}' for x, y in idx_drop.items()]}")
    new_col = list(set(range(len(data.columns))) - set(idx_drop.keys()))
    if drop: data = data.iloc[:, new_col]

    return data


def col_ren(df, row_num=None, mode=0, name=None, strip_regex=None, cutoff=0.65,
            col_num_sep=None, verbose=False):
    """
    mode: int
        set 0 to rename columns with values of a row, set 1 if provide name list or dict
    strip_strip_regex: str
        regex string that contains invalid characters to strip from columns names
    col_num_sep: str
        a regex character between a column's name and ending number that identify a column when same columns exist in the dataframe.
        e. g: column,s names : ID_1, ID_2. Here the separation character is '_'. Don't forget to use '\' when special character like '\.' for '.'.
    """
    new_names_dict = {}
    news = []
    data = df.copy()

    if mode != 0 and mode != 1:
        print("Error! Parameter \'Mode\' must be 0 or 1 (if 1, colums length must be equal to name length)")

    elif mode == 0:
        for i in range(len(data.columns)):
            col = str(data.iloc[row_num, i])
            if re.search('nan', col, flags=re.IGNORECASE):
                new_names_dict.update({data.columns[i]: f'col_{i}'})
            else:
                new_names_dict.update({data.columns[i]: col})

        data.drop([row_num], axis=0, inplace=True)
        data.reset_index(drop=True, inplace=True)

    elif mode == 1:
        if isinstance(name, list):
            if len(name) == len(data.columns):
                for i in range(len(name)):
                    new_names_dict.update({data.columns[i]: name[i]})
            else:
                raise (TypeError('Error! names list length and columns length are not the same.'))

        elif isinstance(name, dict):
            pol_fields = [p.lower() for p in name.keys()]
            if strip_regex is None:
                strip_regex = ',|\?| |>|<|-|\n|_|\(|\.|\)'
            if col_num_sep is None:
                col_num_sep = '\.'

            for i in range(len(data.columns)):
                keys = list(name.keys())
                old = data.columns[i]
                if old.lower() not in pol_fields:
                    news.append(old)

                old_mod = re.sub(strip_regex, '', old)
                closest = get_close_matches(old_mod, keys, n=3, cutoff=cutoff)
                keep_ = None
                for p in closest:
                    keep = re.findall(f'^{old}', p, re.I)
                    if keep:
                        keep_ = keep
                        closest = keep
                if closest:
                    old_mod = re.sub(strip_regex, '', closest[0])

                if verbose: print(f"{i} {old} : {keep_}---- {closest}")

                num_search = re.search(f'(\w+)({col_num_sep}\d$)', old)
                num = ''
                if num_search:
                    num = "_<" + num_search.group(2).lstrip(col_num_sep) + ">"
                    c = num_search.group(1)

                for k in keys:
                    k_mod = re.sub(strip_regex, '', k)
                    if re.match(f"{k_mod}", old_mod, flags=re.I):
                        new_names_dict.update({old: name[k] + num})
                    elif num != '':
                        new_names_dict.update({old: c + num})

    data.rename(columns=new_names_dict, inplace=True)
    if news:
        print(f"\n{WARNING_TEXT_CONFIG['blue']}Possible new pollutants names:{WARNING_TEXT_CONFIG['off']}\n{news}")

    f_cols = list(data.columns)
    dble_cols = list(set([(x, f_cols.count(x)) for x in f_cols if f_cols.count(x) > 1]))
    if dble_cols:
        print(f"{WARNING_TEXT_CONFIG['red']}Double columns' name found :{WARNING_TEXT_CONFIG['off']}\n{dble_cols}")

    return data


def compute_borehole_length(df, mode='length', length_col=None, top_col='Litho_top',
                            base_col='Litho_base', reset_drop=True):
    """

    """
    df[top_col] = df[top_col].astype('float64')
    df[base_col] = df[base_col].astype('float64')

    # compute length or thickness based on litho_top and litho_base
    id_list = []

    if mode == 'length':
        if length_col is None:
            length_col = 'Long_for'
        for i in df.index:
            try:
                float(df.loc[i, top_col])
            except ValueError:
                df.loc[i, top_col] = np.nan
            try:
                float(df.loc[i, base_col])
            except ValueError:
                df.loc[i, base_col] = np.nan

            id_ = df.loc[i, 'ID']
            if id_ not in id_list:
                id_list.append(id_)
                if isinstance(id_, str):
                    sql_id = f"{id_}"
                elif isinstance(id_, float) or isinstance(id_, int):
                    sql_id = id_

                tmp = df[df['ID'] == sql_id]
                df.loc[tmp.index, length_col] = max(tmp[base_col]) - min(tmp[top_col])
    elif mode == 'thickness':
        if length_col is None:
            length_col = 'Ep_litho'
        df[length_col] = df[[top_col, base_col]].apply(lambda x: round(x[1]-x[0],3), axis=1)
    else:
        raise(ValueError("Only 'length' or 'thickness' are allowed!"))

    df.drop(index=df.query(f'{base_col}.isnull() and {top_col}.isnull()').index, inplace=True)
    df.insert(df.columns.to_list().index('ID') + 1, length_col, df.pop(length_col))
    df.reset_index(drop=reset_drop, inplace=True)


def files_search(work_dir, files_dict, prefix='', skip=None, details=False):
    if skip is None:
        skip = "we don't want to skip a word"

    for k in files_dict.keys():
        tmp_list = []
        for p, d, f in os.walk(work_dir):
            for x in f:
                add = False
                if re.search(prefix, x, re.I) and not re.search(skip, x, re.I):
                    add = True
                    i = str(f'{p}/{x}')
                else:
                    add = False
                    i = ''

                if re.search(k, i, re.I) and add:
                    tmp_list.append(i)
        tmp_list.sort()
        files_dict.update({k: tmp_list})

    for k, v in files_dict.items():
        print(k, ' \t: ', len(v))

    if details:  # Look filenames
        which = files_dict.keys()

        for w in which:
            print('\n+++++++++++++++++')
            print(f'+  {w.upper()}\t+ ')
            print('+++++++++++++++++')
            [print(i, '-', x) for i, x in enumerate(files_dict[w], 0)]


def data_overview(d, verbose=False):  # check for same datasets in given files
    """d: dict
    """
    l = len(d)
    with_coord = []
    no_coord = []
    same = []

    def create_df(files, verbose=True):  # find another name for this function
        """
        create dataframes from files and test if they contain position informations
        files: list of files name
        """
        dfs = []
        for f in files:
            df = pd.read_csv(f, delimiter=',')
            dfs.append(df)

            if verbose:
                if 'X' in list(df.columns):
                    msg = ' --> Coordinates'
                else:
                    msg = ' --> No coordinates'

                print(f"df1 : {msg}")

        return dfs

    for i in range(l - 1):
        for j in range(i, l):
            a, b = create_df([d[i], d[j]], verbose)
            if j != i:
                if a.equals(b):
                    same.append((i, j))

            if 'X' in list(b.columns) and j not in with_coord:
                with_coord.append(j)
            elif 'X' not in list(b.columns) and j not in no_coord:
                no_coord.append(j)

    print(f'Same files:{same}\nFiles with coordinates:{with_coord}\nFiles without coordinates:{no_coord}')


def update_dict(d, u):
    """
    parameters
    ------------
    d: dict to update
    u: dict to add
    returns
    ---------
    d : dict
    """
    for k, v in u.items():
        if isinstance(v, collections.abc.Mapping):
            d[k] = update_dict(d.get(k, {}), v)
        else:
            d[k] = v
    return d


def dict_viewer(dictionary):
    """
    Jupyter Notebook magic repr function for dictionaries.
    """
    rows = ''
    s = '<tr><td><strong>{k}</strong></td><td>{v}</td></tr>'
    for k, v in dictionary.items():
        rows += s.format(k=k, v=v)
    html = '<table>{}</table>'.format(rows)
    return display(HTML(html))