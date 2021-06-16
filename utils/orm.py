from striplog import Position, Component, Interval, Lexicon


def get_interval_list(bh, lexicon=None):
    """create a list of interval from a list of boreholeORM ojects
    
    Parameters
    ----------
    bh: list
        list of boreholeORM
    lexicon : dict
        lexicon to retrieve lithological information from descriptions

    Returns
    -------
    interval_list: list
                   list of Interval objects
                   
    """
    if lexicon is None :
        lexicon = Lexicon.default()
    elif not isinstance(lexicon, Lexicon):
        raise (TypeError(f"Must provide a lexicon, not '{type(lexicon)}'"))

    interval_list, depth = [], []
    for i in bh.intervals.values():
        top = Position(upper=i.top.upper, middle=i.top.middle, lower=i.top.lower, x=i.top.x, y=i.top.y)
        base = Position(upper=i.base.upper, middle=i.base.middle, lower=i.base.lower, x=i.top.x, y=i.top.y)
        comp = Component.from_text(i.description, lexicon=lexicon)
        interval_list.append(Interval(top=top, base=base, description=i.description, components=[comp]))
        depth.append(i.base.middle) 
    return interval_list, max(depth)
