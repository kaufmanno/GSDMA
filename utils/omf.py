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

    return omf.data.Legend(description='', name='', values=omf.data.ColorArray(omf_legend)), mcolors.ListedColormap(new_colors)


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
        raise(TypeError('repr_attribute must be a list of attributes present in the component'))
    if not isinstance(legend_dict, dict):
        raise(TypeError('legend must be a dict of attributes (key) and legend (and cmap) dict (value).'))

    if compute_all:  # compute legend, cmap, unique_values for each key in the legend dict
        repr_attrib_list = list(legend_dict.keys())

    detail_legend_cmap = {}  # contains legend/cmap dicts for each borehole
    synth_legend_cmap = {}  # synthetic legend/cmap dict basis on all boreholes data

    if verbose:
        print(f'given legend_dict : {legend_dict} \n')

    for attr in repr_attrib_list:
        if verbose:
            print(attr, '\n---------------------')
        if not isinstance(legend_dict[attr]['legend'], Legend):
            raise (TypeError('legend must be a Striplog.Legend object. Check the docstring!'))

        global_uniq_attrib_val = []  # all unique values for each attribute
        synth_decors = {}  # dict of decors for building all boreholes synthetic legend/cmap per attribute
        for bh3d in bh3d_list:
            if verbose:
                print('|-', bh3d.name)
            if not isinstance(bh3d, core.omf.Borehole3D):
                raise(TypeError('Element in borehole3d must be a Borehole3D object'))

            legend_copy = deepcopy(legend_dict[attr]['legend'])
            bh3d_uniq_attrib_val = []  # unique attribute values for each borehole
            decors = {}  # dict of decors for building each attribute legend/cmap
            for intv in bh3d.intervals:
                if intv.components[0][attr] is None:
                    intv.components[0][attr] = DEFAULT_ATTRIB_VALUE  # set to default value
                if intv.components[0][attr] not in bh3d_uniq_attrib_val:
                    bh3d_uniq_attrib_val.append(intv.components[0][attr])
                if intv.components[0][attr] not in global_uniq_attrib_val:
                    global_uniq_attrib_val.append(intv.components[0][attr])
                # print('++++++++++++', bh3d.name, '++++++++++++++++++++++++++++')
                # print(bh3d_uniq_attrib_val, '\n', global_uniq_attrib_values)

            for i in range((len(legend_copy))):
                leg_value = legend_copy[i].component[attr]
                reg = re.compile("^{:s}$".format(leg_value), flags=re.I)
                reg_value = list(filter(reg.match, bh3d_uniq_attrib_val))  # find value that matches

                if len(reg_value) > 0:
                    # force matching to plot
                    legend_copy[i].component = Component({attr: reg_value[0]})
                    legend_copy[i].width = width
                    # use interval order to obtain correct plot legend order
                    decors.update({bh3d_uniq_attrib_val.index(reg_value[0]): legend_copy[i]})
                    # add decors to build synthetic legend with all boreholes attributes values
                    if global_uniq_attrib_val.index(reg_value[0]) not in synth_decors.keys():
                        synth_decors.update({global_uniq_attrib_val.index(reg_value[0]): legend_copy[i]})
            # print('\n', attr, '\n-----------------\n', decors)
            _legend = Legend([decors[k] for k in sorted(decors.keys())])
            _cmap = striplog_legend_to_omf_legend(_legend)[1]

            if update_bh3d_legend:
                bh3d.legend_dict[attr] = {'legend': _legend, 'cmap': _cmap, 'values': bh3d_uniq_attrib_val}

            if bh3d.name not in detail_legend_cmap.keys():
                detail_legend_cmap[bh3d.name] = {}
            detail_legend_cmap[bh3d.name][attr] = {'legend': _legend, 'cmap': _cmap,
                                               'values': bh3d_uniq_attrib_val}
            if verbose:
                print(' |->', detail_legend_cmap, '\n')

        glob_legend = Legend([synth_decors[k] for k in sorted(synth_decors.keys())])
        # print('\n', attr, '\n-----------------\n', glob_legend)
        glob_cmap = striplog_legend_to_omf_legend(glob_legend)[1]

        synth_legend_cmap[attr] = {'legend': glob_legend, 'cmap': glob_cmap,
                                   'values': global_uniq_attrib_val}
        if update_given_legend:
            legend_dict[attr] = synth_legend_cmap[attr]

    return synth_legend_cmap, detail_legend_cmap
