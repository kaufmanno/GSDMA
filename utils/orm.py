from striplog import Position, Component, Interval


def get_interval_list(bh):
    """create a list of interval from a list of boreholeORM ojects
    
    Parameters
    ----------
    bh: list
        list of boreholeORM object
         
    
    Returns
    -------
    interval_list: list
                   list of Interval objects
                   
    """
    interval_list = []
    for i in bh.intervals.values():
        top = Position(upper=i.top.upper, middle=i.top.middle, lower=i.top.lower, x=i.top.x, y=i.top.y)
        base = Position(upper=i.base.upper, middle=i.base.middle, lower=i.base.lower, x=i.top.x, y=i.top.y)
        comp = Component.from_text(i.description)
        interval_list.append(Interval(top=top, base=base, description=i.description, components=[comp]))
    return interval_list
