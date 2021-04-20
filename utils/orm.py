from striplog import Position, Component, Interval, Lexicon
from lexicon.Lexicon_FR_updated import LEXICON


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
        lexic = Lexicon(LEXICON)
    else:
        lexic = Lexicon(lexicon)

    interval_list, depth = [], []
    for i in bh.intervals.values():
        top = Position(upper=i.top.upper, middle=i.top.middle, lower=i.top.lower, x=i.top.x, y=i.top.y)
        base = Position(upper=i.base.upper, middle=i.base.middle, lower=i.base.lower, x=i.top.x, y=i.top.y)
        comp = Component.from_text(i.description, lexicon=lexic)
        interval_list.append(Interval(top=top, base=base, description=i.description, components=[comp]))
        depth.append(i.base.middle) 
    return interval_list, max(depth)
