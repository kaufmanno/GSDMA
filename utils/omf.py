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


def build_bh3d_legend(borehole3d, legend, repr_attrib='lithology', width=3, update_legend=False):
    """
    Build a legend based on lithologies in the borehole

    Parameters
    -------------
    borehole3d: Borehole3D object
    legend: striplog.Legend object
        A legend that contains default lithologies and their associated colors / hatches
    Returns
    --------
    striplog.Legend
    """

    # given values test
    if not isinstance(legend, Legend):
        raise(TypeError('legend must be a Striplog.Legend object'))

    if not isinstance(borehole3d, core.omf.Borehole3D):
        raise(TypeError('Element in borehole3d must be a Borehole3D object'))

    list_of_decors, hatches_used = [], []

    if borehole3d._components is None:
        components = [i.components[0] for i in borehole3d.intervals]  # don't use self.components !
    else:
        components = borehole3d._components

    # TODO : rewrite below like 'update_legend_cmap()' in project object
    for comp in components:
        if hasattr(comp, repr_attrib):
            comp_attr_val = comp[repr_attrib]
            for leg in legend:
                leg_attr_val = leg.component[repr_attrib]
                if leg_attr_val is None:
                    # legend_copy[i].component[repr_attribute] = DEFAULT_ATTRIB_VALUE
                    # leg_value = DEFAULT_ATTRIB_VALUE
                    pass
                reg = re.compile("^{:s}$".format(leg_attr_val), flags=re.I).match(comp_attr_val)

                if reg:  # attribute value found
                    c = leg.colour
                    h = leg.hatch
        else:
            raise(TypeError('Cannot create a legend for empty component'))
            pass

        decor = Decor({'color': c, 'hatch': h, 'component': comp, 'width': width})
        list_of_decors.append(decor)

    plot_legend = Legend(list_of_decors)
    plot_cmap = striplog_legend_to_omf_legend(plot_legend)[1]

    if update_legend:
        borehole3d.cmap = plot_cmap
        borehole3d.legend = plot_legend

    return plot_legend, plot_cmap