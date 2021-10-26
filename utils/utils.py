import re
import pandas as pd
from striplog import Component, Interval, Striplog, Lexicon
# import warnings
from utils.config import DEFAULT_CONTAM_LEVELS, DEFAULT_LITHO_LEXICON, DEFAULT_POL_LEXICON, WARNING_TEXT_CONFIG
from utils.lexicon.lexicon_memoris import LEX_SOIL_NORM, LEX_WATER_NORM
from difflib import get_close_matches


def get_contam_level_from_df(df, samp_type_col='Type_ech', verbose=False):
    abbr_keys = list(DEFAULT_POL_LEXICON.abbreviations.keys())
    abbr_values = list(DEFAULT_POL_LEXICON.abbreviations.values())
    pollutants = [p for p in df.columns if p in DEFAULT_POL_LEXICON.abbreviations.keys() or p in DEFAULT_POL_LEXICON.abbreviations.values()]
    samp_type_cdt = True  # a sample always has a type (soil, water)
    if samp_type_col not in df.columns:
        samp_type_cdt = False

    result = {}
    for i in df.index:
        col_levels = {}

        if samp_type_cdt:
            if re.search('sol|soil', df.loc[i, samp_type_col], re.I):
                level_norm = LEX_SOIL_NORM['pollutants']
            elif re.search('eau|water', df.loc[i, samp_type_col], re.I):
                level_norm = LEX_WATER_NORM['pollutants']
        else:  # assert all samples type as 'soil'
            level_norm = LEX_SOIL_NORM['pollutants']

        for c in df.columns:
            level = 'Inconnu'
            if c in pollutants:
                val = df.loc[i, c]
                if c in abbr_keys:
                    pol_name = DEFAULT_POL_LEXICON.abbreviations[c]
                elif c in abbr_values:
                    pol_name = c
                else:
                    raise (NameError(f'Pollutant "{c}" not found in lexicon!'))

                if pol_name in level_norm.keys():
                    d = level_norm[pol_name]
                    for lv in list(d.keys()):
                        if verbose: print(f"-------- {val} ? {d[lv]}")
                        if val >= d[lv]:
                            level = list(d.keys())[list(d.values()).index(d[lv])]

                col_levels.update({c: level})
                if verbose: print(f"{i} {pol_name}: {val} --> {level}")

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
            print(f"{WARNING_TEXT_CONFIG['blue']}No matching! Equivalent closest pollutant name found is {pollutant}{WARNING_TEXT_CONFIG['off']}\n")
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
                            intv_top=None, intv_base=None, thickness='Thickness', query=True):
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
        if bh_name is not None:  # and bh_name in df.columns:  # hum... !!!
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

            intervals = intervals_from_dataframe(tmp, attributes, symbols, thickness,
                                                 intv_top, intv_base)
            if len(intervals) != 0:
                strip.update({bh_id: Striplog(list_of_Intervals=intervals)})
            else:
                print(f"{WARNING_TEXT_CONFIG['red']}"
                      f"\nWARNING : Cannot create a striplog, no interval !"
                      f"{WARNING_TEXT_CONFIG['off']}")

    if len(list(strip.values())) != 0:
        print(f"Summary : {strip.values()}")
        return strip
    else:
        return None


def intervals_from_dataframe(df, attributes=None, symbols=None, thickness=None,
                             intv_top=None, intv_base=None):

    pollutants = list(DEFAULT_POL_LEXICON.abbreviations.keys()) + \
                 list(DEFAULT_POL_LEXICON.abbreviations.values())

    attrib_cdt, attrib_top_cdt = False, False
    thick_cdt, color_cdt = False, False

    if thickness is not None and thickness in list(df.columns):
        thick_cdt = True
    if intv_top is not None and intv_top in list(df.columns):
        attrib_top_cdt = True

    intervals = []
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
                print(f"{WARNING_TEXT_CONFIG['blue']}"
                      f"\nWARNING : No value matches with '{val}' in given lexicon !"
                      f"{WARNING_TEXT_CONFIG['off']}")
            else:
                iv_components.append(Component.from_text(val, lexicon))

            print(val, '\n', Component.from_text(val, lexicon))

        # intervals top, base and thickness processing -----------------------
        if attrib_top_cdt:
            top = df.loc[j, intv_top]
            base = df.loc[j, intv_base]
        elif thick_cdt and not pd.isnull(df.loc[j, thickness]):
            thick = df.loc[j, thickness]
            print(f'enter in thick_cdt : thick= {thick}')
            if j == df.index[0]:
                top = 0
                base = top + thick
            else:
                prev_thick = df.loc[j-1, thickness]
                top += prev_thick
                base = top + thick
        else:
            raise (ValueError("Cannot retrieve or compute interval's top values. provide thickness or top/base values!"))

        warn_msg = 'WARNING : Interval skipped because top/base are null!!'
        if base != 0. or base != 0:
            # add interval only when top and base exist
            if not pd.isnull(top) and not pd.isnull(base):
                intervals = intervals + [Interval(top=top, base=base,
                                        description=val, lexicon=lexicon,
                                        components=iv_components)]
                print(f'interval top={top}, base={base}')
            else:
                print(f"{WARNING_TEXT_CONFIG['green']}{warn_msg}{WARNING_TEXT_CONFIG['off']}")
                # warnings.simplefilter('always', UserWarning)
                #warnings.warn(warn_msg, UserWarning)
        else:
            print(f"{WARNING_TEXT_CONFIG['green']}\n{warn_msg}{WARNING_TEXT_CONFIG['off']}")

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
