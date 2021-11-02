import pandas as pd
import re
from striplog import Position, Component, Interval
from core.orm import BoreholeOrm, PositionOrm
from core.visual import Borehole3D
from utils.config import DEFAULT_BOREHOLE_DIAMETER, DEFAULT_BOREHOLE_LENGTH, DEFAULT_POL_LEXICON, WARNING_TEXT_CONFIG, WORDS_WITH_S, NOT_EXIST
from utils.io import update_dict
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
    dict_of_intervals, length_dict = get_interval_list(bh_orm)

    bh_3d = Borehole3D(name=bh_orm.id, date=bh_orm.date, diam=bh_orm.diameter,
                       length=length_dict, legend_dict=legend_dict,
                       intervals_dict=dict_of_intervals)
    if verbose:
        print(bh_orm.id, " added")
    return bh_3d


def get_interval_list(bh_orm):
    """create a list of interval from a boreholeORM object
    
    Parameters
    -------------
    bh_orm: boreholeOrm object

    Returns
    ---------
    interval_dict: dict
        dictionary of Interval objects for each type of interval (lithology or sample)
    depth_dict: dict
        dictionary of borehole's maximum depth for each type of interval (lithology or sample)
                   
    """

    # CONTAM_NAMES = list(DEFAULT_POL_LEXICON.abbreviations.values())
    litho_intervals, samp_intervals = [], []
    depth_l, depth_s = [], []
    x, y = 0, 0
    for i in bh_orm.intervals.values():
        type = i.type
        x, y = i.top.x, i.top.y
        top = Position(upper=i.top.upper, middle=i.top.middle, lower=i.top.lower,
                       x=i.top.x, y=i.top.y)
        base = Position(upper=i.base.upper, middle=i.base.middle, lower=i.base.lower,
                        x=i.top.x, y=i.top.y)

        intv_comp_list = []
        for c in i.description.split('; '):
            intv_comp_list.append(Component(eval(c)))

        # for c in i.description.strip('{|}').split(', '):
        #     print('DESCRIPTIO********', c)
        #     attr_val = [t.strip("'") for t in c.split(': ')]
            # comp_type = 'pollutant' if attr_val[0] in CONTAM_NAMES else 'lithology'
            # comp_val = attr_val[0] if comp_type == 'pollutant' else attr_val[1]
            # comp_lev = attr_val[1] if comp_type == 'pollutant' else None
            # intv_comp_list.append(Component({'type': comp_type, 'value': comp_val,
            #                                  'level': comp_lev}))
            # print('********', intv_comp_list)
            # intv_comp_list.append(Component({attr_val[0]: attr_val[1]})) # old

        if re.search('litho', type, re.I):
            depth_l.append(i.base.middle)
            litho_intervals.append(Interval(top=top, base=base, description=i.description,
                                      components=intv_comp_list, data={'type': type}))
        elif re.search('samp', type, re.I):
            depth_s.append(i.base.middle)
            samp_intervals.append(Interval(top=top, base=base, description=i.description,
                                      components=intv_comp_list, data={'type': type,
                                                                       'sample_ID': 'test'}))

    # set a default values if lists are empty
    warn_msg = lambda x: (f"{WARNING_TEXT_CONFIG['blue']}"
                f"No {x} interval found, a default one is created for visualization !"
                f"{WARNING_TEXT_CONFIG['off']}\n")

    if not litho_intervals:
        depth_l = [DEFAULT_BOREHOLE_LENGTH]
        litho_intervals = [Interval(top=Position(x=x , y=y , middle=0),
                                    base=Position(x=x , y=y , middle=depth_l[0]),
                                    components=[Component({'lithology': NOT_EXIST})])]
        print(warn_msg('lithology'))
    if not samp_intervals:
        depth_s = [DEFAULT_BOREHOLE_LENGTH]
        samp_intervals = [Interval(top=Position(x=x , y=y , middle=0),
                                base=Position(x=x , y=y , middle=depth_l[0]),
                                components=[Component({'benzène': NOT_EXIST})])]
        print(warn_msg('sample'))

    interval_dict = {'lithology': litho_intervals, 'sample': samp_intervals}
    depth_dict = {'lithology': max(depth_l), 'sample': max(depth_s)}
    # print(f'\n===INTERVAL_DICT: {interval_dict}')

    return interval_dict, depth_dict


def boreholes_from_dataframe(data_dict, symbols=None, attributes=None, id_col='ID',
                             diameter_col='Diameter', average_z=None, date_col='Date',
                             sample_type_col=None, verbose=False):
    """ Creates a list of BoreholeORM objects from a dataframe

    Parameters
    ----------
    data_dict: dict
        A dictionary of pandas.DataFrame containing borehole intervals data, based on the type of
        these intervals (lithology or samples). e.g: {'lithology': df_1, 'sample': df2}
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

    if len(data_dict.keys()) > 2:
        raise(KeyError("The data dictionary keys cannot be more than 2 keys"))
    if len(list(filter(re.compile('litho|sample|poll', re.I).match, data_dict.keys()))) < 1:
        raise(KeyError("data_dict keys must contain at least 'lithology', 'sample' or 'pollutant' as keywords. e.g: {'lithology_data': df_litho, 'sample_data': df_samples}"))

    # data concatenation
    df_list = []
    for k, v in data_dict.items():
        assert isinstance(v, pd.DataFrame)

        df = v.copy()
        if re.search('litho', k, re.I):
            df['_intv'] = 'lithology'
        elif re.search('sample|poll', k, re.I):
            df['_intv'] = 'sample'

        # columns' name standardization
        for col in df.columns:
            if re.search('top|toit', col, re.I):
                df.rename(columns={col: 'Top_intv'}, inplace=True)
            elif re.search('base|mur|assise', col, re.I):
                df.rename(columns={col: 'Base_intv'}, inplace=True)
            elif re.search('thick|epais', col, re.I):
                df.rename(columns={col: 'Thick_intv'}, inplace=True)
            elif re.search('desc', col, re.I):
                df.rename(columns={col: 'Desc_intv'}, inplace=True)

        df.insert(list(df.columns).index('Thick_intv') + 1, 'Type_intv', df.pop('_intv'))
        df_list.append(df)

    final_df = df_list[0].append(df_list[1])

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
        final_df[diameter_col] = pd.Series([DEFAULT_BOREHOLE_DIAMETER] * len(final_df))

    top_col, base_col, desc_col = 'Top_intv', 'Base_intv', 'Desc_intv'
    thick_col, intv_type_col = 'Thick_intv', 'Type_intv'

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
                                                    desc_col=desc_col, intv_type_col=intv_type_col,
                                                    query=False, verbose=verbose)

            if striplog_dict is not None:
                bh_counter += 1
                interval_number = 0
                boreholes_orm.append(BoreholeOrm(id=bh_name, date=bh_date))

                for strip_dict in striplog_dict.values():
                    intv_type_dict = {}
                    for iv_type, strip in strip_dict.items():
                        for c in get_components(strip):
                            c_key = list(c.keys())[0]
                            c_type = 'pollutant' if c_key in contam_names else 'lithology'
                            c_val = c_key if c_type == 'pollutant' else c[c_key]
                            # c_lev = c[c_key] if c_type == 'pollutant' else None

                            # remove 's' for plural words
                            if c_val not in WORDS_WITH_S:
                                c_val = c_val.rstrip('s')
                            c = Component({'type': c_type, 'value': c_val})
                            # c = Component({c_key: c_val}) #old
                            if c not in component_dict.keys():
                                component_dict.update({c: comp_id})
                                comp_id += 1
                                # comp_id = list(component_dict.keys()).index(c)

                        # ORM processing
                        interval_dict = {}
                        use_def_z = False
                        for intv in strip:
                            if average_z is not None and (row['Z'] is None or pd.isnull(row['Z'])):
                                if isinstance(average_z, int) or isinstance(average_z, float):
                                    z_val = average_z  # average Z coordinate of boreholes heads
                                    if not use_def_z:
                                        print(f"{WARNING_TEXT_CONFIG['blue']}"
                                              f"WARNING: Borehole's Z coordinate not found, use"
                                              f" default one: {average_z} [m]"
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

                            interval_dict.update({int_id: {'interval_number': interval_number,
                                                    'top': top, 'base': base,
                                                    'type': iv_type, 'description': desc}})

                            update_dict(intv_type_dict, {iv_type: interval_dict})

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
                            # TODO : find a way to store differents type of intervals in ORM
                            # boreholes_orm[bh_idx].intervals_values = interval_dict
                            if re.search('litho', iv_type, re.I):
                                # print('litho_intv:', intv_type_dict['lithology'])
                                boreholes_orm[bh_idx].litho_intv_values = intv_type_dict['lithology']
                            elif re.search('samp', iv_type, re.I):
                                # print('sample_intv:', intv_type_dict['sample'])
                                boreholes_orm[bh_idx].sample_intv_values = intv_type_dict['sample']
                            else:
                                raise(TypeError(f'Unknown interval type: {iv_type}'))

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
