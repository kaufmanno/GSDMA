import pandas as pd
from striplog import Position, Component, Interval

from core.orm import BoreholeOrm, PositionOrm
from core.visual import Borehole3D
from utils.config import DEFAULT_BOREHOLE_DIAMETER
from utils.utils import striplog_from_dataframe
from utils.visual import get_components


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


def boreholes_from_dataframe(df, symbols=None, attributes=None, intv_top=None,
                             intv_base=None, diameter='Diameter', thickness='Length',
                             verbose=False, use_default=True):
    """ Creates a list of BoreholeORM objects from a dataframe

    Parameters
    ----------
    df: pandas.DataFrame
        A dataframe of borehole intervals

    symbols: dict
        A dict e.g. {attribute_1: {'legend': striplog.Legend, 'lexicon': striplog.Lexicon}, ...}

    attributes : list
        List of dataframe's columns of interest, linked to attributes to represent like 'lithology'

    verbose : Bool
        allow verbose option if set = True

    use_default : Bool
        allow use default when values not available if set = True

    Returns
    -------
    boreholes: list
               boreholes object

    components: dict
                dictionary containing ID and component

    """

    int_id = 0  # interval id
    pos_id = 0  # position id
    boreholes_orm = []
    components_dict = []
    comp_id = 0  # component id
    component_dict = {}
    link_dict = {}  # link between intervals and components (<-> junction table)

    assert isinstance(df, pd.DataFrame)

    print(f'\nDataframe processing...\n================================')
    bh_id_list = []  #
    bh_idx = 0  # borehole index in the current dataframe

    if diameter in df.columns:
        diam = df[diameter]
    else:
        print(f'Warning : -- No borehole diameter, default is used (diameter={DEFAULT_BOREHOLE_DIAMETER})')
        diam = pd.Series([DEFAULT_BOREHOLE_DIAMETER] * len(df))

    for idx, row in df.iterrows():
        bh_name = row['ID']

        if bh_name not in bh_id_list:
            bh_id_list.append(bh_name)
            boreholes_orm.append(BoreholeOrm(id=bh_name))
            interval_number = 0

            bh_selection = df['ID'] == f"{bh_name}"
            tmp = df[bh_selection].copy()
            tmp.reset_index(drop=True, inplace=True)
            striplog_dict = striplog_from_dataframe(df=tmp, bh_name=bh_name,
                                                    attributes=attributes,
                                                    symbols=symbols, thickness=thickness,
                                                    intv_top=intv_top, intv_base=intv_base,
                                                    use_default=use_default, query=False)
            for strip in striplog_dict.values():
                # print('strip:', v)
                for c in get_components(strip):
                    if c not in component_dict.keys():
                        component_dict.update({c: comp_id})
                        comp_id += 1
                        # comp_id = list(component_dict.keys()).index(c)
                    # print(f'component: {c}, component_id: {comp_id}')

                interval_dict = {}
                # ORM processing
                for intv in strip:
                    top = PositionOrm(id=pos_id, upper=row['Z'] - intv.top.upper,
                                      middle=row['Z'] - intv.top.middle,
                                      lower=row['Z'] - intv.top.lower,
                                      x=row['X'], y=row['Y']
                                      )

                    base = PositionOrm(id=pos_id + 1, upper=row['Z'] - intv.base.upper,
                                       middle=row['Z'] - intv.base.middle,
                                       lower=row['Z'] - intv.base.lower,
                                       x=row['X'], y=row['Y']
                                       )

                    desc = ', '.join([c.json() for c in intv.components])
                    # print('description:', desc)
                    interval_dict.update({int_id: {'description': desc,
                                       'interval_number': interval_number,
                                       'top': top, 'base': base}})

                    for idx in intv.components:
                        if idx != Component({}):
                            if verbose:
                                print(f'comp_dict: {component_dict}')
                            link_dict.update({
                                (int_id, component_dict[idx]): {'extra_data': ''}})

                    interval_number += 1
                    int_id += 1
                    pos_id += 2

                if verbose:
                    print(f'{interval_dict}\n')
                if bh_idx < len(boreholes_orm):
                    boreholes_orm[bh_idx].intervals_values = interval_dict
                    boreholes_orm[bh_idx].length = tmp[thickness].cumsum().max()
                    if diam[bh_idx] is not None and not pd.isnull(diam[bh_idx]):
                        boreholes_orm[bh_idx].diameter = tmp[diameter][0]
                    else:
                        boreholes_orm[bh_idx].diameter = DEFAULT_BOREHOLE_DIAMETER

                bh_idx += 1
        else:
            # already processed
            pass

        components_dict = {v: k for k, v in component_dict.items()}

    print(f"\nEnd of the process : {len(bh_id_list)} unique ID found")

    return boreholes_orm, components_dict, link_dict