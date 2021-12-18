import re
import pandas as pd
from striplog import Component, Interval, Striplog, Lexicon
from utils.config import DEFAULT_LITHO_LEXICON, DEFAULT_POL_LEXICON, WARNING_TEXT_CONFIG
from utils.lexicon_memoris import LEX_SOIL_NORM, LEX_WATER_NORM
from difflib import get_close_matches


def get_contam_level_from_value(value, pollutant, sample_type=None, pol_lexicon=None,
                                verbose=False):
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
        if len(pollutant) > 0:
            pollutant = pollutant[0]
            print(f"{WARNING_TEXT_CONFIG['blue']}No matching! Equivalent closest pollutant name found is {pollutant}{WARNING_TEXT_CONFIG['off']}\n")
        else:
            raise (NameError(f'Pollutant "{pollutant}" not found in lexicon!'))

    # if sample_type is not None:
    #     if re.search('sol|soil', sample_type, re.I):
    #         level_norm = LEX_SOIL_NORM
    #     elif re.search('eau|water', sample_type, re.I):
    #         level_norm = LEX_WATER_NORM
    #     else:
    #         raise(NameError(f"Sample type must be in {SAMP_TYPE_KW[:-1]}, not {sample_type}"))
    # else:  # suppose sample type is 'soil'
    #     level_norm = LEX_SOIL_NORM

    level_norm = LEX_SOIL_NORM # TODO: FIX this

    unit = level_norm['unit']

    if pol_name in level_norm['pollutants'].keys():
        d = level_norm['pollutants'][pol_name]
        if pd.isnull(value):
            level = 'Inconnu'
        elif value <= d['VR']:
            level = 'VR'
        elif value <= d['VS']:
            level = 'VS'
        elif value <= d['VI']:
            level = 'VI'
        else:
            level = 'VI_'

    if verbose: print(f"{pol_name}: {value} {unit} --> {level}")

    return pol_name, level, unit


def striplog_from_dataframe(df, bh_name, attributes, id_col='ID', symbols=None,
                            top_col=None, base_col=None, desc_col=None, thick_col=None,
                            intv_type_col=None, sample_type_col=None, sample_id_col=None,
                            query=True, verbose=False):
    """
    creates a Striplog object from a dataframe

    Parameters
    ------------
    df : Pandas.DataFrame
        Dataframe that contains borehole intervals data

    bh_name: str
        Borehole name (or ID)

    attributes: list
        Attributes to use for creating components

    symbols : dict of striplog.Lexicon, striplog.Legend objects
        Legend and/or Lexicon to use for attributes

    top_col : str
        Dataframe column that contains interval top

    base_col : str
        Dataframe column that contains interval base

    thick_col : str
        Dataframe column that contains lithology thickness (default:None)

    query : bool
        Work on a restricted copy of df by querying this dataframe first

    Returns
    -------
    strip : dict of striplog objects

    """

    for attrib_col in attributes:
        if not re.search('litho', attrib_col, re.I) and attrib_col not in list(df.columns):
            raise (NameError(f"{attrib_col} is not in the dataframe columns"))

    strip = {}
    bh_list = []

    for j in df.index:
        if bh_name is not None:
            bh_id = bh_name
        else:
            bh_id = df.loc[j, id_col]

        if bh_id in bh_list:
            continue
        else:
            print(f"\n\033[0;40;47m BH_ID: \'{bh_id}\'\033[0;0;0m")
            bh_list.append(bh_id)
            if query:
                selection = df[id_col] == f"{bh_id}"  # f'ID=="{bh_id}"'
                tmp = df[selection].copy()  # divide to work faster ;)
                tmp.reset_index(drop=True, inplace=True)
            else:
                tmp = df

            intervals = intervals_from_dataframe(tmp, attributes=attributes,
                                                 symbols=symbols, thick_col=thick_col,
                                                 top_col=top_col, base_col=base_col,
                                                 desc_col=desc_col,
                                                 sample_id_col=sample_id_col,
                                                 sample_type_col=sample_type_col,
                                                 intv_type_col=intv_type_col,
                                                 verbose=verbose)
            if intervals:
                strip.update({bh_id: Striplog(list_of_Intervals=intervals)})
            else:
                print(f"{WARNING_TEXT_CONFIG['red']}"
                      f"\nWARNING : Cannot create a striplog, no interval !"
                      f"{WARNING_TEXT_CONFIG['off']}")

        if list(strip.values()):
            print(f"\033[1;40;47m Summary : {strip}\033[0;0;0m")
            return strip
        else:
            return None


def intervals_from_dataframe(df, attributes=None, symbols=None, thick_col=None,
                             top_col=None, base_col=None, desc_col=None,
                             intv_type_col=None, sample_type_col=None, sample_id_col=None,
                             verbose=False):

    pollutants = list(DEFAULT_POL_LEXICON.abbreviations.keys()) + \
                 list(DEFAULT_POL_LEXICON.abbreviations.values())

    attrib_cdt, attrib_top_cdt = False, False
    thick_cdt, color_cdt, samp_type_cdt = False, False, False

    if thick_col is not None and thick_col in list(df.columns):
        thick_cdt = True
    if top_col is not None and top_col in list(df.columns):
        attrib_top_cdt = True
    if sample_type_col is not None and sample_type_col in list(df.columns):
        samp_type_cdt = True

    intervals = []
    top, base, thick, val = 0, 0, 0, 0
    for j in df.index:
        samp_name = None
        samp_type = None
        iv_type = df.loc[j, intv_type_col]
        if re.search('litho', iv_type, re.I):
            create_litho = True
        else:
            create_litho = False

        if not create_litho and samp_type_cdt:
            samp_type = df.loc[j, sample_type_col]
            if sample_id_col is not None and not pd.isnull(df.loc[j, sample_id_col]):
                samp_name = df.loc[j, sample_id_col]

        # components processing -------------------------------------------
        iv_components = []
        for attrib in attributes:
            num_val, unit = None, None
            if re.search('litho', attrib, re.I):
                coi = desc_col  # column of interest
            else:
                coi = attrib
            val = df.loc[j, coi]

            # retrieve contamination level
            if attrib in pollutants or attrib.lower() in pollutants:
                if isinstance(val, str):
                    val = val.replace(',', '.')
                num_val = float(val)
                attrib, val, unit = get_contam_level_from_value(num_val, attrib, samp_type)

            if verbose:
                print(f"**CONTAM_VAL** {attrib}: {num_val} {unit} <--> {val}")
            # set correct lexicon
            if attrib.lower() in DEFAULT_POL_LEXICON.pollutants:
                # default lexicon for contaminant
                lexicon = Lexicon({attrib.lower(): DEFAULT_POL_LEXICON.levels})
            elif attrib not in symbols.keys() and attrib.lower() in symbols.keys():
                lexicon = symbols[attrib.lower()]['lexicon']
            else:
                lexicon = symbols[attrib]['lexicon']

            # component creation
            if pd.isnull(val):
                val = ''  # avoid NaN errors with component.from_text()
            if Component.from_text(val, lexicon) == Component({}):
                if val != '':
                    print(f"{WARNING_TEXT_CONFIG['red']}"
                          f"\nWARNING : No value matches with '{val}' in given lexicon !"
                          f"{WARNING_TEXT_CONFIG['off']}")
            elif create_litho and val == 'Inconnu':
                pass  # don't create lithology in this case
            else:
                comp = Component.from_text(val, lexicon)
                if num_val is not None:
                    if pd.isnull(num_val): num_val = 'NaN'  # np.nan
                    comp['concentration'] = num_val
                    if unit is not None: comp['unit'] = unit
                iv_components.append(comp)

        # intervals top, base and thickness processing -----------------------
        if attrib_top_cdt:
            top = df.loc[j, top_col]
            base = df.loc[j, base_col]
        elif thick_cdt and not pd.isnull(df.loc[j, thick_col]):
            thick = df.loc[j, thick_col]
            print(f'enter in thick_cdt : thick= {thick}')
            if j == df.index[0]:
                top = 0
                base = top + thick
            else:
                prev_thick = df.loc[j - 1, thick_col]
                top += prev_thick
                base = top + thick
        else:
            raise (ValueError("Cannot retrieve or compute interval's top values. provide thickness or top/base values!"))

        warn_msg = 'WARNING : Interval skipped because top/base are null!!'
        error_intv = True
        if base != 0. or base != 0:
            # only add interval when top and base exist
            if not pd.isnull(top) and not pd.isnull(base):
                error_intv = False
                print(f'{j}- Interval top={top}, base={base}')
                if samp_name is None:
                    intervals.append(Interval(top=top, base=base, components=iv_components))
                else:
                    intervals.append(Interval(top=top, base=base, components=iv_components,
                                              data={'sample_ID': samp_name,
                                                    'sample_type': samp_type}))
        if error_intv:
            print(f"{WARNING_TEXT_CONFIG['red']}\n{warn_msg}{WARNING_TEXT_CONFIG['off']}")

        print(f" - Interval components: {iv_components}\n")

    return intervals


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
