import re
import pandas as pd
from striplog import Component, Interval, Striplog, Lexicon

from utils.config import DEFAULT_BOREHOLE_LENGTH, DEFAULT_CONTAM_LEVELS
from utils.lexicon.lexicon_memoris import pollutants_memoris


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


def striplog_from_dataframe(df, bh_name, attributes, symbols=None, intv_top=None,
                            intv_base=None, thickness='Thickness', use_default=False,
                            query=True):
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

    attrib_cdt, attrib_top_cdt, attrib_base_cdt = False, False, False
    thick_cdt, color_cdt = False, False

    for attrib_col in attributes:
        if attrib_col not in list(df.columns):
            raise (NameError(f"{attrib_col} is not in the dataframe columns"))

    if thickness is not None and thickness in list(df.columns):
        thick_cdt = True
    if intv_top is not None and intv_top in list(df.columns):
        attrib_top_cdt = True
    if intv_base is not None and intv_base in list(df.columns):
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
                    top = tmp.loc[j, intv_top]
                elif thick_cdt:
                    if j == tmp.index[0]:
                        top = 0
                    else:
                        top += tmp.loc[j - 1, thickness]
                else:
                    raise (ValueError('Cannot retrieve or compute top values. provide thickness values! '))

                if attrib_base_cdt:
                    base = tmp.loc[j, intv_base]
                else:
                    base = top + thick

                if base != 0.:
                    intervals = intervals + [Interval(top=top, base=base, description=val,
                                                      components=iv_components,
                                                      lexicon=lexicon)]

            if len(intervals) != 0:
                strip.update({bh_id: Striplog(list_of_Intervals=intervals)})
            else:
                print(f"Error : -- Cannot create a striplog, no interval (length or base = 0)")

    print(f"Summary : {list(strip.values())}")

    return strip


