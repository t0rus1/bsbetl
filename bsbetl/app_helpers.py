from bsbetl.functions import get_df_from_store
import datetime
import glob
import io
import json
import logging
import os
import re
from os.path import exists

import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import pandas as pd
from dash_table.Format import Align, Format, Group, Scheme
from numpy.core.numeric import NaN

from bsbetl import alltable_calcs, calc_helpers, g, helpers, ov_calcs
from bsbetl.alltable_calcs import (at_columns, at_params, at_Virtual_MovingAverage)
from bsbetl.alltable_calcs.at_virtual_DayOfWeek import at_virtual_DayOfWeek
from bsbetl.alltable_calcs.at_Virtual_MovingAverage import at_virtual_MovingAverage
# from bsbetl.alltable_calcs.D_AvgOfDailyAvgPriceGradient import AvgOfDailyAveragePriceGradient
# from bsbetl.alltable_calcs.D_HundredDaysBroadness import HundredDaysBroadness
# from bsbetl.alltable_calcs.D_PriceHighestSince import PriceHighestSince
# from bsbetl.alltable_calcs.D_SlowRelativeDAP import SlowRelativeDAP
# from bsbetl.alltable_calcs.M_DailyAveragePrice import DailyAveragePrice
from bsbetl.ov_calcs import ov_columns, ov_params, frt_columns

from bsbetl.results._1St_conditions import _1St_conditions
from bsbetl.results._1St_conditions import _1_min_max_value_condition

from bsbetl.results._2StPr_conditions import _2StPr_conditions
from bsbetl.results._2StPr_conditions import _2StPr_min_max_value_condition
from bsbetl.results._2StVols_conditions import _2StVols_conditions
from bsbetl.results._2StVols_conditions import _2StVols_min_max_value_condition
from bsbetl.results._3jP_conditions import _3jP_conditions
from bsbetl.results._3jP_conditions import _3jP_min_max_value_condition


#from bsbetl.results_initial.dp_conditions import dp_init_conditions, dp_init_min_max_value_condition
#from bsbetl.results_initial.dv_conditions import dv_init_conditions, dv_init_min_max_value_condition
#from bsbetl.results_stage2.dp_stage2_conditions import dp_stage2_conditions, dp_stage2_min_max_value_condition


def sharelists_options(mastershares_wanted: bool) -> list:
    """ generate a list of label, value dictionaries for use in a Dash radiobutton options list """

    sharelists_folder = f'{g.CONTAINER_PATH}\{g.SHARELISTS_FOLDER}'

    files = os.listdir(sharelists_folder)
    files.sort()

    options_list = [{'label': entry, 'value': entry}
                    for i, entry in enumerate(files)]

    if mastershares_wanted:
        # put MasterShareDictionary at the top of the list
        master = g.SHARE_DICTIONARY_NAME
        options_list.insert(
            0, {'label': master, 'value': master})

    # print(options_list)
    return options_list

def sized(sh_listname):
    ''' adds number of shares in parentheses to passed in sharelist name '''
    sized_shl = sh_listname
    if sh_listname.startswith('results_3jP'):
        sized_shl = f"{sh_listname} ({len(g.CONFIG_RUNTIME['_3jP_list'])} shares)"
    elif sh_listname.startswith('results_V2d'):
        sized_shl = f"{sh_listname} ({len(g.CONFIG_RUNTIME['_V2d_list'])} shares)"
    if sh_listname.startswith('results_3nH'):
        sized_shl = f"{sh_listname} ({len(g.CONFIG_RUNTIME['_3jP_list'])} shares)"

    return sized_shl

def alltables_sharelists_options() -> list:
    """ generate a list of label, value dictionaries for use in a Dash radiobutton options list 
        in this case just a selected set of sharelists
    """

    sharelists_folder = f'{g.CONTAINER_PATH}\{g.SHARELISTS_FOLDER}'

    files = os.listdir(sharelists_folder)
    files.sort()

    # only allow these options fir the All-Tables sharelists dropdown
    curated_list = ['Default.shl','results_3jP.shl','results_V2d.shl','results_3nH.shl']

    options_list = [{'label': sized(entry), 'value': entry}
                    for i, entry in enumerate(files) if entry in curated_list]

    # print(options_list)
    return options_list


def history_options() -> list:
    return [{'label': 'last 100 days', 'value': 'last100'},
            {'label': 'earliest calculated', 'value': 'earliest'}]


def bourses_options() -> list:
    return [{'label': bourse, 'value': bourse} for bourse in g.BOURSES_LIST]


def get_at_virtual_col_dropdown_options(stage: int = 0) -> list:

    virt_options_lists = [at_virtual_MovingAverage().contribute_dash_dropdown_options(),
                          at_virtual_DayOfWeek().contribute_dash_dropdown_options()]

    options = []
    for options_list in virt_options_lists:
        for option in options_list:
            options.append(option)

    return options


def inject_virtual_columns(df: pd.DataFrame, virtual_cols: list):

    for vc_name in virtual_cols:
        if vc_name.startswith('MA'):
            vc_creator = at_Virtual_MovingAverage()
            vc_creator.create_virtual_columns(df, virtual_cols)
        if vc_name == 'DOW':
            vc_creator = at_virtual_DayOfWeek()
            vc_creator.create_virtual_columns(df, virtual_cols)

    return


def get_at_calcs_dropdown_options(stage: int = 0) -> list:

    options_list = []
    # list the minutely 
    options_list.append({'label': f'=== Minutely All-Tables calculations ===', 'value': '', 'disabled': True})
    for calc in at_columns.at_calcs_stage_1_list:
        calc_variables_list = ','.join(calc.at_computeds)
        options_list.append(
            {'label': f'{calc.name} ({calc_variables_list})', 'value': calc_variables_list})

    # then the daily
    options_list.append({'label': f'=== Daily All-Table calculations ===', 'value': '', 'disabled': True})
    for calc in at_columns.at_calcs_stage_2_list:
        calc_variables_list = ','.join(calc.at_computeds)
        options_list.append(
            {'label': f'{calc.name} ({calc_variables_list})', 'value': calc_variables_list})

    return options_list

def get_ov_calcs_dropdown_options(stage: int = 0) -> list:

    options_list = []
    if stage == 0 or stage == 1:
        for calc in at_columns.at_calcs_stage_1_list:
            options_list.append(
                {'label': calc.name, 'value': ','.join(calc.ov_computeds)})

    if stage == 0 or stage == 2:
        for calc in at_columns.at_calcs_stage_2_list:
            options_list.append(
                {'label': calc.name, 'value': ','.join(calc.ov_computeds)})

    return options_list


def shares_dropdown_options(sharelist: str, bourse: str) -> list:
    """ generate a list of label, value dictionaries for use in a Dash dropdown options list """

    # two cases: sharelist is either
    # SHARE_DICTIONARY_NAME (MasterShareDictionary.csv)
    # OR
    # one of the 'regular' sharelists to be found under the SHARELISTS_FOLDER
    if sharelist.startswith(g.SHARE_DICTIONARY_NAME):
        sharelist_fq = f'{g.CONTAINER_PATH}\{sharelist}'
        # 1+1 DRILLISCH AG O.N.          ,554550.ETR,31.08.2020,13.11.2020
        # 1+1 DRILLISCH AG O.N.          ,554550.FFM,31.08.2020,13.11.2020
        # 11 88 0 SOLUTIONS AG           ,511880.ETR,31.08.2020,13.11.2020
        # 11 88 0 SOLUTIONS AG           ,511880.FFM,31.08.2020,13.11.2020
        # 2G ENERGY AG                   ,A0HL8N.ETR,31.08.2020,13.11.2020
        # 2G ENERGY AG                   ,A0HL8N.FFM,31.08.2020,13.11.2020
        with open(sharelist_fq, 'r') as shlf:
            shlf.readline()  # skip header
            share_entries = shlf.readlines()
            share_entries.sort()
            # options_list = [{'label': entry[:42], 'value': entry[:42]}
            #                 for i, entry in enumerate(share_entries)]
            options_list = []
            for i, entry in enumerate(share_entries):
                if entry[39:42] == bourse:
                    options_list.append(
                        {'label': entry[:42], 'value': entry[:42]})

            first_entry = f'Use ALL shares in {sharelist}'
            options_list.insert(
                0, {'label': first_entry, 'value': 'IGNORE'})
    else:
        sharelist_fq = f'{g.CONTAINER_PATH}\{g.SHARELISTS_FOLDER}\{sharelist}'
        # ANGLO AMERICAN SP.ADR 1/2      A143BR.ETR
        # ANHEUSER-BUSCH INBEV           A2ASUV.ETR
        # APPLE INC.                     865985.ETR
        with open(sharelist_fq, 'r') as shlf:
            shlf.readline()  # skip header
            share_entries = shlf.readlines()
            share_entries.sort()

            options_list = [{'label': entry, 'value': entry}
                            for i, entry in enumerate(share_entries)]

            first_entry = f'Use ALL shares in {sharelist}'
            options_list.insert(
                0, {'label': first_entry, 'value': 'IGNORE'})

    return options_list


def ov_filter_query_options(stage: int = 1) -> list:
    ''' fill options list with previously saved ov filter query (file) names '''

    options_list = []
    ov_query_filters_directory = f'{g.CONTAINER_PATH}\{g.OV_QUERY_FILTERS_FOLDER}'
    for ovq_name_fq in glob.glob(f'{ov_query_filters_directory}\\stage{stage}\\*.ovq'):
        ovq_name = os.path.basename(ovq_name_fq)
        name = re.sub(r'\.ovq$', '', ovq_name)
        options_list.append({'label': name, 'value': name})

    return options_list


def build_at_fmt(column: str):

    try:
        digits = at_columns.AT_COLS_DIGITS[column]
    except KeyError:
        digits = 2

    specifier = f',.{digits}f'
    return {
        "specifier": f"{specifier}",
        "locale": {
            "group": ".",
            "decimal": ",",
        }
    }


def build_ov_fmt(column: str):

    try:
        digits = ov_columns.OV_COLS_DIGITS[column]
    except KeyError:
        digits = 2

    specifier = f',.{digits}f'
    return {
        "specifier": f"{specifier}",
        "locale": {
            "group": ".",
            "decimal": ",",
        }
    }

def build_results_fmt(column: str, digits=3):

    specifier = f',.{digits}f'
    return {
        "specifier": f"{specifier}",
        "locale": {
            "group": ".",
            "decimal": ",",
        }
    }

def build_price_fmt(digits=3):

    return {
        "specifier": f"$,.{digits}f",
        "locale": {
            "symbol": [u'€', ''],
            "group": ".",
            "decimal": ",",
        },
    }


def build_share_datatable_columns(wanted_cols: list, stage: int, virtual_cols) -> list:
    """ finely specified column dicts for the Dash datatable """

    # native 'manual' 'format' valid keys: 'locale', 'nully','prefix','specifier'
    # see alternative 'Format()' options here: https://github.com/plotly/dash-table/blob/dev/dash_table/Format.py

    id_colspec={
        'name': 'id',
        'id': 'id',
        'selectable': False,
    }

    columns = [id_colspec]
    for col in at_columns.AT_COLS_DASH:
        if not col in wanted_cols:
            continue
        if not col in at_columns.AT_STAGE_TO_COLS[stage]:
            continue
        if col == 'date_time':
            col_entry = {
                'name': col,
                'id': col,
                'type': 'datetime',
                'selectable': False,
            }
        elif col == 'price':
            col_entry = {
                'name': col,
                'id': col,
                'type': 'numeric',
                'selectable': True,
                # formatted "manually"
                'format':  build_price_fmt()
            }
        elif col in ['volume']:
            col_entry = {
                'name': col,
                'id': col,
                'type': 'numeric',
                'selectable': True,
                # formatted with Format object
                # 'format': Format(
                #     scheme=Scheme.fixed,
                #     precision=0,
                #     group=Group.yes,
                #     groups=3,
                #     group_delimiter='.',
                #     # symbol=Symbol.yes,
                #     # symbol_prefix=u'€'
                # ),
            }
        else:
            # all other columns
            col_entry = {
                'name': col,
                'id': col,
                'type': 'numeric',
                'selectable': True,
                # formatted "manually"
                'format': build_at_fmt(col),
            }
        columns.append(col_entry)

    # add virtual columns
    if isinstance(virtual_cols, list):
        for col in virtual_cols:
            col_entry = {
                'name': col,
                'id': col,
                'type': 'numeric',
                'selectable': True,
                # formatted "manually"
                'format': build_at_fmt(col),
            }
            columns.append(col_entry)

    return columns


def add_share_datatable_added_columns(initial_colspecs: list, added_cols: list, stage: int) -> list:
    """ add some plain vanilla columns to that of initial columns, accomadate the new columns added by  pluginfilters """

    # native 'manual' 'format' valid keys: 'locale', 'nully','prefix','specifier'
    # see alternative 'Format()' options here: https://github.com/plotly/dash-table/blob/dev/dash_table/Format.py

    columns = initial_colspecs
    for col in added_cols:
        # assume a plain numeric column will do
        col_entry = {
            'name': col,
            'id': col,
            'type': 'numeric',
            'selectable': True,
            # formatted "manually"
            'format':  {
                "specifier": ",.2f",
                "locale": {
                    "group": ".",
                    "decimal": ",",
                },
            }
        }
        columns.append(col_entry)
    return columns


def build_share_datatable_col_tooltips(wanted_cols: list) -> dict:
    ''' grab column tooltips list for wanted columns '''

    tips = {}
    for col in at_columns.AT_COLS_DASH:
        if not col in wanted_cols:
            continue
        if col in at_columns.AT_COLS_TIPS:
            tips[col] = at_columns.AT_COLS_TIPS[col]
        else:
            tips[col] = 'no notes'

    return tips


# def decide_at_page_size(stage: int):

#     pg_size = 10
#     if stage == 1:
#         pg_size = 60*8 + 36  # minute bands, bus hours
#     elif stage > 1:
#         page_size = 20  # days, approx one month

#     return pg_size

def decide_ov_page_size():

    pg_size = 50
    return pg_size

def build_ov_datatable_col_tooltips(wanted_cols: list, stage: int) -> dict:
    ''' grab column tooltips list for wanted columns '''

    tips = {}
    for col in ov_columns.OV_COLUMNS_DASH:
        if not col in wanted_cols:
            continue
        if not col in ov_columns.OV_STAGE_TO_COLS[stage]:
            continue
        if col in ov_columns.OV_COLS_TIPS:
            tips[col] = ov_columns.OV_COLS_TIPS[col]
        else:
            tips[col] = 'no notes'

    return tips


def get_stored_df_by_sharelist_entry(share_name_num: str, stage: int = 1) -> pd.DataFrame:
    """ extract share dataframe from HDFStore  """

    # NOTE there will be a \n at end of the share_name_num
    # share_name_num:
    # share_name                     number\n
    # ANGLO AMERICAN SP.ADR 1/2      A143BR.ETR\n
    # where extracted share_key will be reformed to be 'ETR_A143BR'

    required_name_num_length = len(
        'ANHEUSER-BUSCH INBEV           A2ASUV.ETR\n')

    data_store = pd.HDFStore(g.SHARE_STORE_FQ.format(stage))
    try:
        assert len(
            share_name_num) == required_name_num_length, 'share name number combination malformed'
        share_num = f'{share_name_num[-11:-1]}'
        share_key = share_num[-3:] + '_' + share_num[0:-4]
        # extract dataframe
        df = data_store[share_key]

        # # remove the index by converting it to a column
        # df.reset_index(inplace=True)
        # # further formatting
        # df['date_time'] = pd.DatetimeIndex(
        #     df['date_time']).strftime("%Y-%b-%d %H:%M")  # "%Y-%m-%d %H:%M" see https://strftime.org/

        return df

    except AssertionError as ae:
        logging.error(f'Assertion Error {ae}')
        return None

    except KeyError as ke:
        # print(f'Key Error {ke}')
        logging.error(f'Key Error {ke}')
        return None

    finally:
        data_store.close()


def split_filter_part(filter_part):

    operators = [['ge ', '>='],
                 ['le ', '<='],
                 ['lt ', '<'],
                 ['gt ', '>'],
                 ['ne ', '!='],
                 ['eq ', '='],
                 ['contains '],
                 ['datestartswith ']]

    for operator_type in operators:
        for operator in operator_type:
            if operator in filter_part:
                name_part, value_part = filter_part.split(operator, 1)
                name = name_part[name_part.find('{') + 1: name_part.rfind('}')]

                value_part = value_part.strip()
                v0 = value_part[0]
                if (v0 == value_part[-1] and v0 in ("'", '"', '`')):
                    value = value_part[1: -1].replace('\\' + v0, v0)
                else:
                    try:
                        value = float(value_part)
                    except ValueError:
                        value = value_part

                # word operators need spaces after them in the filter string,
                # but we don't want these later
                return name, operator_type[0].strip(), value

    return [None] * 3


def get_share_dataframe_as_dict(share_name_num: str, columns: list, stage: int, dayends_only: bool, filter, virtual_cols):
    """ extract share dataframe from HDFStore and return as a dict """

    # NOTE there will be a \n at end of the share_name_num
    # share_name_num:
    # share_name                     number\n
    # ANGLO AMERICAN SP.ADR 1/2      A143BR.ETR\n
    # where extracted share_key will be reformed to be 'ETR_A143BR'

    required_name_num_length = len(
        'ANHEUSER-BUSCH INBEV           A2ASUV.ETR\n')

    data_store = pd.HDFStore(g.SHARE_STORE_FQ.format(stage))
    try:
        assert len(
            share_name_num) == required_name_num_length, 'share name number combination malformed'
        share_num = f'{share_name_num[-11:-1]}'
        share_key = share_num[-3:] + '_' + share_num[0:-4]
        # extract dataframe
        df = data_store[share_key]

        if dayends_only and stage == 1:
            # stage 2 is already day-ends
            # keep last row to peform 17:35 check below
            df_last = df.iloc[[-1]]
            #print(df_last)

            # we normally want to return only these rows
            df = df.between_time('17:35', '17:35')

            # but test last row of df - if its not a 17:35 slot, grab it as well
            df_testlast = df_last.between_time('17:35', '17:35')
            if len(df_testlast) == 0 and len(df_last)==1:
                #print('append!')
                # assume data ran out before 17:35
                df = df.append(df_last)


        #print('DHP:')
        #print(df['DHP'].head())
        #print('---')

        # flatten column labels by choosing just the top level label
        # df.columns = [col[0] for col in df.columns]
        # df_reduced = df.loc[:, 'price':'SPe']

        # this removes the index and makes it ('date_time') as a plain column
        # leaving plain integer index
        df.reset_index(inplace=True)
        # we need a numbered id column for the Datatable
        df['id'] = df.index

        if stage == 1:
            df['date_time'] = pd.DatetimeIndex(
                df['date_time']).strftime("%Y-%m-%d %H:%M")  # "%Y-%m-%d %H:%M" see https://strftime.org/
        else:
            df['date_time'] = pd.DatetimeIndex(
                df['date_time']).strftime("%Y-%m-%d")

        # ensure only wanted columns get handed over
        for dfcol in df.columns:
            if dfcol != 'id' and not dfcol in columns:
                del df[dfcol]

        # opportunity here to create virtual columns
        # print(virtual_cols)
        if isinstance(virtual_cols, list):
            inject_virtual_columns(df, virtual_cols)
            # print(df.head())

        # apply dash filtering
        # print(filter)
        filtering_expressions = filter.split(' && ')
        dff = df
        for filter_part in filtering_expressions:
            col_name, operator, filter_value = split_filter_part(filter_part)

            if operator in ('eq', 'ne', 'lt', 'le', 'gt', 'ge'):
                # these operators match pandas series operator method names
                dff = dff.loc[getattr(dff[col_name], operator)(filter_value)]
            elif operator == 'contains':
                dff = dff.loc[dff[col_name].str.contains(filter_value)]
            elif operator == 'datestartswith':
                # this is a simplification of the front-end filtering logic,
                # only works with complete fields in standard format
                dff = dff.loc[dff[col_name].str.startswith(filter_value)]

        #print(dff.head(1))
        dff_records = dff.to_dict('records')
        #print(dff_records[0])
        return dff_records

    except AttributeError as ae:
        logging.error(f'Attribute Error {ae}')
        return None
    except AssertionError as ae:
        logging.error(f'Assertion Error {ae}')
        return None

    except KeyError as ke:
        #print(f'Key Error {ke} loading {share_name_num}')
        logging.error(f'Key Error {ke} loading {share_name_num}')
        return None

    finally:
        data_store.close()


def build_overview_datatable_column_dicts(wanted_cols: list, stage: int) -> list:
    """ finely specified column dicts for the Dash datatable """

    # native 'manual' 'format' valid keys: 'locale', 'nully','prefix','specifier'
    # see alternative 'Format()' options here: https://github.com/plotly/dash-table/blob/dev/dash_table/Format.py

    col_specs = []
    for col in ov_columns.OV_COLUMNS:
        if not col in wanted_cols:
            continue
        if not col in ov_columns.OV_STAGE_TO_COLS[stage]:
            continue
        if col in ['ShareNumber', 'ShareName', 'Source',]:
            col_entry = {
                'name': col,
                'id': col,
                'selectable': True,
                'type': 'text',
            }
        else:
            # all other columns
            col_entry = {
                'name': col,
                'id': col,
                'selectable': True,
                'type': 'numeric',
                # formatted "manually"
                'format':  build_ov_fmt(col)
            }
        col_specs.append(col_entry)
    return col_specs

def get_ov_dataframe_as_dict(columns: list, stage: int, shl_stage):
    """ extract share dataframe from HDFStore """

    print(f'loading ov {g.OVERVIEW_STORE_FQ.format(stage)} using key {shl_stage} ...')

    data_store = pd.HDFStore(g.OVERVIEW_STORE_FQ.format(stage))
    try:
        # extract dataframe
        df = data_store[shl_stage] # eg data_store['Default_2']
        # df_reduced = df.loc[:, 'price':'SPe']

        # this removes the index and makes it ('ShareNumber) as a plain column
        df.reset_index(inplace=True)

        # ensure only wanted columns get handed over
        for dfcol in df.columns:
            if not dfcol in columns:
                del df[dfcol]

        # NOTE add an id column
        # needed for row identifaction eg when clicking on a row
        df['id'] = df['ShareNumber']
        # leave at NATIVE filtering for now since we get problems with handling OR
        # DASH custom filtering
        dff = df
        return dff.to_dict('records')

    except AssertionError as ae:
        logging.error(f'Assertion Error {ae}')
        return None

    except KeyError as ke:
        # print(f'Key Error {ke}')
        logging.error(f'Key Error {ke}')
        return None

    finally:
        data_store.close()

def get_frt_dataframe_as_dict(columns: list, overlay :bool):
    """ build a FRT dataframe from its Results sources, either appending each batch of shares assoc
        with each individual results source, or coalescing into one list
        The sources are the 3jP, 3V2d & 3nH overviews
    """

    data_store = pd.HDFStore(g.OVERVIEW_STORE_FQ.format(2))
    try:
        # extract each dataframe (and either append or combine)
        df_3jP = data_store['results_3jP_2'] # eg data_store['Default_2']
        df_3jP.reset_index(inplace=True)
        df_3jP['3jP'] = 1

        df_3V2d = data_store['results_V2d_2'] # eg data_store['Default_2']
        df_3V2d.reset_index(inplace=True)
        df_3V2d['3V2d'] = 1

        df_3nH = data_store['results_3nH_2'] # eg data_store['Default_2']
        df_3nH.reset_index(inplace=True)
        df_3nH['3nH'] = 1

        if overlay:
            #print('overlaying')
            # co-alesce and compute source counts - start with 3nH as a base
            # since its the latest overview
            df_ovl = df_3nH.copy()
            df_ovl['3jP'] = 0 # gets updated below
            df_ovl['3V2d'] = 0 # gets updated below 

            #print(f'starting with {len(df_ovl)} ovl rows')

            deletions=[]
            for index,row in df_3jP.iterrows():
                # look for a wanted source in the '3nH' rows and add
                try:
                    target_df = df_ovl[df_ovl['ShareNumber']==row['ShareNumber']]
                    if len(target_df)>0:
                        prior_count = df_ovl.at[target_df.index[0], '3jP']
                        df_ovl.at[target_df.index[0],'3jP'] = prior_count+1
                        deletions.append(index)
                except Exception as exc:
                    print(f'exception {0}')
                    pass
            #get rid those rows we've already coalesced, (keep those we couldnt)
            #print(f'deleting {len(deletions)} 3jP rows')
            df_3jP.drop(deletions,inplace=True)

            #those remaining must go into df_ovl
            df_ovl = df_ovl.append(df_3jP,ignore_index=True)
            #print(f'now {len(df_ovl)} ovl rows')

            deletions=[]
            for index,row in df_3V2d.iterrows():
                # look for a wanted source in the '3nH' rows and add
                try:
                    target_df = df_ovl[df_ovl['ShareNumber']==row['ShareNumber']]
                    if len(target_df)>0:
                        prior_count = df_ovl.at[target_df.index[0], '3V2d']
                        df_ovl.at[target_df.index[0],'3V2d'] = prior_count+1
                        deletions.append(index)
                except Exception as exc:
                    print(f'exception {0}')
                    pass
            #get rid those rows we've already coalesced, (keep those we couldnt)
            #print(f'deleting {len(deletions)} 3V2d rows')
            df_3V2d.drop(deletions,inplace=True)

            df_final = df_ovl.append(df_3V2d, ignore_index=True)            
            #print(f'now {len(df_final)} final rows')

        else:
            df_final = df_3jP.append(df_3V2d, ignore_index=True)
            df_final = df_final.append(df_3nH, ignore_index=True)

        df_final['Score'] = df_final['3jP'] + df_final['3V2d'] + df_final['3nH']

        # this removes the index and makes it ('ShareNumber) as a plain column
        df_final.reset_index(inplace=True)

        # ensure only wanted columns get handed over
        for dfcol in df_final.columns:
            if not dfcol in columns:
                del df_final[dfcol]

        # NOTE add an id column
        # needed for row identifaction eg when clicking on a row
        df_final['id'] = df_final['ShareNumber']
        # leave at NATIVE filtering for now since we get problems with handling OR
        # DASH custom filtering
        dff = df_final
        return dff.to_dict('records')

    except AssertionError as ae:
        logging.error(f'Assertion Error {ae}')
        return None

    except KeyError as ke:
        # print(f'Key Error {ke}')
        logging.error(f'Key Error {ke}')
        return None

    finally:
        data_store.close()


# def get_overview_fields_options(stage :int = 0) -> list:

#     options = []
#     for col in ov_calcs.ov_columns.OV_COLUMNS:
#         options.append({'label': col, 'value': col, 'enabled': True})
#     return options


def get_overview_fields_options(stage: int = 0) -> list:

    options = []
    ov_cols = ov_calcs.ov_columns.OV_COLUMNS
    #ov_cols.sort()
    for col in ov_cols:
        enabled = stage == 0 or (col in ov_columns.OV_STAGE_TO_COLS[stage])
        options.append({'label': col, 'value': col, 'disabled': not enabled})

    return options

def get_frt_fields_options() -> list:

    options = []
    for col in frt_columns.FRT_COLUMNS:
        enabled = True
        options.append({'label': col, 'value': col, 'disabled': not enabled})

    return options

def get_frt_fields_initial_values() -> list:

    values = [col for col in frt_columns.FRT_COLUMNS]
    return values

def get_overview_fields_initial_values() -> list:

    values = [col for col in ov_calcs.ov_columns.OV_COLUMNS_INITIAL]
    #values.sort()
    return values


def get_overview_fields_allvalues() -> list:

    values = [col for col in ov_calcs.ov_columns.OV_COLUMNS]
    #values.sort()
    return values


def get_overview_fields_initialvalues() -> list:

    values = [col for col in ov_calcs.OV_COLUMNS_INITIAL]
    #values.sort()
    return values


def get_alltable_fields_options(stage: int = 0) -> list:

    options = []
    atcols=alltable_calcs.at_columns.AT_COLS_DASH
    #atcols.sort()
    for col in atcols:
        enabled = stage == 0 or (col in at_columns.AT_STAGE_TO_COLS[stage])
        options.append({'label': col, 'value': col,
                        'disabled': col == 'date_time' or not enabled})
    return options


def get_alltable_fields_initial_values() -> list:

    cols = alltable_calcs.at_columns.AT_COLS_DASH_INITIAL
    #cols.sort()
    return cols

def get_alltable_fields_plot_values() -> list:

    values = [col for col in g.CONFIG_RUNTIME['ov_at_plot_columns']]
    #values.sort()
    return values


def get_alltable_fields_allvalues() -> list:

    values = [col for col in alltable_calcs.at_columns.AT_COLS_DASH]
    #values.sort()
    return values


def build_sharelist_datatable_columns(wanted_cols: list) -> list:
    """ finely specified column dicts for the Dash datatable """

    # native 'manual' 'format' valid keys: 'locale', 'nully','prefix','specifier'
    # see alternative 'Format()' options here: https://github.com/plotly/dash-table/blob/dev/dash_table/Format.py

    columns = []
    for index, col in enumerate(g.MASTER_SHARELIST_COLUMNS):
        if not col in wanted_cols:
            continue
        if col in ['first_date', 'last_date']:
            col_entry = {
                'name': col,
                'id': col,
                'type': 'datetime',
                'deletable': False,
                'selectable': False,
            }
        else:
            # all other columns
            col_entry = {
                'name': col,
                'id': col,
                'type': 'text',
                'deletable': False,
                'selectable': False,
                # formatted "manually"
                # 'format':  {
                #     "specifier": ",.2f",
                #     "locale": {
                #         "group": ".",
                #         "decimal": ",",
                #     },
                # }
            }

        columns.append(col_entry)
    return columns


def get_master_sharelist_dataframe_as_dict(dict_filename: str, bourse: str,
                                           filtering_sharelist_name: str,
                                           selection_shares: list,
                                           overlay_master: bool) -> dict:

    # print(f"dict_filename={dict_filename}\nbourse={bourse}\nfiltering_sharelist_name={filtering_sharelist_name}\nselection_shares={selection_shares}\noverlay_master={overlay_master}")

    df = pd.read_csv(dict_filename, header=0,
                     names=g.MASTER_SHARELIST_COLUMNS_DASH)

    df = df[df['number'].str.endswith(bourse)]

    # consult passed in sharelist file to construct and apply a filter
    if len(filtering_sharelist_name) > 0 and not overlay_master:
        filtering_sharelist_fq = g.CONTAINER_PATH + \
            f'\{g.SHARELISTS_FOLDER}\{filtering_sharelist_name}'
        filtering_sharelist_tuples = calc_helpers.get_sharelist_list(
            filtering_sharelist_fq)
        # create simple list of chosen share numbers
        chosen_shares = [number for _, number in filtering_sharelist_tuples]
        if len(chosen_shares) > 0:
            df = df[df['number'].isin(chosen_shares)]

    # further filtering on selection shares if not overlaying master
    if isinstance(selection_shares, list) and len(selection_shares) > 0 and not overlay_master:
        df = df[df['number'].isin(selection_shares)]

    # print(df.head())
    df_dict = df.to_dict('records')
    # print(df_dict)
    return df_dict


def share_in_dashtable(datatable_data: list, target_share_num: str):
    ''' looks thru datatable_data for a row with a share number matching '''

    for row in datatable_data:
        if row['number'] == target_share_num:
            return True

    return False


def print_callback_context(ctx, suppress_states=True):
    ''' print dash.callback_context, optionally suppressing the printing of states, which can get very verbose '''

    if suppress_states:
        ctx_msg = json.dumps({
            # 'states': ctx.states,
            'triggered': ctx.triggered,
            'inputs': ctx.inputs
        }, indent=2)
    else:
        ctx_msg = json.dumps({
            'states': ctx.states,
            'triggered': ctx.triggered,
            'inputs': ctx.inputs
        }, indent=2)

    #print('context=', ctx_msg)


# def params_formfields(calc_params: dict, parm_type: str):
#     ''' return an html tree of form labels and input fields for passed in calc_params dict

#         For display in the correspong All-Table calculations or Overview calculations tab '''

#     # enclose each param with a label and input elements in a Div
#     form_rows = []
#     for (parm_name, parm) in calc_params.items():
#         row_label = html.Label(
#             children=parm_name[4:])
#         row_input = dcc.Input(
#             id={
#                 'type': parm_type,
#                 'index': parm_name
#             },
#             type='number',
#             min=parm['min'],
#             max=parm['max'],
#             value=parm['setting'],
#             #placeholder='enter parameter value',
#             debounce=True,
#         )
#         row_extrema_label = html.Label(
#             f"{parm['min']} → {parm['max']}", className='sw-muted-label')
#         # form_rows.append(
#         #     html.Div(children=[row_label, row_input, row_extrema_label]))
#         form_rows.append(row_label)
#         form_rows.append(row_input)
#         form_rows.append(row_extrema_label)
#         form_rows.append(html.Br())

#     return html.Div(form_rows)


def hlp_make_params_form_row(parm_name, parm, parm_type) -> list:

    row_label = html.Label(
        children=parm_name[4:])
    row_input = dcc.Input(
        id={
            'type': parm_type,
            'index': parm_name
        },
        type='number',
        min=parm['min'],
        max=parm['max'],
        value=parm['setting'],
        # placeholder='enter parameter value',
        debounce=False,
    )
    row_extrema_label = html.Label(
        f"{parm['min']} → {parm['max']}", className='sw-muted-label')

    return [row_label, row_input, row_extrema_label, html.Br()]


def hlp_make_condition_form_row(cond_group_name, cond_dict, min_max_val :tuple, cond_type, row_num :int) -> list:

    # create these now for use below
    docref_div = html.Div(children=f"document ref: {cond_dict['document_ref']}", style={'float': 'right'})
    if row_num == 0:
        desc_legend= html.Label('description:', className='sw-muted-legend')
        # don't repeat the description for multi setting conditions
        row_label = html.Label(children=cond_dict['name'])
        desc_label= html.Label(f"{cond_dict['description']}") #, className='sw-muted-label')    
        notes_legend= html.Label('notes:', className='sw-muted-legend')
        notes_label= html.Label(f"{cond_dict['notes']}", className='sw-muted-label')
    else:
        desc_legend= html.Label('description:', className='sw-muted-legend')
        row_label = '' #html.Label(children=cond_dict['name'])
        desc_label = html.Label('see above') #,className='sw-muted-label')
        notes_legend= html.Label('', className='sw-muted-legend')
        notes_label= html.Label(f"", className='sw-muted-label')

    #notes_legend= html.Label('notes:', className='sw-muted-legend')
    #notes_label= html.Label(f"{cond_dict['notes']}", className='sw-muted-label')

    #if not cond_dict['description'].startswith('NO PARAMETERS') and not cond_dict['notes'].startswith('NO PARAMETERS'):
    if not cond_dict['notes'].startswith('NO PARAMETERS'):
        #row_label = html.Label(children=cond_dict['name'])
        row_input = dcc.Input(
            id={
                'type': cond_type,
                'index': cond_dict['name']                
            },
            type='number',
            min=float(min_max_val[0]),
            max=float(min_max_val[1]),
            value=float(min_max_val[2]),
            step=0.001,
            # placeholder='enter parameter value',
            debounce=False,
        )
        extrema_label = html.Label(f"{min_max_val[0]} → {min_max_val[1]}", className='sw-muted-label')
        setting_label = html.Label(min_max_val[3],className='sw-muted-legend')
    else:
        row_label=html.Label('')
        row_input=html.Label('')
        extrema_label=html.Label('')
        setting_label=html.Label('')

    desc_legend_and_label = html.Div(children=[
        desc_legend,desc_label,docref_div
    ])

    #return [row_label, desc_legend, desc_label, html.Br(), setting_label, row_input, extrema_label, html.Br(),  notes_legend, notes_label, html.Br()] #, html.Br()]
    return [row_label, desc_legend_and_label, setting_label, row_input, extrema_label, html.Br(),  notes_legend, notes_label, html.Br()] #, html.Br()]

def hlp_make_adjustors_form_row(cond_group_name, cond_dict, cond_type) -> list:

    adj_strings = [str(i) for i in cond_dict['adjustors']]
    adj_values = ';'.join(adj_strings)

    setting_label = html.Label("adjustors (for unamed parameters). Refer corresponding curly braces in the description. Use '.' for decimals. Take care to not delete the separating semi-colons!",className='sw-muted-legend')
    row_input = dcc.Input(
        id={
            'type': cond_type,
            'index': cond_dict['name']                
        },
        type='text',
        value=adj_values,
        # placeholder='enter parameter value',
        debounce=False,
    )

    return [setting_label, row_input, html.Br()]


def params_formfields(calc_params: dict, parm_type: str):
    ''' return an html tree of form labels and input fields for passed in calc_params dict

        For display in the correspong All-Table calculations or Overview calculations tab '''

    form_rows = []
    calcs = ['getridof']
    # first pass gathers the calculations
    # parameters which are not in groups are treated as distinct un-named groups
    for (parm_name, parm) in calc_params.items():
        if calcs[-1] != parm['calculation']:
            calcs.append(parm['calculation'])

    # now each group will be a fieldset
    calcs.remove('getridof')
    for calc in calcs:
        # for this calc, build all assoc parameters as form rows
        # print(calc)
        # print(calc_params.items())
        rows_to_add = [html.Legend(calc)]
        params_for_calc = [
            parm_tuple for parm_tuple in calc_params.items() if parm_tuple[1]['calculation'] == calc]

        # print(params_for_calc)

        # doc_ref
        #rows_to_add.append(html.Label(children=f"{parm_tuple[1]['doc_ref']}",style={'float': 'right'}))
        rows_to_add.append(html.Label(children=f"{params_for_calc[0][1]['doc_ref']}",style={'float': 'right'}))
        for parm_tuple in params_for_calc:
            rows_to_add.extend(hlp_make_params_form_row(parm_tuple[0], parm_tuple[1], parm_type))

        form_rows.append(html.Fieldset(rows_to_add))

    return html.Form(id=parm_type,children=form_rows)

def num_inputs_for_condition(cond :dict) ->int:
    ''' returns how many (form) inputs each condition holds '''

    num_inputs=0
    for key in cond.keys():
        if key.endswith('_max'):
            num_inputs = num_inputs+1
    if 'adjustors' in cond:
        num_inputs = num_inputs + 1 #len(cond['adjustors'])    

    return num_inputs


def _1_conditions_formfields(cond_type: str) ->str:
    ''' return an html tree of form labels and input fields for passed in calc_params dict
        For display in the correspong All-Table calculations or Overview calculations tab 
    '''

    # first pass gathers the calculation groups
    # dp_init_conditions is a global dict of dicts (see dp_conditions.py)
    # {
    #  'Con_a': {'name': 'Con_a', 'group': 'Con_a', 'description':  ...}, 
    #  'Con_b1': {'name': 'Con_b1', 'group': 'Con_b', 'description': ... },
    #  'Con_b2': {'name': 'Con_b2', 'group': 'Con_b', 'description': ... },
    #   ...
    #  'Con_j': {'name' : 'Con_j', 'group': 'Con_j','description': ...}
    # }  

    form_rows = []
    calc_groups = ['getridof'] # will hold ['Con_a','Con_b', ...'Con_j',]
    for (group_name, condition_dict) in _1St_conditions.items():
        if calc_groups[-1] != condition_dict['group']:
            calc_groups.append(condition_dict['group'])

    calc_groups.remove('getridof')

    # now each group will be a fieldset
    for calc in calc_groups: # eg 'Con_a','Con_b',...
        # for this calc, build all assoc fields as form rows
        rows_to_add = [html.Legend(calc)]
        fields_for_calc_group = [cond_tuple for cond_tuple in _1St_conditions.items() if cond_tuple[1]['group'] == calc]
        for cond_tuple in fields_for_calc_group:
            #print(f'cond_tuple: {cond_tuple}')
            min_max_vals = _1_min_max_value_condition(cond_tuple[1]) # cond_tuple[1] is the condition dict itself
            # min_max_vals is 
            # min,max,current value & setting_name as a list of tuples
            for i,min_max_val in enumerate(min_max_vals):
                fr = hlp_make_condition_form_row(cond_tuple[0], cond_tuple[1], min_max_val, cond_type,i)
                rows_to_add.extend(fr)
            # adjustors for row
            if 'adjustors' in cond_tuple[1]:
                fr = hlp_make_adjustors_form_row(cond_tuple[0],cond_tuple[1], cond_type)
                rows_to_add.extend(fr)

        form_rows.append(html.Fieldset(rows_to_add))

    form_content = html.Form(id=cond_type,children=form_rows)
    return form_content

def _2StPr_conditions_formfields(cond_type: str) ->str:
    ''' return an html tree of form labels and input fields for passed in calc_params dict
        For display in the correspong All-Table calculations or Overview calculations tab 
    '''

    # first pass gathers the calculation groups
    # dp_init_conditions is a global dict of dicts (see dp_conditions.py)
    # {
    #  'Con_a': {'name': 'Con_a', 'group': 'Con_a', 'description':  ...}, 
    #  'Con_b1': {'name': 'Con_b1', 'group': 'Con_b', 'description': ... },
    #  'Con_b2': {'name': 'Con_b2', 'group': 'Con_b', 'description': ... },
    #   ...
    #  'Con_j': {'name' : 'Con_j', 'group': 'Con_j','description': ...}
    # }  

    form_rows = []
    calc_groups = ['getridof'] # will hold ['Con_a','Con_b', ...'Con_j',]
    for (group_name, condition_dict) in _2StPr_conditions.items():
        if calc_groups[-1] != condition_dict['group']:
            calc_groups.append(condition_dict['group'])

    calc_groups.remove('getridof')

    # now each group will be a fieldset
    for calc in calc_groups: # eg 'Con_a','Con_b',...
        # for this calc, build all assoc fields as form rows
        rows_to_add = [html.Legend(calc)]
        fields_for_calc_group = [cond_tuple for cond_tuple in _2StPr_conditions.items() if cond_tuple[1]['group'] == calc]
        for cond_tuple in fields_for_calc_group:
            min_max_vals = _2StPr_min_max_value_condition(cond_tuple[1])
            for i,min_max_val in enumerate(min_max_vals):
                fr = hlp_make_condition_form_row(cond_tuple[0], cond_tuple[1], min_max_val, cond_type,i)
                if len(fr) > 0:
                    rows_to_add.extend(fr)
            # adjustors for row
            if 'adjustors' in cond_tuple[1]:
                fr = hlp_make_adjustors_form_row(cond_tuple[0],cond_tuple[1], cond_type)
                rows_to_add.extend(fr)

        form_rows.append(html.Fieldset(rows_to_add))

    form_content = html.Form(id=cond_type,children=form_rows)
    return form_content

def _2StVols_conditions_formfields(cond_type: str) ->str:
    ''' return an html tree of form labels and input fields for passed in calc_params dict
        For display in the correspong All-Table calculations or Overview calculations tab 
    '''

    # first pass gathers the calculation groups
    # dp_init_conditions is a global dict of dicts (see dp_conditions.py)
    # {
    #  'Con_a': {'name': 'Con_a', 'group': 'Con_a', 'description':  ...}, 
    #  'Con_b1': {'name': 'Con_b1', 'group': 'Con_b', 'description': ... },
    #  'Con_b2': {'name': 'Con_b2', 'group': 'Con_b', 'description': ... },
    #   ...
    #  'Con_j': {'name' : 'Con_j', 'group': 'Con_j','description': ...}
    # }  

    form_rows = []
    calc_groups = ['getridof'] # will hold ['Con_a','Con_b', ...'Con_j',]
    for (group_name, condition_dict) in _2StVols_conditions.items():
        if calc_groups[-1] != condition_dict['group']:
            calc_groups.append(condition_dict['group'])

    calc_groups.remove('getridof')

    # now each group will be a fieldset
    for calc in calc_groups: # eg 'Con_a','Con_b',...
        # for this calc, build all assoc fields as form rows
        rows_to_add = [html.Legend(calc)]
        fields_for_calc_group = [cond_tuple for cond_tuple in _2StVols_conditions.items() if cond_tuple[1]['group'] == calc]
        for cond_tuple in fields_for_calc_group:
            min_max_vals = _2StVols_min_max_value_condition(cond_tuple[1])
            for i,min_max_val in enumerate(min_max_vals):
                fr = hlp_make_condition_form_row(cond_tuple[0], cond_tuple[1], min_max_val, cond_type,i)
                if len(fr)>0:
                    rows_to_add.extend(fr)
            # adjustors for row
            if 'adjustors' in cond_tuple[1]:
                fr = hlp_make_adjustors_form_row(cond_tuple[0],cond_tuple[1], cond_type)
                rows_to_add.extend(fr)

        form_rows.append(html.Fieldset(rows_to_add))

    form_content = html.Form(id=cond_type,children=form_rows)
    return form_content

def _3jP_conditions_formfields(cond_type: str) ->str:
    ''' return an html tree of form labels and input fields for passed in calc_params dict
        For display in the correspong All-Table calculations or Overview calculations tab 
    '''

    # first pass gathers the calculation groups
    # dp_init_conditions is a global dict of dicts (see dp_conditions.py)
    # {
    #  'Con_a': {'name': 'Con_a', 'group': 'Con_a', 'description':  ...}, 
    # }  

    form_rows = []
    calc_groups = ['getridof'] # will hold ['Con_a','Con_b', ...'Con_j',]
    for (group_name, condition_dict) in _3jP_conditions.items():
        if calc_groups[-1] != condition_dict['group']:
            calc_groups.append(condition_dict['group'])

    calc_groups.remove('getridof')

    # now each group will be a fieldset
    for calc in calc_groups: # eg 'Con_a','Con_b',...
        # for this calc, build all assoc fields as form rows
        rows_to_add = [html.Legend(calc)]
        fields_for_calc_group = [cond_tuple for cond_tuple in _3jP_conditions.items() if cond_tuple[1]['group'] == calc]
        for cond_tuple in fields_for_calc_group:
            min_max_vals = _3jP_min_max_value_condition(cond_tuple[1])
            for i,min_max_val in enumerate(min_max_vals):
                fr = hlp_make_condition_form_row(cond_tuple[0], cond_tuple[1], min_max_val, cond_type,i)
                if len(fr) > 0:
                    rows_to_add.extend(fr)
            # adjustors for row
            if 'adjustors' in cond_tuple[1]:
                fr = hlp_make_adjustors_form_row(cond_tuple[0],cond_tuple[1], cond_type)
                rows_to_add.extend(fr)

        form_rows.append(html.Fieldset(rows_to_add))

    form_content = html.Form(id=cond_type,children=form_rows)
    return form_content


def save_at_calc_params():
    ''' save parameters file (while maintaining backup of most recent version) '''

    # we save in list form
    at_calc_params_list = []
    for _, parm in at_params.at_calc_params.items():
        at_calc_params_list.append(parm)

    # back up existing one first
    prior_fq = f'{g.AT_CALC_PARAMS_FQ}.bak'
    if exists(prior_fq):
        os.remove(prior_fq)

    os.rename(g.AT_CALC_PARAMS_FQ, prior_fq)

    # write new
    with open(g.AT_CALC_PARAMS_FQ, 'w') as f:
        #f.write(json.dumps(at_calc_params_list.sort(key=lambda item: item.get('name')), indent=4))
        f.write(json.dumps(at_calc_params_list, indent=4))

def save_1St_conditions():
    ''' save conditions file (while maintaining backup of most recent version) '''

    # we save in list form
    conditions_list = []
    for _, cond in _1St_conditions.items():
        conditions_list.append(cond)

    # back up existing one first
    prior_fq = f'{g._1_CONDITIONS_FQ}.bak'
    if exists(prior_fq):
        os.remove(prior_fq)

    os.rename(g._1_CONDITIONS_FQ, prior_fq)

    # write new
    with open(g._1_CONDITIONS_FQ, 'w') as f:
        f.write(json.dumps(conditions_list,indent=4))  #.sort(key=lambda item: item['name']), indent=4))


def save_2StPr_conditions():
    ''' save conditions file (while maintaining backup of most recent version) '''

    # we save in list form
    conditions_list = []
    for _, cond in _2StPr_conditions.items():
        conditions_list.append(cond)

    #print(g._2STPR_CONDITIONS_FQ)

    # back up existing one first
    prior_fq = f'{g._2STPR_CONDITIONS_FQ}.bak'
    if exists(prior_fq):
        os.remove(prior_fq)

    os.rename(g._2STPR_CONDITIONS_FQ, prior_fq)

    # write new
    with open(g._2STPR_CONDITIONS_FQ, 'w') as f:
        f.write(json.dumps(conditions_list,indent=4))  #.sort(key=lambda item: item['name']), indent=4))

def save_2StVols_conditions():
    ''' save conditions file (while maintaining backup of most recent version) '''

    # we save in list form
    conditions_list = []
    for _, cond in _2StVols_conditions.items():
        conditions_list.append(cond)

    #print(g._2STPR_CONDITIONS_FQ)

    # back up existing one first
    prior_fq = f'{g._2STVOLS_CONDITIONS_FQ}.bak'
    if exists(prior_fq):
        os.remove(prior_fq)

    os.rename(g._2STVOLS_CONDITIONS_FQ, prior_fq)

    # write new
    with open(g._2STVOLS_CONDITIONS_FQ, 'w') as f:
        f.write(json.dumps(conditions_list,indent=4))  #.sort(key=lambda item: item['name']), indent=4))

def save_3jP_conditions():
    ''' save conditions file (while maintaining backup of most recent version) '''

    # we save in list form
    conditions_list = []
    for _, cond in _3jP_conditions.items():
        conditions_list.append(cond)

    # back up existing one first
    prior_fq = f'{g._3JP_CONDITIONS_FQ}.bak'
    if exists(prior_fq):
        os.remove(prior_fq)

    os.rename(g._3JP_CONDITIONS_FQ, prior_fq)

    # write new
    with open(g._3JP_CONDITIONS_FQ, 'w') as f:
        f.write(json.dumps(conditions_list,indent=4))  #.sort(key=lambda item: item['name']), indent=4))


def save_dict_values_as_txt(dict_to_save: dict, save_name_fq: str, header: str):

    prior_fq = f'{save_name_fq}.bak'
    if exists(prior_fq):
        os.remove(prior_fq)

    os.rename(save_name_fq, prior_fq)

    # write new
    with io.open(save_name_fq, 'w', encoding='utf-8') as f:
        if len(header) > 0:
            f.write(f'{header}\n')
        for value in dict_to_save.values():
            f.write(f'{value}\n')


def save_dataframe_as_text(df_data: list, save_name_fq: str, header: str):

    # take care of backup
    prior_fq = f'{save_name_fq}.bak'
    if exists(prior_fq):
        os.remove(prior_fq)

    os.rename(save_name_fq, prior_fq)

    # write out new text file
    with io.open(save_name_fq, 'w', encoding='utf-8') as f:
        if len(header) > 0:
            f.write(f'{header}\n')
        # use header to extract keys
        # eg header: 'bsb_name,bsb_number,investing_name,investing_symbol'
        keys = header.split(',')
        for entry in df_data:
            out_line = ''
            for key in keys:
                out_line = out_line + f'{entry[key]},'
            # chop off last commas
            out_line = out_line[:-1]
            f.write(f'{out_line}\n')


def save_ov_calc_params():
    ''' save parameters file (while maintaining backup of most recent version) '''

    # we save in list form
    ov_calc_params_list = []
    for _, parm in ov_params.ov_calc_params.items():
        ov_calc_params_list.append(parm)

    # back up existing one first
    prior_fq = f'{g.OV_CALC_PARAMS_FQ}.bak'
    if exists(prior_fq):
        os.remove(prior_fq)

    os.rename(g.OV_CALC_PARAMS_FQ, prior_fq)

    # write new
    with open(g.OV_CALC_PARAMS_FQ, 'w') as f:
        #f.write(json.dumps(ov_calc_params_list.sort(key=lambda item: item.get('name')), indent=4))
        f.write(json.dumps(ov_calc_params_list, indent=4))


def get_bsb_lookup_columns() -> list:

    columns = []
    for i in g.BSB_CODE_LOOKUP_COLS:
        columns.append({"name": i, "id": i, "type": "text"})
    # insert also last_bsb_price
    columns.insert(
        2, {"name": "bsb_price", "id": "bsb_price", "type": "numeric"})

    return columns


def get_use_screener_columns() -> list:

    columns = []
    for i in g.INVESTING_COM_USABLE_SCREENER_COLS:
        columns.append({"name": i, "id": i, "type": "text"})

    return columns


def get_bsb_lookup_dataframe_as_dict(bsblookup_filename: str) -> tuple:

    # .set_index('bsb_number', drop=False, inplace=True)
    df_lookup = pd.read_csv(bsblookup_filename)
    df_lookup = df_lookup.fillna('')
    df_lookup.set_index('bsb_number', drop=False, inplace=True)
    df_lookup['bsb_price'] = 0.0
    # print('df_lookup')
    # print(df_lookup.head())

    # NOTE old way using prices from the CSV files in the By_Share folders
    # build dataframe to hold latest prices
    #df_latest = helpers.get_latest_prices_from_share_by_day_folders()
    #df_lookup['bsb_price'] = df_latest['bsb_price']

    # NOTE new way, using the LastPrices.json file which is updated every process-2 run
    g.latest_share_prices = helpers.get_latest_prices_from_last_gen_csv_by_day_run()
    df_latest = pd.DataFrame.from_dict(
        g.latest_share_prices, orient='index', columns=['bsb_price'])
    df_lookup['bsb_price'] = df_latest['bsb_price']

    # 'investing_symbol'
    num_uncoded = len(df_lookup[df_lookup['investing_symbol'] == ''])
    df_dict = df_lookup.to_dict('records')
    return (df_dict, num_uncoded)


def build_bsb_lookup_col_tooltips() -> dict:
    ''' return column tooltips  '''

    tips = {}
    for col in g.BSB_CODE_LOOKUP_COLS:
        if col in g.BSB_CODE_LOOKUP_COLS_TIPS:
            tips[col] = g.BSB_CODE_LOOKUP_COLS_TIPS[col]
        else:
            tips[col] = 'no notes'

    # the inserted bsb_price col also needs a tooltip
    tips['bsb_price'] = 'latest bsb downloaded price'

    return tips


def new_screener_contributor_options(optsOrValues: g.ScreenerDropdownOptions) -> list:
    ''' return checklist options (or values) for csv filenames in screener path '''

    return_list = []
    screener_pattern = f"{g.SCREENER_RESULTS_PATH}\*.csv"
    for fl in glob.glob(screener_pattern):
        csv_name = f'{os.path.basename(fl)}'
        if optsOrValues == g.ScreenerDropdownOptions.OPTIONS:
            return_list.append({'label': csv_name, 'value': csv_name})
        else:
            return_list.append(csv_name)
    return return_list


def get_combined_screeners_as_dict(files_to_combine: list):

    screener_pattern = f"{g.SCREENER_RESULTS_PATH}\*.csv"
    screener_files = glob.glob(screener_pattern)

    # do the file combining
    today_segment = datetime.date.today().strftime("%Y_%m_%d")
    combined_fq = f'{g.CONTAINER_PATH}\{g.SCREENER_FOLDER}\\Screener_{today_segment}.csv'
    with open(combined_fq, "wb") as outfile:
        for wanted_file in files_to_combine:
            for f in screener_files:
                if f.endswith(wanted_file):
                    with open(f, "rb") as infile:
                        outfile.write(infile.read())
                        break

    # load up the combined file
    df = pd.read_csv(combined_fq)
    df = df.fillna('')
    # get rid of the headings rows which get imported from every individual Screener Resuts.csv file
    index_names = df[df['Symbol'] == 'Symbol'].index
    df.drop(index_names, inplace=True)

    # sort by name to take care of likely random order of file ingestion
    rslt_df = df.sort_values(by='Name')

    df_dict = rslt_df.to_dict('records')
    return df_dict


def build_screener_files_options(optsOrValues: g.ScreenerDropdownOptions) -> list:

    return_list = []
    screener_pattern = f"{g.CONTAINER_PATH}\{g.SCREENER_FOLDER}\Screener_*.csv"
    for fl in glob.glob(screener_pattern):
        csv_name = f'{os.path.basename(fl)}'
        if optsOrValues == g.ScreenerDropdownOptions.OPTIONS:
            return_list.append({'label': csv_name, 'value': fl})
        else:
            return_list.append(fl)
    return return_list


def get_screener_dataframe_as_dict(screener_filename: str) -> tuple:

    df_screener = pd.read_csv(screener_filename)
    df_screener = df_screener.fillna('')
    df_screener.set_index('Symbol', drop=False, inplace=True)
    # df_screener.drop_duplicates(inplace=True)

    # add an 'Unmapped' column
    # for col in g.INVESTING_COM_USABLE_SCREENER_COLS:
    #     if not col in df_screener.columns:
    #         if col == 'bsb_number':
    #             df_screener[col] = 'not mapped'
    #         else:
    #             df_screener[col] = ''

    # add an 'Unmapped' column
    df_screener['bsb_number'] = 'not mapped'
    # print(df_screener.columns)

    # load up the BsbCodelookup file
    df_lookup = pd.read_csv(g.BSB_CODE_LOOKUP_NAME_FQ)
    df_lookup = df_lookup.fillna('')
    df_lookup.set_index('investing_symbol', drop=False, inplace=True)
    df_lookup.index.rename('Symbol', inplace=True)
    df_lookup.drop_duplicates(inplace=True)
    # we need to drop rows in the lookup which have blank investing_symbol
    df_lookup['investing_symbol'].replace('', np.nan, inplace=True)
    df_lookup.dropna(subset=['investing_symbol'], inplace=True)
    # now assign the screener bsb_number from the lookup dataframe
    df_screener['bsb_number'] = df_lookup['bsb_number']
    # dont show the .ETR in the bsb_number column (helps with the copy and paste from the plaintext panel)
    df_screener['bsb_number'] = df_screener['bsb_number'].str.replace(
        '.ETR', '')

    # print('lookup:')
    # print(df_lookup.head(10))

    # print('screener:')
    # print(df_screener.head(10))

    # get rid of page headings which resulted from the combining of screener results files
    index_names = df_screener[df_screener['Symbol'] == 'Symbol'].index
    df_screener.drop(index_names, inplace=True)

    num_unmapped = len(df_screener[df_screener['bsb_number'] == 'not mapped'])

    df_dict = df_screener.to_dict('records')
    return (df_dict, num_unmapped)


def build_combined_1_2_datatable_column_dicts(sharelist :str) -> list:

    res_df = get_df_from_store(g._COMBINED_1_2_RESULTS_STORE_FQ, g.HDFSTORE_COMBINED_1_2_RESULTS_KEY.format(sharelist))
    if len(res_df)==0:
        return []
    cols = res_df.columns
    #print(f'cols={cols}')
    col_specs=[]
    non_condition_cols = ['ShareNumber','ShareName','Date']
    for col in cols:
        if col in non_condition_cols:
            col_entry = {
                'name': col,
                'id': col,
                'selectable': False,
                'type': 'text',
                'hideable': True,
                # formatted "manually"
                #'format':  build_results_fmt(col)
            }
        else:
            # all other columns
            digits_spec=3
            col_entry = {
                'name': col,
                'id': col,
                'selectable': False,
                'type': 'numeric',
                'hideable': True,
                # formatted "manually"
                'format':  build_results_fmt(col,digits_spec),
            }
        col_specs.append(col_entry)

    return col_specs

def build_3jP_datatable_column_dicts(sharelist :str) -> list:

    res_df = get_df_from_store(g._3JP_RESULTS_PART2_STORE_FQ, g.HDFSTORE_3JP_RESULTS_PART2_KEY.format(sharelist))
    if len(res_df)==0:
        return []

    _2nd_headers = {
        'Status': '',
        '_1St.Con_a': 'SDHPGr1sh',
        '_1St.Con_b': 'SDHPGr1m',
        '_1St.Con_c': 'SDHPGr1lo',
        '_1St.Con_d': 'DTF',

        '_2StPr.Con_a1': 'DaysDHPlasthi',
        '_2StPr.Con_a2': 'DaysDHPlasthi3perc',
        '_2StPr.Con_a3': 'DaysDHPlast20hi',
        '_2StPr.Con_b1': '(DHPD/DHOCPD)^0.3',
        '_2StPr.Con_b2': '(DHPD/DHOCPD)^0.4',
        '_2StPr.Con_b3': '(DHPD/DHOCPD)^0.6',
        '_2StPr.Con_b4': '(DHPD/DHOCPD)^0.85',
        '_2StPr.Con_b5': '(DHPD/DHOCPD)^1',
        '_2StPr.Con_c1': '(DHPD/DHPD-1)^0.3',
        '_2StPr.Con_c2': '(DHPD/DHPD-1)^0.4',
        '_2StPr.Con_c3': '(DHPD/DHPD-1)^0.6',
        '_2StPr.Con_c4': '(DHPD/DHPD-1)^0.85',
        '_2StPr.Con_c5': '(DHPD/DHPD-1)^1',
        '_2StPr.Con_d1': '(DHPD/DHPD-2)^0.3',
        '_2StPr.Con_d2': '(DHPD/DHPD-2)^0.4',
        '_2StPr.Con_d3': '(DHPD/DHPD-2)^0.6',
        '_2StPr.Con_d4': '(DHPD/DHPD-2)^0.85',
        '_2StPr.Con_d5': '(DHPD/DHPD-2)^1',
        '_2StPr.Con_e1': '(DHPD/DHPD-3)^0.3',
        '_2StPr.Con_e2': '(DHPD/DHPD-3)^0.4',
        '_2StPr.Con_e3': '(DHPD/DHPD-3)^0.6',
        '_2StPr.Con_e4': '(DHPD/DHPD-3)^0.85',
        '_2StPr.Con_e5': '(DHPD/DHPD-3)^1',
        '_2StPr.Con_f': 'DHPGrAvLo',
        '_2StPr.Con_g': 'DHPGr',
        '_2StPr.Con_h': 'DHPGrAvLo',
        '_2StPr.Con_i': 'DHPGrAvSh',
        '_2StPr.Con_j': 'SBr',

        '_2StVols.Con_a1': 'DVFf3',
        '_2StVols.Con_a2': 'DV/SDVBf.D-2',
        '_2StVols.Con_b': 'DVFf1/C2Vcb',
        '_2StVols.Con_c': 'DVFm',
        '_2StVols.Con_d': 'DVFsl',
        '_2StVols.Con_e': 'DVFf2',
        '_2StVols.Con_f': 'DV',
        '3. StjP1': '',
        'DjP': '',
    }

    id_colspec={
        'name': 'id',
        'id': 'id',
        'selectable': False,
    }
    col_specs = [id_colspec]

    cols = res_df.columns
    #print(cols)
    #col_specs=[]
    non_condition_cols = ['ShareName','Date'] #['ShareNumber','ShareName','Date']
    for col in cols:
        if col in non_condition_cols:
            col_entry = {
                'name': [col,''],
                'id': col,
                'selectable': False,
                'type': 'text',
                'hideable': True,
                # formatted "manually"
                #'format':  build_results_fmt(col)
            }
        else:
            if col=='ShareNumber': # we dont want to display this column
                continue 
            # all other columns
            digits_spec=3
            col_entry = {
                #'name': [col,''],
                'name': [col,_2nd_headers[col]],
                'id': col,
                'selectable': False,
                'type': 'numeric',
                'hideable': True,
                # formatted "manually"
                'format':  build_results_fmt(col,digits_spec)
            }
        col_specs.append(col_entry)

    return col_specs

def build_3V2d_datatable_column_dicts(sharelist :str) -> list:

    res_df = get_df_from_store(g._3V2D_RESULTS_STORE_FQ, g.HDFSTORE_3V2D_RESULTS_KEY.format(sharelist))
    if len(res_df)==0:
        return []


    _2nd_headers = {
        'Status': '',
        'RbSDV.D-4': '',
        'RbSDV.D-7': '',
        '_1St.Con_a': 'SDHPGr1sh',
        '_1St.Con_b': 'SDHPGr1m',
        '_1St.Con_c': 'SDHPGr1lo',
        '_1St.Con_d': 'DTF',
        '_2StVols.Con_e': 'DVFf2',
        'RbSDV.D-7÷RbSDV.D-4': ''
    }


    #res_df won't have a ShareNumber col (its curently the index) - we want one
    res_df['ShareNumber'] = res_df.index
    # this column is now at the end - we want it to be first

    #print(f'res_df.columns={res_df.columns}')
    #['Status', 'ShareName', 'Date', 'RbSDV.D-4', 'RbSDV.D-7', '_1St.Con_a',
    # '_1St.Con_b', '_1St.Con_c', '_1St.Con_d', '_2StVols.Con_e',
    # 'RbSDV.D-7÷RbSDV.D-4', 'ShareNumber']
    
    if len(res_df.columns)==12:
        # drop Status column
        res_df = res_df[res_df.columns[[1,2,3,4,5,6,7,8,9,10]]]

    cols = res_df.columns

    id_colspec={
        'name': 'id',
        'id': 'id',
        'selectable': False,
    }
    col_specs = [id_colspec]
    #col_specs=[]
    non_condition_cols = ['ShareName','Date'] #['ShareNumber','ShareName','Date']
    for col in cols:
        if col in non_condition_cols:
            col_entry = {
                'name': [col,''],
                'id': col,
                'selectable': False,
                'type': 'text',
                'hideable': True,
                # formatted "manually"
                #'format':  build_results_fmt(col)
            }
        else:
            # all other columns
            if col == 'ShareNumber': # dont want 
                continue
            digits_spec=3
            col_entry = {
                #'name': col,
                'name': [col,_2nd_headers[col]], 
                'id': col,
                'selectable': False,
                'type': 'numeric',
                'hideable': True,
                # formatted "manually"
                'format':  build_results_fmt(col,digits_spec)
            }
        col_specs.append(col_entry)

    return col_specs

def build_3nH_datatable_column_dicts(sharelist :str) -> list:

    res_df = get_df_from_store(g._3NH_RESULTS_STORE_FQ, g.HDFSTORE_3NH_RESULTS_KEY.format(sharelist))
    if len(res_df)==0:
        return []
    cols = res_df.columns

    id_colspec={
        'name': 'id',
        'id': 'id',
        'selectable': False,
    }
    col_specs = [id_colspec]
    #col_specs=[]
    non_condition_cols = ['ShareName','Date'] #['ShareNumber','ShareName','Date']
    for col in cols:
        if col in non_condition_cols:
            col_entry = {
                'name': col,
                'id': col,
                'selectable': False,
                'type': 'text',
                'hideable': True,
                # formatted "manually"
                #'format':  build_results_fmt(col)
            }
        else:
            # all other columns
            if col == 'ShareNumber' or col == 'Status' : # dont want
                continue
            digits_spec=3
            col_entry = {
                'name': col,
                'id': col,
                'selectable': False,
                'type': 'numeric',
                'hideable': True,
                # formatted "manually"
                'format':  build_results_fmt(col,digits_spec)
            }
        col_specs.append(col_entry)

    return col_specs


def build_1St_results_datatable_column_dicts(res_table, extra_audit_cols :list, col_under_audit :str) -> list:
    """ finely specified column dicts for the Dash datatable """

    # native 'manual' 'format' valid keys: 'locale', 'nully','prefix','specifier'
    # see alternative 'Format()' options here: https://github.com/plotly/dash-table/blob/dev/dash_table/Format.py

    # for now, we ignore res_table

    id_colspec={
        'name': 'id',
        'id': 'id',
        'selectable': False,
    }
    col_specs = [id_colspec]

    non_condition_cols = ['ShareNumber','ShareName','Date'] #['ShareNumber','Status','ShareName','Date']
    digits_spec = 3
   
    _2nd_headers = {
        'Con_a': 'SDHPGr1sh',
        'Con_b': 'SDHPGr1m',
        'Con_c': 'SDHPGr1lo',
        'Con_d': 'DTF',
    }

    if res_table=='1St':    
        # left hand 3 cols
        cols = [col for col in non_condition_cols]
        # augment by appending main list of columns
        for key in _1St_conditions.keys():
            if col_under_audit=='' or key==col_under_audit:
                cols.append(key)
        # and again the extra audit cols
        for ov_audit_col in extra_audit_cols:
            cols.append(ov_audit_col)

        for col in cols:
            if col in non_condition_cols:
                col_entry = {
                    'name': [col,''],
                    'id': col,
                    'selectable': False,
                    'type': 'text',
                    'hideable': True,
                    # formatted "manually"
                    #'format':  build_results_fmt(col)
                }
            else:
                # all other columns
                digits_spec=8 if col in extra_audit_cols else 3
                col_entry = {
                    'name': [col[4:],_2nd_headers[col]] if col not in extra_audit_cols else col,
                    'id': col,
                    'selectable': col not in extra_audit_cols,
                    'type': 'numeric',
                    'hideable': True if col not in extra_audit_cols else False, # and col != col_under_audit else False,
                    # formatted "manually"
                    'format':  build_results_fmt(col,digits_spec)
                }
            col_specs.append(col_entry)

    #print(col_specs)
    return col_specs


def build_2StPr_results_datatable_column_dicts(res_table, extra_audit_cols :list, col_under_audit :str) -> list:
    """ finely specified column dicts for the Dash datatable """

    id_colspec={
        'name': 'id',
        'id': 'id',
        'selectable': False,
    }
    col_specs = [id_colspec]

    digits_spec = 3
    non_condition_cols = ['ShareName','Date'] #['ShareNumber','Status','ShareName','Date']

    _2nd_headers = {
        'Con_a1': 'DaysDHPlasthi',
        'Con_a2': 'DaysDHPlasthi3perc',
        'Con_a3': 'DaysDHPlast20hi',
        'Con_b1': '(DHPD/DHOCPD)^0.3',
        'Con_b2': '(DHPD/DHOCPD)^0.4',
        'Con_b3': '(DHPD/DHOCPD)^0.6',
        'Con_b4': '(DHPD/DHOCPD)^0.85',
        'Con_b5': '(DHPD/DHOCPD)^1',
        'Con_c1': '(DHPD/DHPD-1)^0.3',
        'Con_c2': '(DHPD/DHPD-1)^0.4',
        'Con_c3': '(DHPD/DHPD-1)^0.6',
        'Con_c4': '(DHPD/DHPD-1)^0.85',
        'Con_c5': '(DHPD/DHPD-1)^1',
        'Con_d1': '(DHPD/DHPD-2)^0.3',
        'Con_d2': '(DHPD/DHPD-2)^0.4',
        'Con_d3': '(DHPD/DHPD-2)^0.6',
        'Con_d4': '(DHPD/DHPD-2)^0.85',
        'Con_d5': '(DHPD/DHPD-2)^1',
        'Con_e1': '(DHPD/DHPD-3)^0.3',
        'Con_e2': '(DHPD/DHPD-3)^0.4',
        'Con_e3': '(DHPD/DHPD-3)^0.6',
        'Con_e4': '(DHPD/DHPD-3)^0.85',
        'Con_e5': '(DHPD/DHPD-3)^1',
        'Con_f': 'DHPGrAvLo',
        'Con_g': 'DHPGr',
        'Con_h': 'DHPGrAvLo',
        'Con_i': 'DHPGrAvSh',
        'Con_j': 'SBr',
    }

    if res_table=='2StPr':    
        # left hand 3 cols
        cols = [col for col in non_condition_cols]
        # augment by appending main list of columns
        for key in _2StPr_conditions.keys():
            if col_under_audit=='' or key==col_under_audit:
                cols.append(key)
        # and again the extra audit cols
        for ov_audit_col in extra_audit_cols:
            cols.append(ov_audit_col)

        for col in cols:
            if col in non_condition_cols:
                col_entry = {
                    'name': [col,''],
                    'id': col,
                    'selectable': False,
                    'type': 'text',
                    'hideable': True,
                    # formatted "manually"
                    #'format':  build_results_fmt(col)
                }
            else:
                # all other columns
                digits_spec=8 if col in extra_audit_cols else 3
                col_entry = {
                    'name': [col[4:],_2nd_headers[col]] if col not in extra_audit_cols else col,
                    'id': col,
                    'selectable': col not in extra_audit_cols,
                    'type': 'numeric',
                    'hideable': True if col not in extra_audit_cols else False, # and col != col_under_audit else False,
                    # formatted "manually"
                    'format':  build_results_fmt(col,digits_spec)
                }
            col_specs.append(col_entry)

    return col_specs


def build_2StVols_results_datatable_column_dicts(res_table, extra_audit_cols :list, col_under_audit :str) -> list:
    """ finely specified column dicts for the Dash datatable """

    id_colspec={
        'name': 'id',
        'id': 'id',
        'selectable': False,
    }
    col_specs = [id_colspec]
    digits_spec = 3
    non_condition_cols = ['ShareName','Date'] #['ShareNumber','Status','ShareName','Date']
    # these are the values which get put into the 2rnd header row for the conditions
    # to show the user the value being used as a criterion or the first value in a compound condition
    _2nd_headers = {
        'Con_a1': 'DVFf3',
        'Con_a2': 'DV/SDVBf.D-2',
        'Con_b': 'DVFf1',
        'Con_c': 'DVFm',
        'Con_d': 'DVFsl',
        'Con_e': 'Vlse', #'DVFf2',
        'Con_f': 'Vlsf' #'DV',
    }

    if res_table=='2StVols':    
        # left hand 3 cols
        cols = [col for col in non_condition_cols]
        # augment by appending main list of columns
        for key in _2StVols_conditions.keys():
            if col_under_audit=='' or key==col_under_audit:
                cols.append(key)
        # and again the extra audit cols
        for ov_audit_col in extra_audit_cols:
            cols.append(ov_audit_col)

        for col in cols:
            if col in non_condition_cols:
                col_entry = {
                    'name': [col,''],
                    'id': col,
                    'selectable': False,
                    'type': 'text',
                    'hideable': True,
                    # formatted "manually"
                    #'format':  build_results_fmt(col)
                }
            else:
                # all other columns
                digits_spec=8 if col in extra_audit_cols else 3
                col_entry = {
                    'name': [col[4:],_2nd_headers[col]] if col not in extra_audit_cols else col,
                    'id': col,
                    'selectable': col not in extra_audit_cols,
                    'type': 'numeric',
                    'hideable': True if col not in extra_audit_cols else False, # and col != col_under_audit else False,
                    # formatted "manually"
                    'format':  build_results_fmt(col,digits_spec)
                }
            col_specs.append(col_entry)

    return col_specs


def build_frt_datatable_column_dicts(sharelist :str, cols_on_view :list) -> list:

    res_df = get_df_from_store(g._FRT_RESULTS_STORE_FQ, g.HDFSTORE_FRT_RESULTS_KEY.format(sharelist))
    if len(res_df)==0:
        return []

    # _2nd_headers = {
    #     'Status': '',
    #     'RbSDV.D-4': '',
    #     'RbSDV.D-7': '',
    #     '_1St.Con_a': 'SDHPGr1sh',
    #     '_1St.Con_b': 'SDHPGr1m',
    #     '_1St.Con_c': 'SDHPGr1lo',
    #     '_1St.Con_d': 'DTF',
    #     '_2StVols.Con_e': 'DVFf2',
    #     'RbSDV.D-7÷RbSDV.D-4': ''
    # }

    #res_df won't have a ShareNumber col (its curently the index) - we want one
    res_df['ShareNumber'] = res_df.index
    # this column is now at the end - we want it to be first
    # if len(res_df.columns)==12:
    #     res_df = res_df[res_df.columns[[11,0,1,2,3,4,5,6,7,8,9,10]]]
    #print(f'res_df.columns={res_df.columns}')

    cols = res_df.columns

    id_colspec={
        'name': 'id',
        'id': 'id',
        'selectable': False,
    }
    col_specs = [id_colspec]
    #col_specs=[]
    non_condition_cols = ['ShareNumber','ShareName','Date','Status']
    for col in cols:
        #show ALL columns if cols_on_view is empty
        if len(cols_on_view)>0 and col not in cols_on_view:
            continue
        if col in non_condition_cols:
            col_entry = {
                'name': col,
                'id': col,
                'selectable': False,
                'type': 'text',
                'hideable': True,
                # formatted "manually"
                #'format':  build_results_fmt(col)
            }
        else:
            # all other columns
            digits_spec=frt_columns.FRT_COLS_DIGITS[col]
            col_entry = {
                'name': col,
                #'name': [col,_2nd_headers[col]], 
                'id': col,
                'selectable': False,
                'type': 'numeric',
                'hideable': True,
                # formatted "manually"
                'format':  build_results_fmt(col,digits_spec)
            }
        col_specs.append(col_entry)

    return col_specs



def get_res_dataframe_as_dict(which_results_table :str, sharelist :str, ov_audit_cols, suppression_spec :str = ''):
    """ extract share dataframe from HDFStore """

    data_store = None
    data_store_key = None

    # if ov_audit_cols has content, we're going to have to grab an Ov
    ov_df = None
    if len(ov_audit_cols) > 0:
        try:
            #print(sharelist)
            data_store = pd.HDFStore(g.OVERVIEW_STORE_FQ.format(2))
            ov_key = g.HDFSTORE_OV_KEY.format(sharelist,2)
            print(f'loading ov (audit purposes) {g.OVERVIEW_STORE_FQ.format(2)} using key {ov_key}')

            ov_df = data_store[ov_key]
            # strip duplicates (should NOT be required) 
            if not ov_df.index.is_unique:
                ov_df = ov_df.loc[~ov_df.index.duplicated(), :]
        except KeyError as ke:
            print(f"Key '{ov_key}' error {ke}")
        finally:
            data_store.close()

    data_store_fn = 'fn?'
    data_store_key = 'key?'
    if which_results_table=='1St':
        data_store_fn = g._1ST_RESULTS_STORE_FQ
        data_store_key = g.HDFSTORE_1ST_RESULTS_KEY.format(sharelist)
    elif which_results_table=='2StPr':
        data_store_fn = g._2STPR_RESULTS_STORE_FQ
        data_store_key = g.HDFSTORE_2STPR_RESULTS_KEY.format(sharelist)
    elif which_results_table=='2StVols':
        data_store_fn = g._2STVOLS_RESULTS_STORE_FQ
        data_store_key = g.HDFSTORE_2STVOLS_RESULTS_KEY.format(sharelist)
    elif which_results_table=='combined_1_2':
        data_store_fn = g._COMBINED_1_2_RESULTS_STORE_FQ
        data_store_key = g.HDFSTORE_COMBINED_1_2_RESULTS_KEY.format(sharelist)
    elif which_results_table=='3jP_part1':
        data_store_fn = g._3JP_RESULTS_PART1_STORE_FQ
        data_store_key = g.HDFSTORE_3JP_RESULTS_PART1_KEY.format(sharelist)
    elif which_results_table=='3jP_part2': 
        data_store_fn = g._3JP_RESULTS_PART2_STORE_FQ
        data_store_key = g.HDFSTORE_3JP_RESULTS_PART2_KEY.format(sharelist)
    elif which_results_table=='3V2d':
        data_store_fn = g._3V2D_RESULTS_STORE_FQ
        data_store_key = g.HDFSTORE_3V2D_RESULTS_KEY.format(sharelist)
    elif which_results_table=='3nH':
        data_store_fn = g._3NH_RESULTS_STORE_FQ
        data_store_key = g.HDFSTORE_3NH_RESULTS_KEY.format(sharelist)
    elif which_results_table=='FRT':
        data_store_fn = g._FRT_RESULTS_STORE_FQ
        data_store_key = g.HDFSTORE_FRT_RESULTS_KEY.format(sharelist)

    if not exists(data_store_fn):
        print(f'results store {data_store_fn} not found. Have you run the command to create these results?')
        return None

    try:
        # extract previously (recently) stored results dataframe
        print(f'loading results from {data_store_fn} using key {data_store_key}')
        data_store = pd.HDFStore(data_store_fn)
        df = data_store[data_store_key]

        # df_reduced = df.loc[:, 'price':'SPe']
        #df.reset_index(inplace=True)
        #df['ShareNumber'] = df.index
        # this removes the index and makes it ('ShareNumber) as a plain column
        if 'ShareNumber' in df.columns:
            del df['ShareNumber']

        df.reset_index(inplace=True)
        
        # we need a numbered id column for the Datatable
        # NOTE add an id column
        df['id'] = df.index
        #print(df.head(1))

        # needed for row identifaction eg when clicking on a row
        #df['id'] = df['ShareNumber']

        # leave at NATIVE filtering for now since we get problems with handling OR
        # DASH custom filtering

        # for ov_col in ov_audit_cols:
        #     df[ov_col] = ov_df[ov_col]

        if len(ov_audit_cols) > 0:
            for audit_col in ov_audit_cols:
                df[audit_col] = ov_df[audit_col]

        # blank out numbers if required
        #print(f"suppression_spec={suppression_spec}")
        if suppression_spec=='passing_only':
            df = df.replace(to_replace=r'🗙', value=NaN, regex=True)
        elif suppression_spec=='failing_only':
            df = df.replace(to_replace=r'✓', value=NaN, regex=True)


        dff = df

        return dff.to_dict('records')

    except AssertionError as ae:
        logging.error(f'Assertion Error {ae}')
        return None

    except KeyError as ke:
        # print(f'Key Error {ke}')
        logging.error(f"Key '{data_store_key}' Error {ke}")
        return None

    finally:
        data_store.close()

def build_results_datatable_col_tooltips(df_columns :list, tooltips_dict :dict) -> dict:
    ''' create column tooltips list for columns of dp_results dataframe '''

    tips = {}
    for con_group in tooltips_dict.keys(): # 'a', 'b', 'c',..
        if isinstance(tooltips_dict[con_group], dict):
            for cond_col in tooltips_dict[con_group].keys(): #'Con_b1', 'Con_b2', ...
                #print(cond_col)
                #tips[cond_col] = 'influenced by: ' + ','.join(tooltips_dict[con_group][cond_col]['audit_list'])                
                condition = tooltips_dict[con_group][cond_col].copy()
                condition.pop('name')
                condition.pop('group')
                #condition.pop('audit_list')
                condition_json = json.dumps(condition, indent=4)
                condition_json = condition_json[1:-1] # effectively remove enclosing '{' and '}'
                condition_json += '  \nAdjust these parameters on the *Conditions* tab'
                #inject double spaces before each newline in order to force markdown line breaks
                md = condition_json.replace('\n','  \n')                
                md = md.replace('"description":','"desc":',1)
                #md = md.replace('{',f'### {cond_col}  ',1) # double trailing spaces must remain
                md = md.replace('"','')
                tips[cond_col] = { 'value': md,
                                    'type': 'markdown' }
    
    return tips

def display_results_report(kind :str) ->str:

    report_file_fq = g.REPORTS_PATH + f"\\{kind}_results_report.txt"
    scrubbed_md_fq = report_file_fq.replace("\\","|") #.replace("|","\\")
    report = f'{scrubbed_md_fq} not found'
    if exists(report_file_fq):
        f = open(report_file_fq, "r")
        report = f.read()
        f.close
    return report + "\n---  " #click *Load Share results* button to view result by share\n"

def get_overview_key_options() ->list:
    ''' inspect HDFStores for the keys of stored Overview dataframes and 
        return radio button compatible options - both stage 1 & 2 are looked for
    ''' 
    options=[]
    #stage 1 store
    try:
        data_store1 = pd.HDFStore(g.OVERVIEW_STORE_FQ.format(1))
        for key in data_store1.keys():
            option_label = key[1:]  # key = eg '\Default_1'
            option_label = option_label.replace('_1',' sharelist (minutely)')
            option_label = option_label.replace('sharelist','')
            options.append({'label': option_label, 'value':key[1:] })
    except:
        pass
    finally:
        data_store1.close()

    #stage 2 store
    _3nh_daily_index=-1
    try:
        data_store2 = pd.HDFStore(g.OVERVIEW_STORE_FQ.format(2))
        i=len(options) # take into account the exist minutely options
        for key in data_store2.keys():
            option_label = key[1:]  # key = eg '\Default_2'
            option_label = option_label.replace('_2',' sharelist (daily)')
            option_label = option_label.replace('sharelist','')
            options.append({'label': option_label, 'value':key[1:] })
            #print(option_label)
            if option_label.startswith('results_3nH  (daily)'):
                #we capture this because it must be forced to be the last one
                _3nh_daily_index=i
            i=i+1
        #print(f'_3nh_index={_3nh_daily_index}')
        if _3nh_daily_index >= 0:
            #we captured it, force it to the end    
            option_at_end = options[_3nh_daily_index]
            options.remove(option_at_end)
            options.append(option_at_end)
    except:
        pass
    finally:
        data_store2.close()

    #print(options)
    return options

def get_overview_key_default_value(wanted) ->list:
    ''' return the 1st stage 1 key from an Overview stage 1 HDFStore
        suitable for use as the default radio button value
    ''' 
    options=[]
    i=0
    target=0
    try:
        # NB we reference stage_2 store only, since its a 'Daily' we assume as a default
        data_store1 = pd.HDFStore(g.OVERVIEW_STORE_FQ.format(2))
        for key in data_store1.keys():
            option_label = key[1:] # key = eg '\Default_1'
            if option_label==wanted: # eg 'Default_2'
                target=i
            option_label = option_label.replace('_1',' sharelist (minutely)')
            options.append({'label': option_label, 'value':key[1:] })
            i = i+1
    except:
        pass
    finally:
        data_store1.close()

    if len(options)>0:        
        return options[target]['value']
    else:
        return None


# def get_results_key_options(store_fq :str) ->list:
#     ''' this routine replaces the commented out one below due to there being a BUG in the HDFStore keys() function'''

#     # [
#     # {'label': 'Default  (minutely)', 'value': 'Default_1'}, 
#     # {'label': 'results_3jP  (minutely)', 'value': 'results_3jP_1'}, 
#     # {'label': 'results_3nH  (minutely)', 'value': 'results_3nH_1'}, 
#     # {'label': 'results_V2d  (minutely)', 'value': 'results_V2d_1'}, 
#     # {'label': 'Default  (daily)', 'value': 'Default_2'}, 
#     # {'label': 'results_3jP  (daily)', 'value': 'results_3jP_2'}, 
#     # {'label': 'results_V2d  (daily)', 'value': 'results_V2d_2'}, 
#     # {'label': 'results_3nH  (daily)', 'value': 'results_3nH_2'}
#     # ]

#     print(store_fq)
#     # return hardcoded list
#     options = [
#         {'label': 'Default  (daily)', 'value': 'Default_2'}, 
#     ]

#     return options

def get_results_key_options(store_fq :str) ->list:
    ''' inspect HDFStore for the keys of stored Results dataframes and 
        return radio button compatible options 
    ''' 


    options=[]
    try:
        data_store = pd.HDFStore(store_fq)

        for key in data_store.keys(): 
            option_label = key[1:]  # key = eg '\Default_1'
            options.append({'label': option_label, 'value':key[1:] })

    except Exception as exc:
        print(exc)
    finally:
        data_store.close()

    return options

def get_results_key_default_value(store_fq :str) ->list:
    ''' return the 1st stage 1 Results key from the Results HDFStore
        suitable for use as the default radio button value
    ''' 

    options=[]
    try:
        data_store = pd.HDFStore(store_fq)
        for key in data_store.keys():
            option_label = key[1:] # key = eg '\Default_1'
            options.append({'label': option_label, 'value':key[1:] })
    except:
        pass
    finally:
        data_store.close()

    # print(store_fq)
    # print(options)

    if len(options) > 0:
        return options[0]['value']
    else:
        return None

def assign_global_at_plot_values(last_plot_tuple):

    g.at_plot_figure = last_plot_tuple[0]
    g.at_plot_df_datetime_col = last_plot_tuple[1]
    g.at_plot_share_name_num = last_plot_tuple[2]
    g.at_plot_stage_cols = last_plot_tuple[3]
    g.at_plot_stage = last_plot_tuple[4]
    g.at_plot_data_source = last_plot_tuple[5]


def striped_and_numeric():

    return  [
        {
            'if': {
                'row_index': 'odd',  # number | 'odd' | 'even'
                # 'column_id': 'date_time'
            },
            'backgroundColor': 'ghostwhite',
            # 'color': 'white'
        },
        {
            'if': {
                'column_type': 'numeric',
            },
            'textAlign': 'right',
        }
    ]


def red_failures(condition_columns=None):

    if condition_columns is not None:
        outlist = striped_and_numeric() + [
                {
                    'if': {
                        'filter_query': '{{{}}} contains 🗙'.format(col),
                        'column_id': col
                    },
                    'color': 'red'
                } for col in condition_columns
        ]      
        return  outlist
    else:
        return striped_and_numeric()

at_data_style = striped_and_numeric() + [
        {
            'if': {
                'column_id': 'price',
            },
            # 'backgroundColor': 'dodgerblue',
            'color': 'blue',
            'fontWeight': 'bold',
        }
    ]

ov_data_style = striped_and_numeric() + [
        {
            'if': {
                'column_id': 'ShareNumber',
            },
            # 'backgroundColor': 'dodgerblue',
            'color': 'blue',
            'fontWeight': 'bold',
        }
    ]


def init_page_size_input(page_size_setting_name):

    return g.CONFIG_RUNTIME[page_size_setting_name]
