from importlib import import_module
import re
import pandas as pd
from os import walk, path, makedirs


def desc_process(df, desc_col):
    """
    Extract descriptions from a dataframe

    Parameters
    -------------
    df : pandas.Dataframe
    desc_col : str
        common description column name in the dataframes

    returns
    --------
    desc : list
        a list of words found in dataframe description column
    """

    kw, desc = [], []

    for i in range(len(df)):
        if not pd.isnull(df.loc[i, desc_col]):
            kw = kw + df.loc[i, desc_col].split(' ')
    kw = list(set(kw))

    for i in range(len(kw)):
        if len(kw[i]) > 2 and not re.search('\d.*', kw[i]):  # to eliminate all 'one letter words' and all numbers
            wlist = [re.sub(r"^/|\.|l'|d'", "", kw[i]).rstrip('[.|...|,|;|(|)|?]').lstrip('?|(|+').replace(',…', "")]
            desc = desc + wlist
    desc = list(set(desc))

    return desc


def modifier_process(desc, lexicon_file=None, kind=None):
    """ extract lithology and modifier keywords from a list of description keywords
    Parameters
    ------------
    desc : list
        list of description keywords
    lexicon_file : str
        filename of a lexicon (filetype :*.py)
    kind : str
        kind of keywords ('lithology', 'mofifier', ...)

    Returns
    ---------
    words: list
        a list of modifier keywords
    litho : list
        a list of lithology keywords
    """

    if lexicon_file is None:
        lexicon_file = import_module('utils.defaults.basic_lexicon_FR')
        lexicon = lexicon_file.LEXICON
    elif isinstance(lexicon_file, str):
        lexicon_file = import_module(lexicon_file)
        lexicon = lexicon_file.LEXICON
    else:
        lexicon = lexicon_file

    lith, md = '', ''
    mdf, litho = [], []
    words, skip_words = [], []
    flag = re.IGNORECASE

    rc = re.compile('(?:-)?(\w+eu(?:x|se|ses))')

    match = filter(rc.findall, desc)
    for i in match:
        for j in re.split('-|/', i):
            # retrieve modifier
            if not re.search(r'\w+o$', j):
                md = re.sub(r'eu(x|se|ses)$', 'eu(?:x|se|ses)?', j)

            # retrieve lithology
            if re.search(r'(velo)$', j):
                # line to create regex keyword
                lith = re.sub(r'(velo)$', 'vier(?:s)?', j)
                # lith = re.sub(r'(velo)$', 'vier', j) # gravelo -> gravier
            elif re.search(r'(ono)$', j):
                lith = re.sub(r'o$', '(?:s)?', j)
                # lith = re.sub(r'o$', '', j) # limono -> limon
            elif re.search(r'o$', j):
                lith = re.sub(r'(o)$', 'e(?:s)?', j)
                # lith = re.sub(r'(o)$', 'e', j) # sablo -> sable

            if md not in mdf and md != '':
                mdf = mdf + [md]
            if lith not in litho and lith != '':
                litho = litho + [lith]

    for w in lexicon['lithology']:  # to manage modifiers
        w = re.sub('(e|es)$', '', w.replace('(?:s)?', ''))
        # print(w)
        r = re.compile("^{:s}\w?eu".format(w), flags=flag)
        words = words + list(set(filter(r.findall, mdf)))

    skip_words = list(set(mdf) - set(words))

    if len(skip_words) > 0 and kind == 'modifier':
        log_file = f"lexicon/Lexicon_Log_{kind}.py"

        path_dir = re.search('(.+/).+\.(?:py)', log_file).group(1)
        if not path.exists(path_dir):
            makedirs(path_dir)

        with open(log_file, 'w+') as f:
            f.write('"""This file contains all keywords skipped during lexicon building processes"""')
            f.write(f'\n\n#================== {kind.upper()} LOG ================================ \n')
            f.write(f'SKIPPED_WORDS = {skip_words}')

    if len(skip_words) != 0 and kind == 'modifier':
        print(
            f"|>>> Processing for 'modifier' : {len(words)} keywords extracted and "
            f"{len(skip_words)} words skipped : \ncheck in \'{log_file}\' ! ")
    elif kind == 'lithology':
        pass
        # print(f"|>>> Processing for {kind} : {len(litho)} keywords extracted")
    else:
        print(f"|>>> Processing for {kind} : {len(words)} keywords extracted")

    # print('\n',mdf_lex, '\n', litho,'\n')

    return words, litho


def update_lexicon_db(save_lexicon, lexicon_db=None, colour_db=None):
    if save_lexicon is None:
        save_lexicon = 'lexicon/Lexicon_FR_updated.py'
    else:
        save_lexicon = f"{save_lexicon}"

    path_dir = re.search('(.+/).+\.(?:py)', save_lexicon).group(1)
    if not path.exists(path_dir):
        makedirs(path_dir)

    with open(save_lexicon, 'w+') as f:
        f.write(f'"""\nDefinition de mots clés pour les descriptions de cuttings de forages.\n' +
                ':copyright: 2021  Y. N\'DEPO & O. Kaufmann \n"""')

        f.write(f'\n\n#==================== LEXIQUE ================================ \n')
        f.write(f'LEXICON = {lexicon_db}')

        f.write(f'\n\n#======================= COULEURS ============================ \n')
        f.write(f'COLORS = {colour_db}')

    print(f'\nThe lexicon have been updated and saved in {save_lexicon} !')


def extract_keyword(df, kind_list, desc_col, lexicon, kind_def, kw_com):
    # lexicon['splitters']

    flag = re.IGNORECASE

    lex = {'lithology': [], 'material': [], 'modifier': [], 'colour': []}
    # generated from the processing

    com_lex = {'lithology': lexicon['lithology'], 'material': lexicon['material'],
               'modifier': lexicon['modifier'], 'colour': lexicon['colour']}
    # manually built to contain default values

    desc = desc_process(df, desc_col)

    if kind_list == ['all']:
        kind_list = kind_def

    for kind in kind_list:
        filter_lex, words, skip_words = [], [], []
        tmp_lex = lex[kind]
        if len(kw_com) == 0:
            tmp_com = com_lex[kind]
        else:
            tmp_com = kw_com[kind]
        # print(tmp_com)
        if kind not in kind_def:
            print("Parameter *kind* must be 'lithology' or compatible str : see docstring !")

        for v in tmp_com:
            if kind == 'colour':
                v = re.sub('(e|t)$', '', v)
                r = re.compile("{:s}(e|es|s)?([-|/]\w+)?([â|a]tre)?$".format(v), flags=flag)
                tmp_lex = tmp_lex + list(filter(r.findall, desc))
            elif kind == 'material':
                v = re.sub('(e|es)$', '', v)
                r = re.compile("^{:s}(e|es)?(-)*(.^/)*$".format(v), flags=flag)
                tmp_lex = tmp_lex + list(filter(r.findall, desc))
            elif kind == 'lithology':
                v = re.sub('(e|es)$', '', v)
                r = re.compile("^{:s}(e|es)?([-|/]\w+)*$".format(v), flags=flag)

                match = filter(r.findall, desc)
                for i in match:
                    for j in re.split('-|/', i):
                        j = j.capitalize()
                        # j = re.sub(r'o$','(?:s)?',j)
                        if j in tmp_com and j != '':
                            words.append(j)
                        elif j not in tmp_com:
                            skip_words.append(j)

        words = list(set(words))
        skip_words = list(set(skip_words))

        if len(skip_words) > 0:
            log_file = f"lexicon/Lexicon_Log_{kind}.py"

            path_dir = re.search('(.+/).+\.(?:py)', log_file).group(1)
            if not path.exists(path_dir):
                makedirs(path_dir)

            with open(log_file, 'w+') as f:
                f.write('"""This file contains all keywords skipped during lexicon building processes"""')
                f.write(f'\n\n#================== {kind.upper()} LOG ================================ \n')
                f.write(f'SKIPPED_WORDS = {skip_words}')

        if kind == 'lithology':
            tmp_lex = tmp_lex + words
            # lithologies from modifier_process()
            words, litho = modifier_process(desc, lexicon, kind)
            tmp_lex = list(set(tmp_lex + litho))

        if kind == 'modifier':
            words, litho = modifier_process(desc, lexicon, kind)
            tmp_lex = words

        for w in tmp_lex:
            w = w.capitalize()
            if kind == 'lithology':
                if not re.search('mon$', w):
                    w = re.sub('o$', 'e(?:s)?', w)
                if not re.search('ss$', w):  # avoid words like 'gneiss'
                    w = re.sub('s$', '(?:s)?', w)

            if w not in filter_lex:
                filter_lex.append(w)

        lex[kind] = lex[kind] + filter_lex

        # print(f"{len(desc)} total keywords found")
        if kind != 'modifier':
            print(f"|>>> Processing for '{kind}' : {len(filter_lex)} keywords extracted")

    return lex, desc


def build_lexicon(fdir=None, kind_list=None, df_dict=None, desc_col='Description',
                  kw_com={}, lexicon_file=None, save_lexicon=None):
    """
    Generate a lexicon from lithological descriptions in dataframes

    Parameters
    ------------
    fdir: str
        dir from which CSV filenames with 'litho' (also in subdirs) will be used to
         collect lithological description data
    kind_list : list
        list of lexicon thematic ['lithology','material','colour']. Default is 'None'
    df_dict : dict
        a dict of dataframes retrieved from files in dir
    desc_col : str
        name of the dataframe column that contains descriptions
    kw_com: dict
        dict of common keywords to be considered for each lexicon thematic
    lexicon_file: str
        filename of a lexicon file (*.py). Default is None.
    save_lexicon: str
        filename to save the lexicon built. Default is None.

    Returns
    --------
        lexicon_db: dict
            new words keywords (grouped by thematic) found in description
        all_desc: list
            all description keywords
    """
    if lexicon_file is None:
        lexicon_mod = import_module('utils.defaults.basic_lexicon_FR')
    else:
        lexicon_mod = import_module(lexicon_file)

    lexicon_db = lexicon_mod.LEXICON

    assert isinstance(fdir, str), "Expected a str for parameter *fdir*!"
    assert isinstance(kind_list, list), "Expected a list for parameter *kind_list*!"
    assert isinstance(desc_col, str), "Expected a str for parameter *desc_col*!"
    assert isinstance(kw_com, dict), "Expected a dict for parameter *kw_com*!"

    kind_def = ['lithology', 'material', 'modifier', 'colour']
    flist, df_list, all_desc = [], [], []

    if fdir is not None:
        for p, dirs, files in walk(fdir):
            for f in files:
                if f[0] != '.' and re.compile(r".+[L|l]ith.+\.csv").match(f) and f is not None:
                    p = p + "/" + f
                    flist.append('{}'.format(p))
                    df_list.append(pd.read_csv('{}'.format(p)))

        df_dict = dict(list(enumerate(df_list)))  # same -> dict(zip(keys, values)) where key = range(len(df_list))

    if not isinstance(df_dict, type(None)):
        for nb, df in df_dict.items():
            print(f"\nkeywords extraction and filtering from \'{flist[nb].replace(fdir, '')}\'")
            new_lexicon, desc = extract_keyword(df, kind_list, desc_col, lexicon_db, kind_def, kw_com)

            all_desc = all_desc + desc
            new_litho_lex = []

            for kind in kind_def:
                lexicon_db[kind] = list(set(lexicon_db[kind] + new_lexicon[kind]))
                if kind == 'lithology':
                    for w in lexicon_db[kind]:
                        if not re.search('(x|ss|\)s|\)\?)$', w) and w not in new_litho_lex:
                            new_litho_lex.append(w.capitalize() + '(?:s)?')
                        elif w not in new_litho_lex:
                            new_litho_lex.append(w.capitalize())

                    lexicon_db[kind] = new_litho_lex
                # print(f'{kind} : {lexicon_db[kind]}')

            update_lexicon_db(save_lexicon, lexicon_db)  # Lexicon_db update

    return lexicon_db, all_desc
