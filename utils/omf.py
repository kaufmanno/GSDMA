from striplog.utils import hex_to_rgb
from striplog import Legend, Decor
from utils.lexicon.lexicon_fr import COLOURS
import numpy as np
import omf
import random
import re
import matplotlib.colors as mcolors
import core.omf


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
    # new_colors = [np.array([0.9, 0.9, 0.9, alpha])]
    # omf_legend.append(legend[0].colour)

    for i in legend:
        omf_legend.append(i.colour)  # i.colour is in RGB format
        new_colors.append(np.hstack([np.array(hex_to_rgb(i.colour)) / 255, np.array([alpha])]))
    # new_colors.append(np.array([0.9, 0.9, 0.9, 1.]))
    # omf_legend.append(legend[0].colour)
    return omf.data.Legend(description='', name='', values=omf.data.ColorArray(omf_legend)), \
        mcolors.ListedColormap(new_colors)


def build_bh3d_legend(borehole3d, default_legend, attribute='lithology', width=3):
    """
    Build a legend based on lithologies in the borehole

    Parameters
    -------------
    borehole3d: Borehole3D object
    default_legend: striplog.Legend object
        A legend that contains default lithologies and their associated colors / hatches
    Returns
    --------
    striplog.Legend
    """

    # given values test
    if not isinstance(borehole3d, core.omf.Borehole3D):
        raise(TypeError('borehole3d must be a Borehole3D object'))

    if not isinstance(default_legend, Legend):
        raise(TypeError('legend must be a Striplog.Legend object'))

    list_of_decors, hatches_used = [], []

    if borehole3d._components is None:
        components = [i.components[0] for i in borehole3d.intervals]  # don't use self.components !
    else:
        components = borehole3d._components

    for comp in components:
        if hasattr(comp, attribute):
            comp_attr_val = comp[attribute]
            for leg in default_legend:
                leg_attr_val = leg.component[attribute]
                reg = re.compile("^{:s}$".format(leg_attr_val), flags=re.I).match(comp_attr_val)

                if reg:  # attribute value found
                    c = leg.colour

                    # try:
                    #     c = COLOURS[col.lower()].lower()
                    # except(Exception):
                    #     c = col.lower()

                    h = leg.hatch
        else:
            raise (TypeError('Cannot create a legend for empty component'))
            # TODO : allow empty component (define a lacking lithology type)

        decor = Decor({'color': c, 'hatch': h, 'component': comp, 'width': width})
        list_of_decors.append(decor)

    return Legend(list_of_decors)