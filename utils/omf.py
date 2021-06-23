from striplog.utils import hex_to_rgb


def striplog_legend_to_omf_legend(legend, alpha=1.):
    """
    Creates an omf.data.Legend object from a striplog.Legend object

    Parameters
    -----------
    legend : striplog.Legend object

    Returns
    --------
    omf.data.Legend
        Legends to be used with DataMap indices

    ListedColormap(new_colors)
        matplotlib colormap
    """
    # we must add colors as a parameter to allow to change colors style

    omf_legend = []
    new_colors = []  # new_colors in RGBA format
    # new_colors = [np.array([0.9, 0.9, 0.9, alpha])]
    # omf_legend.append(legend[0].colour)
    # n = 0

    for i in legend:
        # n += 1
        omf_legend.append(i.colour)  # i.colour is in RGB format
        new_colors.append(np.hstack([np.array(hex_to_rgb(i.colour)) / 255, np.array([alpha])]))
        # print(n, omf_legend[n-1], hex_to_rgb(i.colour), '---', new_colors[n-1])
    # new_colors.append(np.array([0.9, 0.9, 0.9, 1.]))
    # omf_legend.append(legend[0].colour)
    return omf.data.Legend(description='', name='', values=omf.data.ColorArray(omf_legend)), mcolors.ListedColormap(
        new_colors)


