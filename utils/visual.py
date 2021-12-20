from copy import deepcopy
import matplotlib.pyplot as plt
import matplotlib as mpl
import omf
import pandas as pd
from matplotlib import colors as mcolors
from striplog.striplog import StriplogError
import re
from striplog import Legend, Component
import numpy as np
from striplog.utils import hex_to_rgb
import core.visual as cv
from utils.config import WORDS_WITH_S, DEFAULT_POL_LEXICON
from utils.lexicon_memoris import LEG_CONTAMINATION_LEV


def striplog_legend_to_omf_legend(legend, alpha=1.):
    """
    Creates an omf.data.Legend object from a striplog.Legend object

    Parameters
    -----------
    legend : striplog.Legend object
    alpha : float

    Returns
    --------
    omf.data.Legend
        Legends to be used with DataMap indices
    ListedColormap(new_colors)
        matplotlib colormap
    """
    # TODO: we must add colors as a parameter to allow to change colors style

    omf_legend = []
    new_colors = []  # new_colors in RGBA format

    for i in legend:
        omf_legend.append(i.colour)  # i.colour is in RGB format
        new_colors.append(np.hstack([np.array(hex_to_rgb(i.colour)) / 255, np.array([alpha])]))

    return omf.data.Legend(description='', name='', values=omf.data.ColorArray(omf_legend)), mcolors.ListedColormap(
        new_colors)


def build_bh3d_legend_cmap(bh3d_list, legend_dict, repr_attrib_list=['lithology'], width=3,
                           compute_all=False, update_bh3d_legend=False,
                           update_given_legend=False, verbose=False):
    """
    Build legends and colormaps based on attribute values in boreholes

    Parameters
    -------------
    bh3d_list: List of Borehole3D objects

    legend_dict: Dict of dict
        A dictionary that contains default legend (and cmap) for each attribute.
        Legend must be a Striplog.Legend object (and cmap, a Matplotlib.Colors.ListedColormap object).
        e.g: legend_dict={"attribute1": {"legend":Striplog.Legend}}

    repr_attrib_list: List of str
        specifies the attributes for which the legend and cmap should be computed

    compute_all: Bool (default=False)
        compute legend and cmap for all attributes (keys) found in legend_dict.
        If True, no need to set 'repr_attrib_list'

    update_bh3d_legend: Bool (default=False)
        If True, updates each borehole legend, cmap

    update_given_legend: Bool (default=False)
        If True, updates legend, cmap, unique values for each attribute in the given legend_dict

    Returns
    --------
    synth_legend_cmap : dict of synthetic legend, cmap and unique values basis on all boreholes

    detail_legend_cmap : dict of legend, cmap and unique values for each borehole
    """

    if not isinstance(repr_attrib_list, list):
        raise (TypeError('repr_attribute must be a list of attributes present in the interval'))
    if not isinstance(legend_dict, dict):
        raise (TypeError('legend must be a dict of attributes (key) and legend (and cmap) dict (value).'))

    if compute_all:  # compute legend, cmap, unique_values for each key in the legend dict
        repr_attrib_list = list(legend_dict.keys())

    detail_legend_cmap = {}  # contains legend/cmap dicts for each borehole
    synth_legend_cmap = {}  # synthetic legend/cmap dict basis on all boreholes data

    for attr in repr_attrib_list:
        attr = attr.lower()
        if verbose:
            print(f'BLCMap for : {attr}\n---------------------------------------')

        r = attr.replace('(', '\(').replace(')', '\)')
        reg_attr = re.compile("^{:s}$".format(r), flags=re.I)
        rgx = list(filter(reg_attr.match, DEFAULT_POL_LEXICON.pollutants))
        # print('-->', attr, '--- regex:', rgx)

        if rgx and legend_dict[attr]['legend'] is None:
            # create default legend for pollutant
            legend_dict[attr]['legend'] = Legend.from_csv(text=LEG_CONTAMINATION_LEV.format(attr))

        if not isinstance(legend_dict[attr]['legend'], Legend):
            raise (TypeError('legend must be a Striplog.Legend object. Check the docstring!'))

        global_uniq_attrib_val = []  # [DEFAULT_ATTRIB_VALUE]  # all unique values for each attribute
        synth_decors = {}  # dict of decors for building all boreholes synthetic legend/cmap per attribute
        for bh3d in bh3d_list:
            if verbose:
                print('|-> BH:', bh3d.name)
            if not isinstance(bh3d, cv.Borehole3D):
                raise (TypeError('Element in borehole3d must be a Borehole3D object'))

            legend_copy = deepcopy(legend_dict[attr]['legend'])
            bh3d_uniq_attrib_val = []  # unique attribute values for each borehole
            for intv in bh3d.intervals:
                j = find_component_from_attrib(intv, attr, verbose=verbose)
                if j == -1:  # add default component if none found
                    # intv.components.append(Component({attr: DEFAULT_ATTRIB_VALUE}))
                    pass
                if intv.components[j][attr] is not None:
                    if intv.components[j][attr] not in WORDS_WITH_S:
                        comp_v = intv.components[j][attr].rstrip('s')  # remove ending 's'
                        intv.components[j] = Component({attr: comp_v})  # overwrite component
                    if intv.components[j][attr] not in bh3d_uniq_attrib_val:
                        bh3d_uniq_attrib_val.append(intv.components[j][attr])
                    if intv.components[j][attr] not in global_uniq_attrib_val:
                        global_uniq_attrib_val.append(intv.components[j][attr])
            if verbose:
                print(f'\nBLCMap - unique/bh3d: {bh3d_uniq_attrib_val}, unique_proj: {global_uniq_attrib_val}')

            decors = {}  # dict of decors for building each attribute legend/cmap
            if len(bh3d_uniq_attrib_val)>0:
                for i in range((len(legend_copy))):
                    leg_value = legend_copy[i].component[attr]
                    reg = re.compile("^{:s}$".format(leg_value), flags=re.I)
                    reg_value = list(filter(reg.match, bh3d_uniq_attrib_val))  # value that matches

                    if len(reg_value) > 0:
                        # force matching to plot
                        legend_copy[i].component = Component({attr: reg_value[0]})
                        legend_copy[i].width = width
                        # use interval order to obtain correct plot legend order
                        if bh3d_uniq_attrib_val.index(reg_value[0]) not in decors.keys():
                            decors.update({bh3d_uniq_attrib_val.index(reg_value[0]): legend_copy[i]})
                        # add decors to build synthetic legend with all boreholes attributes values
                        if global_uniq_attrib_val.index(reg_value[0]) not in synth_decors.keys():
                            synth_decors.update({global_uniq_attrib_val.index(reg_value[0]): legend_copy[i]})

            if verbose:
                print('\nBLCMap | Decors:', decors)
            _legend = Legend([decors[k] for k in sorted(decors.keys())])
            _cmap = striplog_legend_to_omf_legend(_legend)[1]

            if update_bh3d_legend:
                bh3d.legend_dict[attr] = {'legend': _legend, 'cmap': _cmap,
                                          'values': bh3d_uniq_attrib_val}

            if bh3d.name not in detail_legend_cmap.keys():
                detail_legend_cmap[bh3d.name] = {}
            detail_legend_cmap[bh3d.name][attr] = {'legend': _legend, 'cmap': _cmap,
                                                   'values': bh3d_uniq_attrib_val}

        glob_legend = Legend([synth_decors[k] for k in sorted(synth_decors.keys())])
        glob_cmap = striplog_legend_to_omf_legend(glob_legend)[1]

        synth_legend_cmap[attr] = {'legend': glob_legend, 'cmap': glob_cmap,
                                   'values': global_uniq_attrib_val}
        if update_given_legend:
            legend_dict[attr] = synth_legend_cmap[attr]

    return synth_legend_cmap, detail_legend_cmap


def legend_from_attributes(attributes):
    """
    Generate a legend dictionary ({attribute:Legend}) from a list of attributes string and/or
    tuples of attribute and associated legend

    Parameter
    ------------
    attributes: list

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
        elif isinstance(attr, str):  # to generate a legend for a pollutant
            abbr_names = list(DEFAULT_POL_LEXICON.abbreviations.keys())
            abbr_names_lowercase = [n.lower() for n in abbr_names]
            full_names = list(DEFAULT_POL_LEXICON.abbreviations.values())

            if attr in abbr_names or attr.lower() in abbr_names_lowercase:
                attr = DEFAULT_POL_LEXICON.abbreviations[attr].lower()
            elif attr.lower() in full_names:
                attr = attr.lower()

            attribute = attr
            # default contamination level for pollutants
            # legend_text = f"colour,width,component {attr}\n#9CB39C, None, VR,\n#00FF00, None, VS,\n#FFA500, None, VI,\n#FF0000, None, VI_sup,\n#FFFFFF, None, Inconnu\n"
            legend = Legend.from_csv(text=LEG_CONTAMINATION_LEV.format(attr))
            # legend = Legend.from_csv(text=legend_text)
        else:
            raise(TypeError('Only a list containing strings and/or tuple (attribute, Legend) is allowed !'))

        legend_dict.update({attribute: {'legend': legend}})

    return legend_dict


def get_components(strip):
    """retrieve all components of a Striplog object"""
    return list(pd.unique([comp for iv in strip._Striplog__list for comp in iv.components]))


def find_component_from_attrib(intv, attrib, verbose=False):
    """retrieve the first component index in the components list of an interval, according to the defined attribute

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
        if attrib.lower() in intv.components[i].keys():
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


def plot_from_striplog(striplog, legend=None, width=1.5, ladder=True, aspect=10,
        ticks=(1, 10), match_only=None, ax=None, return_fig=False, colour=None,
        cmap='viridis', field=None, default=None, style='intervals',
        label=None, **kwargs):
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
    print(ax.get_label())
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

