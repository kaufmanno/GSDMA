import collections.abc
from striplog import Legend
import matplotlib.pyplot as plt
import matplotlib as mpl
from striplog.striplog import StriplogError


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
