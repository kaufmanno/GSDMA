import pandas as pd
import re
from striplog import Position, Component, Interval
from core.orm import BoreholeOrm, PositionOrm
from core.visual import Borehole3D
from utils.config import DEFAULT_BOREHOLE_DIAMETER, DEFAULT_BOREHOLE_LENGTH, DEFAULT_POL_LEXICON,\
    WARNING_TEXT_CONFIG, WORDS_WITH_S, NOT_EXIST

from utils.utils import striplog_from_dataframe
from utils.visual import get_components


def create_bh3d_from_bhorm(bh_orm, legend_dict=None, attribute=None, verbose=False):
    """
    Create a Borehole3D object from a BoreholeOrm object

    parameters
    ------------
    bh_orm : BoreholeOrm object

    legend_dict : dict of legend per attribute

    verbose : bool

    returns
    --------
    Borehole3D
        a Borehole3D object
    """
    intervals, length = get_interval_list(bh_orm, attribute=attribute)

    bh_3d = Borehole3D(name=bh_orm.id, date=bh_orm.date, diam=bh_orm.diameter, repr_attribute=attribute,
                       length=length, legend_dict=legend_dict, intervals=intervals)
    if verbose:
        print(bh_orm.id, " added")
    return bh_3d


def component_orm_to_component(comp_orm):
    return Component(eval(comp_orm.description))


def interval_orm_to_interval(intv_orm):
    top = Position(upper=intv_orm.top.upper, middle=intv_orm.top.middle, lower=intv_orm.top.lower,
                   x=intv_orm.top.x, y=intv_orm.top.y)
    base = Position(upper=intv_orm.base.upper, middle=intv_orm.base.middle, lower=intv_orm.base.lower,
                    x=intv_orm.top.x, y=intv_orm.top.y)

    intv_comp_list = [component_orm_to_component(c_orm) for c_orm in intv_orm.components]

    intv = Interval(top=top, base=base, description=intv_orm.description, components=intv_comp_list)
    return intv


def get_interval_list(bh_orm, attribute=None):
    """create a list of interval from a boreholeORM object

    Parameters
    -------------
    bh_orm: boreholeOrm object
        A BoreholeOrm object from which intervals matching the attribute will be listed
    attribute: str
        The attribute of components to search in components associated with the borehole intervals
    Returns
    ---------
    interval_list: list
        List of Interval objects for each type of interval
    max_depth: float
        Borehole's maximum depth for all intervals

    """

    max_depth = None
    interval_list = []
    for int_id, intv_orm in bh_orm.intervals.items():
        for c in intv_orm.components:
            interval_attributes = [i for i in eval(c.description).keys()]
            if (attribute in interval_attributes) or (attribute is None):
                interval_list.append(interval_orm_to_interval(intv_orm))
            if 'borehole_type' in interval_attributes:
                max_depth = intv_orm.base.middle
    assert max_depth is not None
    return interval_list, max_depth


def orm_boreholes_from_dataframe(data_list, symbols=None, attributes=None, id_col='ID',
                                 diameter_col='Diameter', default_z=None, date_col='Date',
                                 sample_type_col=None, skip_cols=None, verbose=False):
    """ Creates a list of BoreholeORM objects from a dataframe

    Parameters
    ----------
    data_list: list
        A list of pandas.DataFrame containing borehole intervals data
    symbols: dict
        A dict e.g. {attribute_1: {'legend': striplog.Legend, 'lexicon': striplog.Lexicon}, ...}
    attributes : list
        List of dataframe's columns of interest, linked to attributes to represent like 'lithology'
    verbose : Bool
        allow verbose option if set = True

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
    link_intv_comp_dict = {}  # link between intervals and components (<-> junction table)
    contam_names = list(DEFAULT_POL_LEXICON.abbreviations.values())

    if skip_cols is None:
        skip_cols = []

    # data concatenation
    final_df = pd.DataFrame()
    last_index = None
    for dataf in data_list:
        assert isinstance(dataf, pd.DataFrame)
        df = dataf.copy()

        # rename certain columns' name
        for col in df.columns:
            if col not in skip_cols:
                if re.search('top|toit', col, re.I):
                    df.rename(columns={col: 'Top_intv'}, inplace=True)
                elif re.search('base|mur|assise', col, re.I):
                    df.rename(columns={col: 'Base_intv'}, inplace=True)
                elif re.search('thick|epais', col, re.I):
                    df.rename(columns={col: 'Thick_intv'}, inplace=True)
                elif re.search('descr', col, re.I):
                    df.rename(columns={col: 'Descr_intv'}, inplace=True)

        if last_index is not None:
            df.index = range(last_index, last_index + len(df))

        final_df = final_df.append(df, ignore_index=True)
        last_index = len(final_df)

    # data exploitation
    print(f'\nData Processing...\n================================')
    bh_id_list = []  #
    bh_counter = 0
    bh_idx = 0  # borehole index in the current dataframe

    if diameter_col not in final_df.columns:
        print(f"{WARNING_TEXT_CONFIG['blue']}"
              f"Warning : -- No borehole diameter column found or check given column's name.\n"
              f'To continue, default diameter column has been created with value: '
              f'{DEFAULT_BOREHOLE_DIAMETER} [m]{WARNING_TEXT_CONFIG["off"]}')
        final_df[diameter_col] = DEFAULT_BOREHOLE_DIAMETER

    top_col, base_col, desc_col = 'Top_intv', 'Base_intv', 'Descr_intv'
    thick_col = 'Thick_intv'

    for idx, row in final_df.iterrows():
        bh_name = row[id_col]
        if date_col not in final_df.columns:
            bh_date = None
        else:
            bh_date = row[date_col]

        if bh_name not in bh_id_list:
            bh_id_list.append(bh_name)
            bh_selection = final_df[id_col] == f"{bh_name}"
            tmp = final_df[bh_selection].copy()
            tmp.reset_index(drop=True, inplace=True)
            striplog_dict = striplog_from_dataframe(df=tmp, bh_name=bh_name,
                                                    attributes=attributes, symbols=symbols,
                                                    id_col=id_col, thick_col=thick_col,
                                                    top_col=top_col, base_col=base_col,
                                                    sample_type_col=sample_type_col,
                                                    desc_col=desc_col,
                                                    query=False, verbose=verbose)

            if striplog_dict is not None:
                bh_counter += 1
                interval_number = 0
                boreholes_orm.append(BoreholeOrm(id=bh_name, date=bh_date))

                for strip in striplog_dict.values():
                    for c in get_components(strip):
                        c_key = list(c.keys())[0]
                        c_type = 'pollutant' if c_key in contam_names else 'lithology'
                        c_val = c_key if c_type == 'pollutant' else c[c_key]
                        # c_lev = c[c_key] if c_type == 'pollutant' else None

                        # remove 's' for plural words
                        if c_val not in WORDS_WITH_S:
                            c_val = c_val.rstrip('s')
                        c = Component({'type': c_type, 'value': c_val})
                        if c not in component_dict.keys():
                            component_dict.update({c: comp_id})
                            comp_id += 1

                    # ORM processing
                    interval_dict = {}
                    use_def_z = False
                    for intv in strip:
                        if default_z is not None and (row['Z'] is None or pd.isnull(row['Z'])):
                            if isinstance(default_z, int) or isinstance(default_z, float):
                                z_val = default_z  # average Z coordinate of boreholes heads
                                if not use_def_z:
                                    print(f"{WARNING_TEXT_CONFIG['blue']}"
                                          f"WARNING: Borehole's Z coordinate not found, use"
                                          f" default one: {default_z} [m]"
                                          f"{WARNING_TEXT_CONFIG['off']}")
                                    use_def_z = True
                            else:
                                raise(TypeError("default_Z value must be int or float"))
                        else:
                            z_val = row['Z']

                        top = PositionOrm(id=pos_id, upper=z_val - intv.top.upper,
                                          middle=z_val - intv.top.middle,
                                          lower=z_val - intv.top.lower,
                                          x=row['X'], y=row['Y']
                                          )

                        base = PositionOrm(id=pos_id + 1, upper=z_val - intv.base.upper,
                                           middle=z_val - intv.base.middle,
                                           lower=z_val - intv.base.lower,
                                           x=row['X'], y=row['Y']
                                           )

                        desc = '; '.join([c.json() for c in intv.components])

                        interval_dict.update({int_id: {'top': top, 'base': base,
                                                'interval_number': interval_number,
                                                'description': desc}})

                        for cp in intv.components:
                            if cp != Component({}):
                                cp_key = list(cp.keys())[0]
                                cp_type = 'pollutant' if cp_key in contam_names else 'lithology'
                                cp_val = cp_key if cp_type == 'pollutant' else cp[cp_key]
                                cp_lev = cp[cp_key] if cp_type == 'pollutant' else None
                                unit = cp['unit'] if hasattr(cp, 'unit') else None
                                pol_conc = cp['concentration'] if hasattr(cp, 'concentration') else None
                                # remove 's' for plural words
                                if cp_val not in WORDS_WITH_S:
                                    cp_val = cp_val.rstrip('s')
                                cp = Component({'type': cp_type, 'value': cp_val})

                                link_intv_comp_dict.update({(int_id, component_dict[cp]):
                                    {'extra_data': str({'level': cp_lev,
                                                        'concentration': pol_conc,
                                                        'unit': unit})}
                                                            })

                        interval_number += 1
                        int_id += 1
                        pos_id += 2

                    if bh_idx < len(boreholes_orm):
                        boreholes_orm[bh_idx].intervals_values = interval_dict
                        if thick_col in final_df.columns:
                            boreholes_orm[bh_idx].length = tmp[thick_col].cumsum().max()
                        elif base_col in final_df.columns:
                            boreholes_orm[bh_idx].length = tmp[base_col].max()

                        diam_val = tmp[diameter_col][0]
                        if diam_val is not None and not pd.isnull(diam_val):
                            boreholes_orm[bh_idx].diameter = diam_val
                        else:
                            boreholes_orm[bh_idx].diameter = DEFAULT_BOREHOLE_DIAMETER
                            print(f'No diameter value found, using default: '
                                  f'{DEFAULT_BOREHOLE_DIAMETER}')

                bh_idx += 1

        components_dict = {v: k for k, v in component_dict.items()}

    print(f"\nEnd of the process : {bh_counter} boreholes created successfully")

    return boreholes_orm, components_dict, link_intv_comp_dict
