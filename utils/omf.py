from striplog.utils import hex_to_rgb
from striplog import Legend, Decor, Component
import numpy as np
import omf
import re
import matplotlib.colors as mcolors
import core.omf
from copy import deepcopy
from utils.config import DEFAULT_ATTRIB_VALUE


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
    # print(new_colors)
    # print(omf_legend)

    return omf.data.Legend(description='', name='', values=omf.data.ColorArray(omf_legend)), \
        mcolors.ListedColormap(new_colors)


def build_bh3d_legend_cmap(bh3d_list, legend_dict, repr_attrib_list=['lithology'], width=3,
                           update_legend=False):
    """
    Build a legend based on lithologies in the borehole

    Parameters
    -------------
    bh3d_list: List of Borehole3D objects
    legend_dict: dict of dict
        A dictionary that contains default legend (and cmap) for each attribute.
        Legend must be a Striplog.Legend object (and cmap, a Matplotlib.Colors.ListedColormap object).
        e.g: legend_dict={"attribute1": {"legend":Striplog.Legend}}

    Returns
    --------
    striplog.Legend
    """

    # given values test
    if not isinstance(repr_attrib_list, list):
        raise(TypeError('repr_attribute must be a list of attributes present in the component'))
    if not isinstance(legend_dict, dict):
        raise(TypeError('legend must be a dict of attributes (key) and legend (and cmap) dict (value).'))

    process_result = {}  # all boreholes legend dicts
    uniq_attrib_values = []  # list of distinct attributes (e.g: lithologies) in project boreholes
    decors = {}  # dict of decors for building a project legend/cmap

    for bh3d in bh3d_list:
        if not isinstance(bh3d, core.omf.Borehole3D):
            raise(TypeError('Element in borehole3d must be a Borehole3D object'))

        for attr in repr_attrib_list:
            # print(attr, '\n', legend_dict[attr].keys())
            if not isinstance(legend_dict[attr]['legend'], Legend):
                raise (TypeError('legend must be a Striplog.Legend object. Check the docstring!'))

            legend_copy = deepcopy(bh3d.legend_dict[attr]['legend'])
            for intv in bh3d.intervals:
                if intv.components[0][attr] is None:
                    intv.components[0][attr] = DEFAULT_ATTRIB_VALUE  # set to default value
                if intv.components[0][attr] not in uniq_attrib_values:
                    uniq_attrib_values.append(intv.components[0][attr])
            # print(bh.name, ":", uniq_attrib_values)

            for i in range((len(legend_copy))):
                leg_value = legend_copy[i].component[attr]
                reg = re.compile("^{:s}$".format(leg_value), flags=re.I)
                reg_value = list(filter(reg.match, uniq_attrib_values))  # find value that matches

                if len(reg_value) > 0:
                    # force matching to plot
                    legend_copy[i].component = Component({attr: reg_value[0]})
                    legend_copy[i].width = width
                    # use interval order to obtain correct plot legend order
                    decors.update({uniq_attrib_values.index(reg_value[0]): legend_copy[i]})

            _decors = [decors[idx] for idx in range(len(decors.values()))]
            _legend = Legend(_decors)
            _cmap = striplog_legend_to_omf_legend(_legend)[1]

            process_result[bh3d.name] = {}
            process_result[bh3d.name][attr] = {'legend': _legend, 'cmap': _cmap,
                                               'values': uniq_attrib_values}

            if update_legend:
                bh3d.legend_dict[attr] = {'legend': _legend, 'cmap': _cmap}

    return process_result
