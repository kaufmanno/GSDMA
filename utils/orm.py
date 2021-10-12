import pandas as pd
from striplog import Position, Component, Interval
from core.orm import BoreholeOrm, PositionOrm, SampleOrm
from core.visual import Borehole3D
from utils.config import DEFAULT_BOREHOLE_DIAMETER
from utils.utils import striplog_from_dataframe, intervals_from_dataframe
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

    bh_3d = Borehole3D(name=bh_orm.id, date=bh_orm.date, diam=bh_orm.diameter,
                       length=bh_orm.length, legend_dict=legend_dict,
                       intervals=list_of_intervals)
    return bh_3d


def get_interval_list(bh_orm):
    """create a list of interval from a list of boreholeORM objects
    
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
        # print(f"\n{i}\n")
        top = Position(upper=i.top.upper, middle=i.top.middle, lower=i.top.lower, x=i.top.x, y=i.top.y)
        base = Position(upper=i.base.upper, middle=i.base.middle, lower=i.base.lower, x=i.top.x, y=i.top.y)

        intv_comp_list = []
        for c in i.description.split(', '):
            intv_comp_list.append(Component(eval(c)))

        interval_list.append(Interval(top=top, base=base, description=i.description,
                                      components=intv_comp_list))
        depth.append(i.base.middle)
    return interval_list, max(depth)


def boreholes_from_dataframe(df, symbols=None, attributes=None, id_col='ID',
                             intv_top=None, intv_base=None, diameter='Diameter',
                             thickness=None, average_z=None, date_col='Date',
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
    link_intv_comp_dict = {}  # link between intervals and components (<-> junction table)

    assert isinstance(df, pd.DataFrame)

    print(f'\nDataframe processing...\n================================')
    bh_id_list = []  #
    bh_idx = 0  # borehole index in the current dataframe

    if diameter not in df.columns:
        print(f"Warning : -- No borehole diameter column found or check given column's name.\n"
              f'To continue, default diameter column has been created with value: '
              f'{DEFAULT_BOREHOLE_DIAMETER}')
        df[diameter] = pd.Series([DEFAULT_BOREHOLE_DIAMETER] * len(df))

    for idx, row in df.iterrows():
        bh_name = row[id_col]
        if date_col not in df.columns:
            bh_date = None
        else:
            bh_date = row[date_col]

        if bh_name not in bh_id_list:
            bh_id_list.append(bh_name)
            boreholes_orm.append(BoreholeOrm(id=bh_name, date=bh_date))
            interval_number = 0

            bh_selection = df[id_col] == f"{bh_name}"
            tmp = df[bh_selection].copy()
            tmp.reset_index(drop=True, inplace=True)
            striplog_dict = striplog_from_dataframe(df=tmp, bh_name=bh_name,
                                                    attributes=attributes,
                                                    symbols=symbols, thickness=thickness,
                                                    intv_top=intv_top, intv_base=intv_base,
                                                    use_default=use_default, query=False)

            for strip in striplog_dict.values():
                for c in get_components(strip):
                    if c not in component_dict.keys():
                        component_dict.update({c: comp_id})
                        comp_id += 1
                        # comp_id = list(component_dict.keys()).index(c)
                    # print(f'component: {c}, component_id: {comp_id}')

                # ORM processing
                interval_dict = {}
                for intv in strip:
                    if average_z is not None and (row['Z'] is None or pd.isnull(row['Z'])):
                        if isinstance(average_z, int) or isinstance(average_z, float):
                            z_val = average_z  # average Z coordinate of boreholes heads
                            print(f'Z coordinate not found, default one is used: {average_z}')
                        else:
                            raise(TypeError("default_Z value must be int or float"))
                    else:
                        z_val = row['Z']
                    # print('test1:', idx, bh_name, z_val)

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

                    desc = ', '.join([c.json() for c in intv.components])
                    # print('description:', desc)
                    interval_dict.update({int_id: {'description': desc,
                                       'interval_number': interval_number,
                                       'top': top, 'base': base}})

                    for cmp in intv.components:
                        if cmp != Component({}):
                            if verbose:
                                print(f'comp_dict: {component_dict}')
                            link_intv_comp_dict.update({
                                (int_id, component_dict[cmp]): {'extra_data': ''}})

                    interval_number += 1
                    int_id += 1
                    pos_id += 2

                if verbose:
                    print(f'{interval_dict}\n')
                if bh_idx < len(boreholes_orm):
                    boreholes_orm[bh_idx].intervals_values = interval_dict
                    if thickness is not None:
                        boreholes_orm[bh_idx].length = tmp[thickness].cumsum().max()
                    elif intv_base is not None:
                        boreholes_orm[bh_idx].length = tmp[intv_base].max()

                    diam_val = tmp[diameter][0]
                    if diam_val is not None and not pd.isnull(diam_val):
                        boreholes_orm[bh_idx].diameter = diam_val
                    else:
                        boreholes_orm[bh_idx].diameter = DEFAULT_BOREHOLE_DIAMETER
                        print(f'No diameter value found, using default: '
                              f'{DEFAULT_BOREHOLE_DIAMETER}')

                bh_idx += 1
        else:
            # already processed
            pass

        components_dict = {v: k for k, v in component_dict.items()}

    print(f"\nEnd of the process : {len(bh_id_list)} boreholes found")

    return boreholes_orm, components_dict, link_intv_comp_dict


def samples_from_dataframe(df, symbols=None, attributes=None, bh_id_col='ID',
                           samp_id_col='ID_ech', samp_type_col='Type_ech', intv_top=None,
                           samp_date_col='Date', intv_base=None, thickness='Length',
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

    samp_id = 0  # interval id *******
    comp_id = 0  # component id
    pos_id = 0  # position id
    samples_orm = []
    components_list = []
    component_dict = {}
    bh_samples_dict = {}
    link_samp_comp_dict = {}  # link between samples and components (<-> junction table)

    assert isinstance(df, pd.DataFrame)

    print(f'\nDataframe processing...\n================================')
    bh_id_list = []
    samp_id_list = []
    samp_idx = 0  # sample index in the current dataframe

    for idx, row in df.iterrows():
        bh_name = row[bh_id_col]
        samp_name = row[samp_id_col]
        samp_type = row[samp_type_col]
        if samp_date_col not in df.columns:
            samp_date = None
        else:
            samp_date = row[samp_date_col]

        samp_id_list.append(samp_name)
        samples_orm.append(SampleOrm(id=samp_name, type=samp_type, date=samp_date))
        if bh_name not in bh_id_list:
            bh_id_list.append(bh_name)
            samp_number = 0

            bh_selection = df[bh_id_col] == f"{bh_name}"
            tmp = df[bh_selection].copy()
            tmp.reset_index(drop=True, inplace=True)
            samples_list = intervals_from_dataframe(tmp, attributes, symbols,
                                                    intv_top, intv_base, thickness,
                                                    sample_prop={'id_col': samp_id_col,
                                                                 'type_col': samp_type_col,
                                                                 'date_col': samp_date_col})
            bh_samples_dict.update({bh_name: samples_list})

            # ORM processing
            sample_dict = {}
            for sp in samples_list:
                for c in sp.components:
                    if c not in component_dict.keys():
                        component_dict.update({c: comp_id})
                        comp_id += 1

                top = PositionOrm(id=pos_id, upper=row['Z'] - sp.top.upper,
                                  middle=row['Z'] - sp.top.middle,
                                  lower=row['Z'] - sp.top.lower,
                                  x=row['X'], y=row['Y']
                                  )

                base = PositionOrm(id=pos_id + 1, upper=row['Z'] - sp.base.upper,
                                   middle=row['Z'] - sp.base.middle,
                                   lower=row['Z'] - sp.base.lower,
                                   x=row['X'], y=row['Y']
                                   )

                desc = ', '.join([c.json() for c in sp.components])
                # print('description:', desc)
                sample_dict.update({samp_id: {'description': desc,
                                             'interval_number': samp_number,
                                             'top': top, 'base': base}})

                for c in sp.components:
                    if c != Component({}):
                        if verbose:
                            print(f'comp_dict: {component_dict}')
                        link_samp_comp_dict.update(
                            {(samp_id, component_dict[c]): {'extra_data': ''}}
                                                  )
                samp_number += 1
                samp_id += 1
                pos_id += 2

        components_list = {v: k for k, v in component_dict.items()}

    print(f"\nEnd of the process : {len(samp_id_list)} samples found")

    return samples_orm, components_list, link_samp_comp_dict

