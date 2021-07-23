from striplog import Position, Component, Interval
from core.visual import Borehole3D


def create_bh3d_from_bhorm(bh_orm, legend_dict=None, verbose=False):
    """
    Create a Borehole3D object from a BoreholeOrm object

    parameters
    ------------
    bh_orm: BoreholeOrm object
    legend_dict: dict of legend per attribute
    verbose: bool

    returns
    --------
    bh_3d : Borehole3D object
    """
    list_of_intervals, bh_orm.length = get_interval_list(bh_orm)
    if verbose:
        print(bh_orm.id, " added")

    bh_3d = Borehole3D(name=bh_orm.id, diam=bh_orm.diameter, length=bh_orm.length,
                      legend_dict=legend_dict, intervals=list_of_intervals)
    return bh_3d


def get_interval_list(bh_orm):
    """create a list of interval from a list of boreholeORM ojects
    
    Parameters
    -------------
    bh_orm: list
        list of boreholeORM

    Returns
    ---------
    interval_list: list
                   list of Interval objects
                   
    """

    interval_list, depth = [], []
    for i in bh_orm.intervals.values():
        top = Position(upper=i.top.upper, middle=i.top.middle, lower=i.top.lower, x=i.top.x, y=i.top.y)
        base = Position(upper=i.base.upper, middle=i.base.middle, lower=i.base.lower, x=i.top.x, y=i.top.y)

        intv_comp_list = []
        for c in i.description.split(', '):
            intv_comp_list.append(Component(eval(c)))

        interval_list.append(Interval(top=top, base=base, description=i.description,
                                      components=intv_comp_list))
        depth.append(i.base.middle)
    return interval_list, max(depth)
