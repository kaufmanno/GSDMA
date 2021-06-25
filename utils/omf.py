from striplog.utils import hex_to_rgb
from striplog import Legend, Decor
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


def build_bh3d_legend(borehole3d, default_legend, attribute='lithology', hatches=None, colors=None, width=3):
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

    if (colors is not None and colors not in ['random', 'default']) \
            and not isinstance(colors, list):
        raise(TypeError('colors must be a list of colors in str, html or RGB(A) codes'))

    if (hatches is not None and hatches not in ['random', 'default']) \
            and not isinstance(hatches, list):
        raise(TypeError('hatches must be a list of hatches in str'))

    # default values
    if hatches == 'random' or hatches is None:
        def_hatches = ['+', 'x', '.', 's', '*', 'b', 'c', 'v', '/', 't']

    if colors == 'random':
        def_colors = [i.colour for i in Legend.default()] + list(mcolors.CSS4_COLORS.values())

    list_of_decors, hatches_used = [], []

    if borehole3d._components is None:
        components = [i.components[0] for i in borehole3d.intervals]  # don't use self.components !
    else:
        components = borehole3d._components
    i = 0  # increment to retrieve given colors or hatches

    for comp in components:
        # print('---------------\n', components)
        if hasattr(comp, attribute):
            comp_attr_val = comp[attribute]
            for leg in default_legend:
                leg_attr_val = leg.component[attribute]
                reg = re.compile("^{:s}$".format(leg_attr_val), flags=re.I).match(comp_attr_val)

                if reg:  # attribute value found
                    # ------------ color processing --------------------
                    if colors is None:
                        if hasattr(comp, 'colour'):
                            c = comp.colour
                        else:
                            c = leg.colour
                    elif colors == 'default':
                        c = leg.colour
                    elif colors == 'random':
                        c = random.sample(def_colors, 1)[0]
                    elif colors is not None:
                        c = colors[i]

                    # ------------ hatch processing ------------------------
                    if hatches is None:
                        if hasattr(comp, 'hatch'):
                            h = comp.hatch
                        elif leg.hatch is not None:
                            h = leg.hatch
                    elif hatches == 'default':
                        h = leg.hatch
                    elif hatches == 'random':
                        h = random.sample(def_hatches, 1)[0]
                        while h in hatches_used:
                            if len(hatches_used) >= len(def_hatches):
                                h = ''.join(random.sample(hatches_used, 2))
                            elif len(hatches_used) >= 2 * len(def_hatches):
                                h = ''.join(random.sample(hatches_used, 3))
                            else:
                                h = random.sample(hatches, 1)[0]

                        hatches_used.append(h)
                    elif hatches is not None:
                        h = hatches[i]
                    else:
                        h = None
        else:
            # print(f"All components : {components}")
            # print(f"Empty component: {i}-{comp}")
            raise (TypeError('Cannot create a legend for empty component'))
            # TODO : allow empty component (define a lacking lithology type)

        i += 1

        decor = Decor({'color': c, 'hatch': h, 'component': comp, 'width': width})
        list_of_decors.append(decor)

    return Legend(list_of_decors)