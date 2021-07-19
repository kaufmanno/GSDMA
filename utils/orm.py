from striplog import Position, Component, Interval, Lexicon


def get_interval_list(bhOrm):
    """create a list of interval from a list of boreholeORM ojects
    
    Parameters
    ----------
    bhOrm: list
        list of boreholeORM

    Returns
    -------
    interval_list: list
                   list of Interval objects
                   
    """

    interval_list, depth = [], []
    for i in bhOrm.intervals.values():
        top = Position(upper=i.top.upper, middle=i.top.middle, lower=i.top.lower, x=i.top.x, y=i.top.y)
        base = Position(upper=i.base.upper, middle=i.base.middle, lower=i.base.lower, x=i.top.x, y=i.top.y)

        intv_comp_list = []
        for c in i.description.split(', '):
            intv_comp_list.append(Component(eval(c)))

        interval_list.append(Interval(top=top, base=base, description=i.description,
                                      components=intv_comp_list))
        depth.append(i.base.middle)
    return interval_list, max(depth)
