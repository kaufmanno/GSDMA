import re
import pandas as pd
from striplog import Component, Interval, Striplog, Lexicon
import core.visual as cv
from core.orm import SampleOrm
from utils.config import DEFAULT_BOREHOLE_LENGTH, DEFAULT_CONTAM_LEVELS, DEFAULT_LITHO_LEXICON, DEFAULT_POL_LEXICON
from utils.lexicon.lexicon_memoris import LEX_SOIL_NORM
from difflib import get_close_matches


def get_contam_level_from_df(df, verbose=False):
    abbr_keys = list(DEFAULT_POL_LEXICON.abbreviations.keys())
    abbr_values = list(DEFAULT_POL_LEXICON.abbreviations.values())
    pollutants = [p for p in df.columns if p in DEFAULT_POL_LEXICON.abbreviations.keys() or p in DEFAULT_POL_LEXICON.abbreviations.values()]

    result = {}
    for i in df.index:
        col_levels = {}
        for c in df.columns:
            level = 'Inconnu'
            if c in pollutants:
                val = df.loc[i, c]
                if c in abbr_keys:
                    pol_name = DEFAULT_POL_LEXICON.abbreviations[c]
                elif c in abbr_values:
                    pol_name = c
                else:
                    raise (NameError('Pollutant not found in lexicon!'))

                if pol_name in LEX_SOIL_NORM['pollutants'].keys():
                    d = LEX_SOIL_NORM['pollutants'][pol_name]
                    for lv in list(d.keys()):
                        if verbose: print(f"-------- {val} ? {d[lv]}")
                        if val >= d[lv]:
                            level = list(d.keys())[list(d.values()).index(d[lv])]

                col_levels.update({c: level})
                if verbose: print(f"{i} {pol_name}: {level} - {val}")

        result.update({i: col_levels})
    return result


def get_contam_level_from_value(value, pollutant, pol_lexicon=None, verbose=False):
    """ assign a contamination level according to a value and pollutant,
    based on standard (e.g: soil pollutants standard for industrial sites)
    Parameters
    ------------
    value: float
        contaminant concentration
    pollutant: str
        contaminant name
    verbose:  Bool
    """
    if pol_lexicon is None:
        pol_lexicon = DEFAULT_POL_LEXICON

    abbr_names = list(pol_lexicon.abbreviations.keys())  # retrieve pollutants' abbreviated names
    abbr_names_lowercase = [n.lower() for n in abbr_names]
    full_names = list(pol_lexicon.abbreviations.values())  # retrieve pollutants' full names
    level = 'Inconnu'

    if pollutant in abbr_names or pollutant.lower() in abbr_names_lowercase:
        pol_name = DEFAULT_POL_LEXICON.abbreviations[pollutant].lower()
    elif pollutant.lower() in full_names:
        pol_name = pollutant.lower()
    else:
        pollutant = get_close_matches(pollutant, full_names)
        if len(pollutant)>0:
            pollutant = pollutant[0]
            print(f'No matching! Equivalent closest pollutant name found is {pollutant}\n')
        else:
            raise (NameError(f'Pollutant "{pollutant}" not found in lexicon!'))

    if pol_name in LEX_SOIL_NORM['pollutants'].keys():
        d = LEX_SOIL_NORM['pollutants'][pol_name]
        for lv in list(d.keys()):
            if verbose: print(f"-------- {value} ? {d[lv]}")
            if value >= d[lv]:
                level = list(d.keys())[list(d.values()).index(d[lv])]

    if verbose: print(f"{pol_name}: {level} - {value}")
    return pol_name, level


def striplog_from_dataframe(df, bh_name, attributes, id_col='ID', symbols=None,
                            intv_top=None,intv_base=None, thickness='Thickness',
                            use_default=False, query=True):
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

    intv_top : str
        Dataframe column that contains interval top

    intv_base : str
        Dataframe column that contains interval base

    thickness : str
        Dataframe column that contains lithology thickness (default:None)

    query : bool
        Work on a restricted copy of df by querying this dataframe first

    Returns
    -------
    strip : dict of striplog objects

    """

    for attrib_col in attributes:
        if attrib_col not in list(df.columns):
            raise (NameError(f"{attrib_col} is not in the dataframe columns"))

    strip = {}
    bh_list = []

    for j in df.index:
        if bh_name is not None and bh_name in df.columns:
            bh_id = bh_name
        else:
            bh_id = df.loc[j, id_col]

        if bh_id not in bh_list:
            print(f"\n|__ID:\'{bh_id}\'")
            bh_list.append(bh_id)
            if query:
                selection = df[id_col] == f"{bh_id}"  # f'ID=="{bh_id}"'
                tmp = df[selection].copy()  # divide to work faster ;)
                tmp.reset_index(drop=True, inplace=True)
            else:
                tmp = df

            intervals = intervals_from_dataframe(tmp, attributes, symbols,
                                                 intv_top, intv_base, thickness,
                                                 sample_prop=None)
            if len(intervals) != 0:
                strip.update({bh_id: Striplog(list_of_Intervals=intervals)})
            else:
                print(f"Error : -- Cannot create a striplog, no interval (length or base = 0)")

    print(f"Summary : {strip.values()}")

    return strip


def intervals_from_dataframe(df, attributes=None, symbols=None,
                             intv_top=None, intv_base=None,
                             thickness=None, sample_prop=None,
                             use_default=False):

    pollutants = list(DEFAULT_POL_LEXICON.abbreviations.keys()) + \
                 list(DEFAULT_POL_LEXICON.abbreviations.values())

    attrib_cdt, attrib_top_cdt = False, False
    thick_cdt, color_cdt = False, False

    if thickness is not None and thickness in list(df.columns):
        thick_cdt = True
    if intv_top is not None and intv_top in list(df.columns):
        attrib_top_cdt = True

    intervals, samples_orm = [], []
    top, base, thick, val = 0, 0, 0, 0
    lexicon = ''
    for j in df.index:
        # components processing -------------------------------------------
        iv_components = []
        for attrib in attributes:
            val = df.loc[j, attrib]
            # retrieve contamination level
            if attrib in pollutants or attrib.lower() in pollutants:
                if isinstance(val, str):
                    val = val.replace(',', '.')
                val = float(val)
                attrib, val = get_contam_level_from_value(val, attrib)

            if attrib.lower() in DEFAULT_POL_LEXICON.pollutant:
                # default lexicon for contaminant
                lexicon = Lexicon({attrib.lower(): DEFAULT_CONTAM_LEVELS})
            elif attrib not in symbols.keys() and attrib.lower() in symbols.keys():
                lexicon = symbols[attrib.lower()]['lexicon']
            else:
                lexicon = symbols[attrib]['lexicon']
            if Component.from_text(val, lexicon) == Component({}):
                print(f"Error : No value matches with '{val}' in given lexicon")
            else:
                iv_components.append(Component.from_text(val, lexicon))

        # length/thickness processing --------------------------------------
        if thick_cdt and not pd.isnull(df.loc[j, thickness]):
            thick = df.loc[j, thickness]
        # else:
        #     if use_default:
        #         print(f'Warning : ++ No thickness provided, default is used '
        #               f'(length={DEFAULT_BOREHOLE_LENGTH})')
        #         thick = DEFAULT_BOREHOLE_LENGTH
        #     else:
        #         raise (ValueError('Cannot create interval with null thickness !'))

        # intervals processing ----------------------------------------------
        if attrib_top_cdt:
            top = df.loc[j, intv_top]
            base = df.loc[j, intv_base]
        elif thick_cdt:
            thick = df.loc[j, thickness]
            if j == df.index[0]:
                top = 0
                base = top + thick
            else:
                prev_thick = df.loc[j-1, thickness]
                top += prev_thick
                base = top + thick
        else:
            raise (ValueError("Cannot retrieve or compute interval's top values. provide thickness or top/base values!"))

        if base != 0. or base != 0:
            if sample_prop is not None:  # to use when intervals are based on samples
                assert isinstance(sample_prop, dict)
                if 'id_col' in sample_prop.keys() and 'type_col' in sample_prop.keys():
                    s_type = df.loc[j, sample_prop['type_col']]
                    s_name = df.loc[j, sample_prop['id_col']]
                else:
                    raise(KeyError("sample_prop dict must contain at least 2 keys : 'id_col', 'type_col'"))
                if 'date_col' not in sample_prop.keys():
                    s_date = None
                elif sample_prop['date_col'] is None:
                    s_date = None
                else:
                    s_date = df.loc[j, sample_prop['date_col']]

                intervals = intervals + [cv.Sample3D(top=top, base=base, s_type=s_type,
                                                     date=s_date, components=iv_components,
                                                     name=s_name, description=val,
                                                     lexicon=lexicon)]
            else:
                intervals = intervals + [Interval(top=top, base=base,
                                        description=val, lexicon=lexicon,
                                        components=iv_components)]
        else:
            raise(ValueError('Interval base value cannot be : 0 !'))

    return intervals


def striplog_from_text_file(filename, lexicon=None):
    """
    creates a Striplog object from a las or flat text file

    Parameters
    ------------
    filename : str name of text file
    lexicon : dict
        A vocabulary for parsing lithological or stratigraphical descriptions
        (default set to Lexicon.default() if lexicon is None)

    Returns
    ---------
    strip: striplog object

    """

    if lexicon is None:
        lexicon = DEFAULT_LITHO_LEXICON
    elif isinstance(lexicon, Lexicon):
        lexicon = lexicon
    else:
        raise(TypeError(f"Must provide a lexicon, not '{type(lexicon)}'"))

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


def dict_repr_html(dictionary):
    """
    Jupyter Notebook magic repr function for dictionaries.
    """
    rows = ''
    s = '<tr><td><strong>{k}</strong></td><td>{v}</td></tr>'
    for k, v in dictionary.items():
        rows += s.format(k=k, v=v)
    html = '<table>{}</table>'.format(rows)
    return html
