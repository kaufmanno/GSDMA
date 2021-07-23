import re
import numpy as np
import pandas as pd
from striplog import Component, Interval, Striplog, Lexicon

from core.orm import BoreholeOrm, PositionOrm
from utils.config import DEFAULT_BOREHOLE_LENGTH, DEFAULT_CONTAM_LEVELS, DEFAULT_BOREHOLE_DIAMETER, DEFAULT_ATTRIB_VALUE
from utils.visual import get_components
from utils.lexicon.lexicon_memoris import lexicon_memoris, pollutants_memoris


def striplog_from_text_file(filename, lexicon=None):
    """
    creates a Striplog object from a las or flat text file

    Parameters
    ------------
    filename : str name of text file
    lexicon : dict
        A vocabulary for parsing lithologic or stratigraphic descriptions
        (default set to Lexicon.default() if lexicon is None)

    Returns
    ---------
    strip: striplog object

    """

    if lexicon is None:
        lexicon = Lexicon.default()  # lexicon = Lexicon(lexicon_memoris.LEXICON)
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
        raise(EOFError("Error! Check the file extension !"))

    return strip


def striplog_from_dataframe(df, bh_name, attributes, symbols=None, iv_top=None,
        iv_base=None, thickness='Thickness', use_default=False, query=True):
    """
    creates a Striplog object from a dataframe

    Parameters
    ----------
    df : Pandas.DataFrame
        Dataframe that contains borehole intervals data

    bh_name: str
        Borehole name (or ID)

    attributes: list
        Attributes to use for creating components

    symbols : dict of striplog.Lexicon, striplog.Legend objects
        Legend and/or Lexicon to use for attributes

    iv_top : str
        Dataframe column that contains interval top

    iv_base : str
        Dataframe column that contains interval base

    thickness : str
        Dataframe column that contains lithology thickness (default:None)

    query : bool
        Work on a restricted copy of df by querying this dataframe first

    Returns
    -------
    strip : dict of striplog objects

    """

    attrib_cdt, attrib_top_cdt, attrib_base_cdt = False, False, False
    thick_cdt, color_cdt = False, False

    for attrib_col in attributes:
        if attrib_col not in list(df.columns):
            raise (NameError(f"{attrib_col} is not in the dataframe columns"))

    if thickness is not None and thickness in list(df.columns):
        thick_cdt = True
    if iv_top is not None and iv_top in list(df.columns):
        attrib_top_cdt = True
    if iv_base is not None and iv_base in list(df.columns):
        attrib_base_cdt = True

    strip = {}
    bh_list = []

    for i in df.index:
        if bh_name is not None and bh_name in df.columns:
            bh_id = bh_name
        else:
            bh_id = df.loc[i, 'ID']

        if bh_id not in bh_list:
            print(f"\n|__ID:\'{bh_id}\'")
            bh_list.append(bh_id)
            if query:
                selection = df['ID'] == f"{bh_id}"  # f'ID=="{bh_id}"'
                tmp = df[selection].copy()  # divide to work faster ;)
                tmp.reset_index(drop=True, inplace=True)
            else:
                tmp = df

            intervals = []
            for j in tmp.index:
                # components processing -------------------------------------------
                iv_components = []
                for attrib in attributes:
                    val = tmp.loc[j, attrib]
                    if attrib.lower() in pollutants_memoris.pollutant:
                        # default lexicon for contaminant
                        lexicon = Lexicon({attrib.lower(): DEFAULT_CONTAM_LEVELS})
                    elif attrib not in symbols.keys() and attrib.lower() in symbols.keys():
                        lexicon = symbols[attrib.lower()]['lexicon']
                    else:
                        lexicon = symbols[attrib]['lexicon']

                    if Component.from_text(val, lexicon) == Component({}):  # empty component !
                        print(f"Error : No value matching with '{val}' in given lexicon")
                    else:
                        iv_components.append(Component.from_text(val, lexicon))
                print(f'{iv_components}')

                # length/thickness processing --------------------------------------
                if thick_cdt and not pd.isnull(tmp.loc[j, thickness]):
                    thick = tmp.loc[j, thickness]
                else:
                    if use_default:
                        print(f'Warning : ++ No thickness provided, default is used '
                              f'(length={DEFAULT_BOREHOLE_LENGTH})')
                        thick = DEFAULT_BOREHOLE_LENGTH
                    else:
                        raise (ValueError('Cannot create interval with null thickness !'))

                # intervals processing ----------------------------------------------
                if attrib_top_cdt:
                    top = tmp.loc[j, iv_top]
                elif thick_cdt:
                    if j == tmp.index[0]:
                        top = 0
                    else:
                        top += tmp.loc[j - 1, thickness]
                else:
                    raise (ValueError('Cannot retrieve or compute top values. provide thickness values! '))

                if attrib_base_cdt:
                    base = tmp.loc[j, iv_base]
                else:
                    base = top + thick

                if base != 0.:
                    intervals = intervals + [Interval(top=top, base=base, description=val,
                                                      components=iv_components, lexicon=lexicon)]

            if len(intervals) != 0:
                strip.update({bh_id: Striplog(list_of_Intervals=intervals)})
            else:
                print(f"Error : -- Cannot create a striplog, no interval (length or base = 0)")

    print(f"Summary : {list(strip.values())}")

    return strip


def boreholes_from_dataframe(df, symbols=None, attributes=None, iv_top=None,
        iv_base=None, diameter='Diameter', thickness='Length',
        verbose=False, use_default=True):
    """ Creates a list of BoreholeORM objects from a dataframe

    Parameters
    ----------
    df: pandas.DataFrame
        A dataframe of borehole intervals

    x : str
        Column name where the x coordinates of the position of the top of the intervals are stored

    y : str
        Column name where the x coordinates of the position of the top of the intervals are stored

    z : str
        Column name where the x coordinates of the position of the top of the intervals are stored

    symbols: dict
        A dict e.g. {attribute_1: {'legend': striplog.Legend, 'lexicon': striplog.Lexicon}, ...}
         '
    attributes : list
        Dictionary with lexicons as keys and associated list of column names (attributes) as values

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
    pos_id = 0  # position id
    boreholes_orm = []
    components = []
    comp_id = 0  # component id
    component_dict = {}
    link_dict = {}  # link between intervals and components (<-> junction table)

    assert isinstance(df, pd.DataFrame)

    print(f'\nDataframe processing...\n================================')
    bh_id_list = []  #
    bh_idx = 0  # borehole index in the current dataframe

    if diameter in df.columns:
        diam = df[diameter]
    else:
        print(f'Warning : -- No borehole diameter, default is used (diameter={DEFAULT_BOREHOLE_DIAMETER})')
        diam = pd.Series([DEFAULT_BOREHOLE_DIAMETER] * len(df))

    for idx, row in df.iterrows():
        bh_name = row['ID']

        if bh_name not in bh_id_list:
            bh_id_list.append(bh_name)
            boreholes_orm.append(BoreholeOrm(id=bh_name))
            interval_number = 0

            bh_selection = df['ID'] == f"{bh_name}"
            tmp = df[bh_selection].copy()
            tmp.reset_index(drop=True, inplace=True)
            striplog_dict = striplog_from_dataframe(df=tmp, bh_name=bh_name,
                                            attributes=attributes,
                                            symbols=symbols, thickness=thickness,
                                            iv_top=iv_top, iv_base=iv_base,
                                            use_default=use_default, query=False)
            for strip in striplog_dict.values():
                # print('strip:', v)
                for c in get_components(strip):
                    if c not in component_dict.keys():
                        component_dict.update({c: comp_id})
                        comp_id += 1
                        # comp_id = list(component_dict.keys()).index(c)
                    # print(f'component: {c}, component_id: {comp_id}')

                interval_dict = {}
                # ORM processing
                for intv in strip:
                    top = PositionOrm(id=pos_id, upper=row['Z'] - intv.top.upper,
                                      middle=row['Z'] - intv.top.middle,
                                      lower=row['Z'] - intv.top.lower,
                                      x=row['X'], y=row['Y']
                                      )

                    base = PositionOrm(id=pos_id + 1, upper=row['Z'] - intv.base.upper,
                                       middle=row['Z'] - intv.base.middle,
                                       lower=row['Z'] - intv.base.lower,
                                       x=row['X'], y=row['Y']
                                       )

                    desc = ', '.join([c.json() for c in intv.components])
                    # print('description:', desc)
                    interval_dict.update({int_id: {'description': desc,
                                       'interval_number': interval_number,
                                       'top': top, 'base': base}})

                    for idx in intv.components:
                        if idx != Component({}):
                            if verbose:
                                print(f'comp_dict: {component_dict}')
                            link_dict.update({
                                (int_id, component_dict[idx]): {'extra_data': ''}})

                    interval_number += 1
                    int_id += 1
                    pos_id += 2

                if verbose:
                    print(f'{interval_dict}\n')
                if bh_idx < len(boreholes_orm):
                    boreholes_orm[bh_idx].intervals_values = interval_dict
                    boreholes_orm[bh_idx].length = tmp[thickness].cumsum().max()
                    if diam[bh_idx] is not None and not pd.isnull(diam[bh_idx]):
                        boreholes_orm[bh_idx].diameter = tmp[diameter][0]
                    else:
                        boreholes_orm[bh_idx].diameter = DEFAULT_BOREHOLE_DIAMETER

                bh_idx += 1
        else:
            # already processed
            pass

        components = {v: k for k, v in component_dict.items()}

    print(f"\nEnd of the process : {len(bh_id_list)} unique ID found")

    return boreholes_orm, components, link_dict
