import collections.abc
import matplotlib.pyplot as plt
import matplotlib as mpl
from striplog.striplog import StriplogError
import re
from striplog import Lexicon, Legend, Component, Striplog, Interval
import pandas as pd
import numpy as np
from core.orm import BoreholeOrm, PositionOrm
from utils.config import DEFAULT_BOREHOLE_LENGTH, DEFAULT_ATTRIB_VALUE, DEFAULT_BOREHOLE_DIAMETER

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


def legend_from_attributes(attributes):
    """
    Generate a legend dict (attribute:Legend) from a list of attributes string and/or
    tuples of attribute and associated legend

    Parameter
    ------------
    attributes: str

    return
    -----------
    legend_dict : dict
    """
    legend_dict = {}
    for attr in attributes:
        if isinstance(attr, tuple):
            v = [i for i, j in enumerate(attr) if isinstance(j, Legend)][0]
            k = [i for i, j in enumerate(attr) if isinstance(j, str)][0]
            attribute = attr[k]
            legend = attr[v]
        elif isinstance(attr, str):
            attribute = attr
            # default contamination level for pollutants
            legend_text = f"colour,width,component {attr}\n#00FF00, None, VR,\n#FFA500, None, VS,\n#FF0000, None, VI,\n#FFFFFF, None, Inconnu\n"
            legend = Legend.from_csv(text=legend_text)
        else:
            raise(TypeError('Only a list containing strings and/or tuple (attribute, Legend) is allowed !'))

        legend_dict.update({attribute: {'legend': legend}})

    return legend_dict


def get_components(strip):
    """retrieve all components of a Striplog object"""

    return list(set([comp for iv in strip._Striplog__list for comp in iv.components]))


def find_component_from_attrib(intv, attrib, verbose=False):
    """retrieve component index in the components list of an interval, according to the defined attribute

    Parameters
    -------------
    intv : Striplog.Interval
    attrib : attribute key (string) to identify a type of component (e.g: 'lithology')

    Returns
    ------------
    j : index of the first component whose key that matches to attribute
    """
    values = {}
    pos = []
    j = None
    for i in range(len(intv.components)):
        values.update({i: intv.components[i][attrib]})
        if attrib in intv.components[i].keys():
            pos.append(i)
            j = pos[0]  # take the first one if 2 components match for the attribute
            # print(f'j: {j} --> {intv.components[i][attrib]}')
            break
        else:
            j = -1  # not found
            # print(f'j: {j} --> {intv.components[i][attrib]}')
    if j is None:
        raise(StriplogError(f"Actually, empty interval is not allowed"))
    if verbose:
        print(f'find_comp -in- {verbose} | {len(intv.components)} component(s), '
              f'position(s) for {attrib}: {pos}, value(s): {values}')
    return j


def plot_from_striplog(striplog, legend=None, width=1.5, ladder=True, aspect=10, ticks=(1, 10),
        match_only=None, ax=None, return_fig=False, colour=None, cmap='viridis', field=None,
        default=None, style='intervals', label=None, **kwargs):
    """
    Hands-free plotting.

    Args:
        legend (Legend): The Legend to use for colours, etc.
        width (int): The width of the plot, in inches. Default 1.
        ladder (bool): Whether to use widths or not. Default False.
        aspect (int): The aspect ratio of the plot. Default 10.
        ticks (int or tuple): The (minor,major) tick interval for depth.
            Only the major interval is labeled. Default (1,10).
        match_only (list): A list of strings matching the attributes you
            want to compare when plotting.
        ax (ax): A maplotlib axis to plot onto. If you pass this, it will
            be returned. Optional.
        return_fig (bool): Whether or not to return the maplotlib ``fig``
            object. Default False.
        colour (str): Which data field to use for colours.
        cmap (cmap): Matplotlib colourmap. Default ``viridis``.
        **kwargs are passed through to matplotlib's ``patches.Rectangle``.

    Returns:
        None. Unless you specify ``return_fig=True`` or pass in an ``ax``.
    """
    if legend is None:
        legend = Legend.random(striplog.components)

    if style.lower() == 'tops':
        # Make sure width is at least 3 for 'tops' style
        width = max([3, width])

    if ax is None:
        return_ax = False
        fig = plt.figure(figsize=(width, aspect * width))
        ax = fig.add_axes([0.35, 0.05, 0.6, 0.95])
    else:
        return_ax = True

    if (striplog.order == 'none') or (style.lower() == 'points'):
        # Then this is a set of points.
        ax = striplog.plot_points(ax=ax, legend=legend, field=field, **kwargs)
    elif style.lower() == 'field':
        if field is None:
            raise StriplogError('You must provide a field to plot.')
        ax = striplog.plot_field(ax=ax, legend=legend, field=field)
    elif style.lower() == 'tops':
        ax = striplog.plot_tops(ax=ax, legend=legend, field=field)
        ax.set_xticks([])
    else:
        ax = plot_axis_from_striplog(striplog, ax=ax, legend=legend, ladder=ladder, cmap=cmap,
                colour=colour, default=default,default_width=width, width_field=field,
                match_only=kwargs.get('match_only', match_only), **kwargs)

        ax.set_xlim([0, width])
        ax.set_xticks([])

    # Rely on interval order.
    if striplog.order == 'depth':
        upper, lower = striplog.start.z, striplog.stop.z
    else:
        upper, lower = striplog.stop.z, striplog.start.z
    rng = abs(upper - lower)

    ax.set_ylim([lower, upper])

    if label is not None:
        for iv in striplog._Striplog__list:
            plt.text(1.6, iv.middle, iv.components[0][label], ha='left', va='center', size=10)

    # Make sure ticks is a tuple.
    try:
        ticks = tuple(ticks)
    except TypeError:
        ticks = (1, ticks)

    # Avoid MAXTICKS error.
    while rng / ticks[0] > 250:
        mi, ma = 10 * ticks[0], ticks[1]
        if ma <= mi:
            ma = 10 * mi
        ticks = (mi, ma)

    # Carry on plotting...
    minorLocator = mpl.ticker.MultipleLocator(ticks[0])
    ax.yaxis.set_minor_locator(minorLocator)

    majorLocator = mpl.ticker.MultipleLocator(ticks[1])
    majorFormatter = mpl.ticker.FormatStrFormatter('%d')
    ax.yaxis.set_major_locator(majorLocator)
    ax.yaxis.set_major_formatter(majorFormatter)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.yaxis.set_ticks_position('left')
    ax.get_yaxis().set_tick_params(which='both', direction='out')

    # Optional title.
    title = getattr(striplog, 'title', None)
    if title is not None:
        ax.set_title(title)

    ax.patch.set_alpha(0)

    if return_ax:
        return ax
    elif return_fig:
        return fig
    else:
        return


def plot_axis_from_striplog(striplog, ax, legend, ladder=False, default_width=1,
        match_only=None, colour=None, colour_function=None, width_field=None,
        cmap=None, default=None, verbose=False,  **kwargs):
    """
    Plotting, but only the Rectangles. You have to set up the figure.
    Returns a matplotlib axis object.

    Args:
        ax (axis): The matplotlib axis to plot into.
        legend (Legend): The Legend to use for colours, etc.
        ladder (bool): Whether to use widths or not. Default False.
        default_width (int): A width for the plot if not using widths.
            Default 1.
        match_only (list): A list of strings matching the attributes you
            want to compare when plotting.
        colour (str): Which data field to use for colours.
        cmap (cmap): Matplotlib colourmap. Default ``viridis``.
        default (float): The default (null) value.
        width_field (str): The field to use for the width of the patches.
        **kwargs are passed through to matplotlib's ``patches.Rectangle``.

    Returns:
        axis: The matplotlib.pyplot axis.
    """
    default_c = None
    patches = []

    for iv in striplog.intervals:
        origin = (0, iv.top.z)
        j = find_component_from_attrib(iv, match_only[0])
        if verbose:
            print(f'\nplot_axis_from_striplog | comp_index: {j}, match:{match_only},'
                  f' intv: {iv.components}')

        d = legend.get_decor(iv.components[j], match_only=match_only)
        thick = iv.base.z - iv.top.z

        if ladder:
            if width_field is not None:
                w = iv.data.get(width_field, 1)
                w = default_width * w / striplog.max_field(width_field)
                default_c = 'gray'
            elif legend is not None:
                w = d.width or default_width
                try:
                    w = default_width * w / legend.max_width
                except:
                    w = default_width
        else:
            w = default_width

        # Allow override of lw
        this_patch_kwargs = kwargs.copy()
        lw = this_patch_kwargs.pop('lw', 0)
        ec = this_patch_kwargs.pop('ec', 'k')
        fc = this_patch_kwargs.pop('fc', None) or default_c or d.colour

        if colour is None:
            rect = mpl.patches.Rectangle(origin, w, thick, fc=fc, lw=lw, hatch=d.hatch, 
                                         ec=ec,  # edgecolour for hatching 
                                         **this_patch_kwargs)
            ax.add_patch(rect)
        else:
            rect = mpl.patches.Rectangle(origin, w, thick, lw=lw, ec=ec, **this_patch_kwargs)
            patches.append(rect)

    if colour is not None:
        cmap = cmap or 'viridis'
        p = mpl.collections.PatchCollection(patches, cmap=cmap, lw=lw)
        p.set_array(striplog.get_data(colour, colour_function, default=default))
        ax.add_collection(p)
        cb = plt.colorbar(p)
        cb.outline.set_linewidth(0)

    return ax


def striplog_from_dataframe(df, bh_name, attributes, symbols=None, iv_top=None, iv_base=None,
                            thickness='Thickness', use_default=False, query=True):
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
        Legend and Lexicon to use for attributes

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
            print(f"|__ID:\'{bh_id}\'")
            bh_list.append(bh_id)
            if query:
                selection = df['ID'] == f"{bh_id}"  # f'ID=="{bh_id}"'
                tmp = df[selection].copy()  # divide to work faster ;)
                tmp.reset_index(drop=True, inplace=True)
            else:
                tmp = df

            intervals = []
            for j in tmp.index:
                # lithology processing -------------------------------------------

                iv_components = []
                for attrib in attributes:
                    val = tmp.loc[j, attrib]
                    lexicon = symbols[attrib.lower()]['lexicon']
                    if Component.from_text(val, lexicon) == Component({}):  # empty component !
                        print(f"Error : No value matching with '{val}' in given lexicon")
                    else:
                        iv_components.append(Component.from_text(val, lexicon))
                print(iv_components)

                # length processing -----------------------------------------------
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


def striplog_from_df(df, attrib_cols, bh_name=None, attrib_top_col=None, attrib_base_col=None,
                     thick_col=None ,color_col=None, lexicon=None, use_default=True,
                     verbose=False, query=True):
    """
    creates a Striplog object from a dataframe

    Parameters
    ----------
    df : Pandas.DataFrame
        dataframe that contains boreholes data
    bh_name: str
        Borehole name (or ID)
    attrib_cols : str, list
        dataframe column that contains lithology or description text (default:None)

    thick_col : str
        dataframe column that contains lithology thickness (default:None)

    lexicon : striplog.Lexicon
        A vocabulary for parsing lithological or stratigraphic descriptions
        (set to Lexicon.default() if lexicon is None)

    Returns
    -------
    strip : dict of striplog objects

    """
    attrib_cdt, attrib_top_cdt, attrib_base_cdt = False, False, False
    thick_cdt, color_cdt = False, False

    if attrib_cols is not None:
        if not isinstance(attrib_cols, list):
            attrib_cols = [attrib_cols]  # convert to a list
        for attrib_col in attrib_cols:
            if attrib_col not in list(df.columns):
                raise(NameError(f"{attrib_col} is not in the dataframe columns"))

    if thick_col is not None and thick_col in list(df.columns):
        thick_cdt = True
    if attrib_top_col is not None and attrib_top_col in list(df.columns):
        attrib_top_cdt = True
    if attrib_base_col is not None and attrib_base_col in list(df.columns):
        attrib_base_cdt = True
    if color_col is not None and color_col in list(df.columns):
        color_cdt = True

    if lexicon is None:
        lexicon = Lexicon.default()
    elif not isinstance(lexicon, Lexicon):
        raise (TypeError(f"Must provide a lexicon, not '{type(lexicon)}'"))

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
                # if litho_cdt and color_cdt :  # to use color in description
                # litho = f"{tmp.loc[j, litho_col]} {tmp.loc[j, color_col]}"

                attrib_values = tmp.loc[j, attrib_cols]  # values for each columns of interest

                # create components from lithological description
                val = ' '.join(attrib_values)
                if Component.from_text(val, lexicon) == Component({}):  # empty component !
                    print(f"Error : No value matching with '{val}' in given lexicon")
                    if use_default:
                        print(f"Warning : ++ interval's component replaced by default ('{DEFAULT_ATTRIB_VALUE}')")
                        val = DEFAULT_ATTRIB_VALUE
                        component = Component.from_text(val, Lexicon.default())
                else:
                    component = Component.from_text(val, lexicon)

                    print(component)
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
                if attrib_top_cdt:
                    top = tmp.loc[j, attrib_top_col]
                elif thick_cdt:
                    if j == tmp.index[0]:
                        top = 0
                    else:
                        top += tmp.loc[ j -1, thick_col]
                else:
                    raise(ValueError('Cannot retrieve or compute top values. provide thickness values! '))

                if attrib_base_cdt:
                    base = tmp.loc[j, attrib_base_col]
                else:
                    base = top + thick

                if base != 0.:
                    intervals = intervals + [Interval(top=top, base=base, description= val,
                                                      components=[component], lexicon=lexicon)]

            if len(intervals) != 0:
                strip.update({bh_id: Striplog(list_of_Intervals=intervals)})
            else:
                print(f"Error : -- Cannot create a striplog, no interval (length or base = 0)")

    print(f"Summary : {list(strip.values())}")

    return strip


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


def boreholes_from_dataframe(df, x=None, y=None, z=None, symbols=None, attributes=None,
                             diameter='Diameter', thickness='Length',  iv_top=None,
                             iv_base=None, verbose=False, use_default=True):
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
    boreholes = []
    components = []
    comp_id = 0  # component id
    component_dict = {}
    link_dict = {}  # link between intervals and components (<-> junction table)
    df_id = 0  # dataframe id

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
            boreholes.append(BoreholeOrm(id=bh_name))
            interval_number = 0

            bh_selection = df['ID'] == f"{bh_name}"
            tmp = df[bh_selection].copy()
            tmp.reset_index(drop=True, inplace=True)
            strip = striplog_from_dataframe(df=tmp, bh_name=bh_name, attributes=attributes, symbols=symbols,
                                            iv_top=iv_top, iv_base=iv_base, thickness=thickness,
                                            use_default=use_default, query=False)
            for v in strip.values():
                for c in get_components(v):
                    # print('color:', c.colour)
                    if c not in component_dict.keys():
                        component_dict.update({c: comp_id})
                        comp_id += 1
                    print(f'comp: {c}, id: {comp_id}')
                d = {}

                # ORM processing
                for interval in v:
                    top = PositionOrm(id=pos_id, upper=row['Z'] - interval.top.upper,
                                      middle=row['Z'] - interval.top.middle,
                                      lower=row['Z'] - interval.top.lower,
                                      x=row['X'], y=row['Y']
                                      )

                    base = PositionOrm(id=pos_id + 1, upper=row['Z'] - interval.base.upper,
                                       middle=row['Z'] - interval.base.middle,
                                       lower=row['Z'] - interval.base.lower,
                                       x=row['X'], y=row['Y']
                                       )

                    d.update({int_id: {'description': interval.description,
                                       'interval_number': interval_number,
                                       'top': top, 'base': base}
                              })

                    for idx in interval.components:
                        if idx != Component({}):
                            print(f'comp_dict: {component_dict}')
                            link_dict.update({(int_id, component_dict[idx]): {'extra_data': ''}})

                    interval_number += 1
                    int_id += 1
                    pos_id += 2

                if verbose:
                    print(f'{d}\n')
                if bh_idx < len(boreholes):
                    boreholes[bh_idx].intervals_values = d
                    boreholes[bh_idx].length = tmp[thickness].cumsum().max()
                    if diam[bh_idx] is not None and not pd.isnull(diam[bh_idx]):
                        boreholes[bh_idx].diameter = tmp[diameter][0]
                    else:
                        boreholes[bh_idx].diameter = DEFAULT_BOREHOLE_DIAMETER

                bh_idx += 1

        else:
            pass

        components = {v: k for k, v in component_dict.items()}

    print(f"\nEnd of the process : {len(bh_id_list)} unique ID found")

    return boreholes, components, link_dict


def boreholes_from_files(boreholes_dict=None, x=None, y=None, z=None,
                         diam_field='Diameter', thick_field='Length', color_field='Color',
                         litho_field=None, litho_top_field=None, litho_base_field=None,
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

    z : list of float
        Z coordinates

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

    if boreholes_dict is None:
        print("Error! Borehole dictionary not given.")

    # ------------------ argument is a dict of files ---------------------------------------
    if isinstance(boreholes_dict, dict):
        while (boreholes_dict is not None) and bh_id < len(boreholes_dict):
            print(f'\nFile {bh_id} processing...\n================================')
            for bh, filename in boreholes_dict.items():
                interval_number = 0
                boreholes.append(BoreholeOrm(id=bh))
                strip = striplog_from_text_file(filename)

                for c in strip.components:
                    if c not in component_dict.keys():
                        component_dict.update({c: comp_id})
                        comp_id += 1

                d = {}

                for interval in strip:
                    top = PositionOrm(id=pos_id, upper=z[bh_id] - interval.top.upper,
                                      middle=z[bh_id] - interval.top.middle,
                                      lower=z[bh_id] - interval.top.lower,
                                      x=x[bh_id], y=y[bh_id])

                    base = PositionOrm(id=pos_id + 1, upper=z[bh_id] - interval.base.upper,
                                       middle=z[bh_id] - interval.base.middle,
                                       lower=z[bh_id] - interval.base.lower,
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
                    strip = striplog_from_text_file(filename, lexicon)
                else:
                    strip = None

                for c in strip.components:
                    if c not in component_dict.keys():
                        component_dict.update({c: comp_id})
                        comp_id += 1
                d = {}
                for interval in strip:
                    top = PositionOrm(id=pos_id, upper=z[bh_id] - interval.top.upper,
                                      middle=z[bh_id] - interval.top.middle,
                                      lower=z[bh_id] - interval.top.lower,
                                      x=x[bh_id], y=y[bh_id])

                    base = PositionOrm(id=pos_id + 1, upper=z[bh_id] - interval.base.upper,
                                       middle=z[bh_id] - interval.base.middle,
                                       lower=z[bh_id] - interval.base.lower,
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

            if diam_field in boreholes_dict[df_id].columns:
                diam = boreholes_dict[df_id][diam_field]
            else:
                print(f'Warning : -- No borehole diameter, default is used (diameter={DEFAULT_BOREHOLE_DIAMETER})')
                diam = pd.Series([DEFAULT_BOREHOLE_DIAMETER] * len(boreholes_dict[df_id]))

            for idx, row in boreholes_dict[df_id].iterrows():
                bh_name = row['ID']

                if bh_name not in bh_id_list:
                    bh_id_list.append(bh_name)
                    boreholes.append(BoreholeOrm(id=bh_name))
                    interval_number = 0

                    bh_selection = boreholes_dict[df_id]['ID'] == f"{bh_name}"
                    tmp = boreholes_dict[df_id][bh_selection].copy()
                    tmp.reset_index(drop=True, inplace=True)
                    strip = striplog_from_df(df=tmp, bh_name=bh_name, attrib_cols=litho_field,
                                             attrib_top_col=litho_top_field, attrib_base_col=litho_base_field,
                                             thick_col=thick_field, color_col=color_field,
                                             use_default=use_default, verbose=verbose, lexicon=lexicon,
                                             query=False)

                    for v in strip.values():
                        for c in v.components:
                            # print('color:', c.colour)
                            if c not in component_dict.keys():
                                component_dict.update({c: comp_id})
                                comp_id += 1

                        d = {}

                        # ORM processing
                        for interval in v:
                            top = PositionOrm(id=pos_id, upper=row['Z'] - interval.top.upper,
                                              middle=row['Z'] - interval.top.middle,
                                              lower=row['Z'] - interval.top.lower,
                                              x=row['X'], y=row['Y']
                                              )

                            base = PositionOrm(id=pos_id + 1, upper=row['Z'] - interval.base.upper,
                                               middle=row['Z'] - interval.base.middle,
                                               lower=row['Z'] - interval.base.lower,
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
