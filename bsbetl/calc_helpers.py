import datetime
import logging
import os
import sys
from datetime import date, timedelta
from os.path import exists
from pandas.tseries.offsets import *

import numpy as np
import pandas as pd
from numpy.core.arrayprint import _formatArray
from pandas._libs.tslibs import Timedelta, Timestamp

from bsbetl import g
from bsbetl.func_helpers import save_runtime_config
from bsbetl.helpers import append_csv_maxsize_log
from bsbetl.ov_calcs import ov_columns


def ov_dataframe_to_store(df: pd.DataFrame, overview_key: str, stage: int, sharelist_name :str):
    """ save overview dataframe to HDFStore """

    assert sharelist_name in overview_key, "ov_dataframe_to_store must have sharelist_name in its key"

    ov_fn = g.OVERVIEW_STORE_FQ.format(stage)
    data_store = pd.HDFStore(ov_fn)
    # we need a 'natural name' for the key
    ov_key=overview_key.replace('.shl','')
    data_store[ov_key] = df
    data_store.close()
    logging.info(f"saved {ov_fn} under key {ov_key}")

def _1St_results_dataframe_to_store(df: pd.DataFrame, sharelist :str):
    """ save dataframe to HDFStore """

    #df.to_hdf(g._1ST_RESULTS_STORE_FQ,key=g.HDFSTORE_1ST_RESULTS_KEY,mode='w',format='table')

    data_store = pd.HDFStore(g._1ST_RESULTS_STORE_FQ)
    #data_store[g.HDFSTORE_1ST_RESULTS_KEY] = df
    data_store.put(key=g.HDFSTORE_1ST_RESULTS_KEY.format(sharelist.replace('.shl','')),value=df,format='fixed')

    logging.info(f'saved 1St results to _1ST_RESULTS datastore ({df.shape[0]} rows) under key {sharelist}')
    data_store.close()

def _2StPr_results_dataframe_to_store(df: pd.DataFrame, sharelist :str):
    """ save dataframe to HDFStore """

    data_store = pd.HDFStore(g._2STPR_RESULTS_STORE_FQ)
    store_key = g.HDFSTORE_2STPR_RESULTS_KEY.format(sharelist.replace('.shl',''))
    data_store.put(key=store_key,value=df,format='fixed')

    logging.info(f'saved 2StPr results to _2STPR_RESULTS datastore ({df.shape[0]} rows) under key {sharelist}')
    data_store.close()

def _2StVols_results_dataframe_to_store(df: pd.DataFrame, sharelist :str):
    """ save dataframe to HDFStore """

    data_store = pd.HDFStore(g._2STVOLS_RESULTS_STORE_FQ)
    data_store.put(key=g.HDFSTORE_2STVOLS_RESULTS_KEY.format(sharelist.replace('.shl','')),value=df,format='fixed')

    logging.info(f'saved 2StVols results to _2STVOLS_RESULTS datastore ({df.shape[0]} rows) under key {sharelist}')
    data_store.close()

def _combined_1_2_results_dataframe_to_store(df: pd.DataFrame, sharelist :str):
    """ save dataframe to HDFStore """

    store_fn = g._COMBINED_1_2_RESULTS_STORE_FQ
    store_key=g.HDFSTORE_COMBINED_1_2_RESULTS_KEY.format(sharelist.replace('.shl',''))
    logging.info(f'saving combined_1_2 results to {store_fn} under key {store_key} ({df.shape[0]} rows)')

    data_store = pd.HDFStore(store_fn)
    data_store.put(key=store_key, value=df, format='fixed')
    data_store.close()


def _3jP_results_dataframe_to_store(df: pd.DataFrame, sharelist :str, which_part):
    """ save dataframe to HDFStore """

    if which_part=='_3jP_part1':
        data_store = pd.HDFStore(g._3JP_RESULTS_PART1_STORE_FQ)
        filekey=g.HDFSTORE_3JP_RESULTS_PART1_KEY.format(sharelist.replace('.shl',''))

        data_store.put(key=filekey,value=df,format='fixed')
        logging.info(f"saved 3jP part 1 results to {g._3JP_RESULTS_PART1_STORE_FQ} datastore under key '{filekey}' ({df.shape[0]} rows)")
        data_store.close()
    elif which_part=='_3jP_part2':
        data_store = pd.HDFStore(g._3JP_RESULTS_PART2_STORE_FQ)
        filekey=g.HDFSTORE_3JP_RESULTS_PART2_KEY.format(sharelist.replace('.shl',''))

        data_store.put(key=filekey,value=df,format='fixed')
        logging.info(f"saved 3jP part 2 results to {g._3JP_RESULTS_PART2_STORE_FQ} datastore under key '{filekey}' ({df.shape[0]} rows)")
        data_store.close()
    else: # final
        data_store = pd.HDFStore(g._3JP_RESULTS_FINAL_STORE_FQ)
        filekey=g.HDFSTORE_3JP_RESULTS_FINAL_KEY.format(sharelist.replace('.shl',''))

        data_store.put(key=filekey,value=df,format='fixed')
        logging.info(f"saved 3jP final results to {g._3JP_RESULTS_FINAL_FQ} datastore under key '{filekey}' ({df.shape[0]} rows)")
        data_store.close()


def _3V2d_results_dataframe_to_store(df: pd.DataFrame, sharelist :str):
    """ save dataframe to HDFStore """

    data_store = pd.HDFStore(g._3V2D_RESULTS_STORE_FQ)
    filekey=g.HDFSTORE_3V2D_RESULTS_KEY.format(sharelist.replace('.shl',''))

    data_store.put(key=filekey, value=df, format='fixed')

    logging.info(f"saved 3V2d results to {g._3V2D_RESULTS_STORE_FQ} datastore under key '{filekey}' ({df.shape[0]} rows)")
    data_store.close()

def _3nH_results_dataframe_to_store(df: pd.DataFrame, sharelist :str):
    """ save dataframe to HDFStore """

    data_store = pd.HDFStore(g._3NH_RESULTS_STORE_FQ)
    filekey=g.HDFSTORE_3NH_RESULTS_KEY.format(sharelist.replace('.shl',''))

    data_store.put(key=filekey, value=df, format='fixed')

    logging.info(f"saved 3nH results to {g._3NH_RESULTS_STORE_FQ} datastore under key '{filekey}' ({df.shape[0]} rows)")
    data_store.close()

def frt_results_dataframe_to_store(df: pd.DataFrame, sharelist :str):
    """ save dataframe to HDFStore """

    data_store = pd.HDFStore(g._FRT_RESULTS_STORE_FQ)
    filekey=g.HDFSTORE_FRT_RESULTS_KEY.format(sharelist.replace('.shl',''))

    data_store.put(key=filekey, value=df, format='fixed')

    logging.info(f"saved FRT results to {g._FRT_RESULTS_STORE_FQ} datastore under key '{filekey}' ({df.shape[0]} rows)")
    data_store.close()



def share_dataframe_to_store(df: pd.DataFrame, share_num: str, stage: int):
    """ save share dataframe to HDFStore

    NOTE Existing dataframe, if any, gets replaced
    """

    data_store = pd.HDFStore(g.SHARE_STORE_FQ.format(stage))
    # we need a 'natural name' for the key
    natural_key = share_num[-3:] + '_' + share_num[0:-4]

    data_store[natural_key] = df  # alternative 'table' format below
    # df.to_hdf(g.SHARE_STORE_FQ, natural_key, format="table")

    logging.info(f'saved {natural_key} in SHARES_{stage} datastore')
    data_store.close()


def add_calc_columns(df_bh: pd.DataFrame):
    """  Add all extra required columns to df_bh Note: price & volume - assumed present """

    for col in g.AT_COLS[2:]:  # skip price and volume
        arr = np.zeros(len(df_bh.index))
        arr[:] = np.nan
        df_bh[col] = arr


def check_share_num(value: str) -> bool:

    ok = False
    for index, bourse in enumerate(g.BOURSES_LIST):
        if value.endswith(bourse):
            ok = True
            break

    return ok


def get_sharelist_list(sharelist_name_fq: str) -> list:
    """ return a list of (share_name, share_number) tuples """

    sharelist_shares = []
    if exists(sharelist_name_fq):
        with open(sharelist_name_fq, "r", encoding='utf8') as shlf:
            sharelist_line = shlf.readline()  # skip assumed header share_number,sharename
            if sharelist_line.startswith(g.SHARELIST_HEADER):
                sharelist_line = shlf.readline()  # if header, skip
            while sharelist_line:
                share_name = sharelist_line[:31].rstrip()
                share_number = sharelist_line[31:].rstrip()
                if not share_number.endswith('None.ETR'):
                    sharelist_shares.append((share_name, share_number))
                sharelist_line = shlf.readline()  # read next dict line

    return sharelist_shares

def create_results_3jP_sharelist():
    ''' create a standard SW sharelist file from the _3jP_list in runtime config '''

    results3_shl_fq = g.SHARELISTS_FOLDER_FQ + '\\' + 'results_3jP.shl'

    with open(results3_shl_fq,'w', encoding='utf8') as shlf:
        #SHARELIST_HEADER = 'share_name                     number'
        shlf.write(f'{g.SHARELIST_HEADER}\n')
        for number_name_list in g.CONFIG_RUNTIME['_3jP_list']:
            share_number = number_name_list[0]
            share_name = number_name_list[1].ljust(31)
            #NOTE name then number despite other way around in PSMV_list
            shlf.write(f'{share_name}{share_number}\n') 

def create_results_V2d_sharelist():
    ''' create a standard SW sharelist file from the _V2d_list in runtime config '''

    shl_fq = g.SHARELISTS_FOLDER_FQ + '\\' + 'results_V2d.shl'

    with open(shl_fq,'w', encoding='utf8') as shlf:
        #SHARELIST_HEADER = 'share_name                     number'
        shlf.write(f'{g.SHARELIST_HEADER}\n')
        for number_name_list in g.CONFIG_RUNTIME['_V2d_list']:
            share_number = number_name_list[0]
            share_name = number_name_list[1].ljust(31)
            #NOTE name then number despite other way around in PSMV_list
            shlf.write(f'{share_name}{share_number}\n') 

def create_results_3nH_sharelist():
    ''' create a standard SW sharelist file from the _3nH_list in runtime config '''

    shl_fq = g.SHARELISTS_FOLDER_FQ + '\\' + 'results_3nH.shl'

    with open(shl_fq,'w', encoding='utf8') as shlf:
        #SHARELIST_HEADER = 'share_name                     number'
        shlf.write(f'{g.SHARELIST_HEADER}\n')
        for number_name_list in g.CONFIG_RUNTIME['_3nH_list']:
            share_number = number_name_list[0]
            share_name = number_name_list[1].ljust(31)
            #NOTE name then number despite other way around in PSMV_list
            shlf.write(f'{share_name}{share_number}\n') 

def sharenum_in_spinoff_list(share_num :str, list_key :str) ->bool:
    ''' decides whether share_num is present in the config_runtime's  x_list'''
    # list_key eg '_3jP_list', '_V2d_list'
    for number_name_list in g.CONFIG_RUNTIME[list_key]:
        if number_name_list[0] == share_num:
            return True
    return False

    
def clear_3jP_list():
    ''' invalidate the list of shares for which M_ParticularSumOfMV gets run'''
    g.CONFIG_RUNTIME['_3jP_list']  = []
    save_runtime_config()

def scrub_csv_footers(csv_file_fq :str):
    ''' get rid of any (esp footer) lines in passed in csv file which start with date_time 
        NOTE we allow the first line header however
    '''

    scrubbed_lines = []
    # select only the good lines  
    lines_scrubbed=0
    with open(csv_file_fq, "r") as inf:
        line_num=0
        for in_line in inf:
            if not in_line.startswith('date_time') or line_num==0:
                scrubbed_lines.append(in_line)
                line_num = line_num+1
            else:
                lines_scrubbed = lines_scrubbed+1

    # write these back to the same csv file
    with open(csv_file_fq, "w") as outf:
        for out_line in scrubbed_lines:
            outf.write(out_line)

    if lines_scrubbed > 0:
        logging.info(f'{lines_scrubbed} unwanted (footer) lines removed from .CSV')

def df_from_csv(share_dest_path: str, share_num: str, share_name: str, start_date: str, end_date :str, stage: int) -> pd.DataFrame:
    """
    Return a dataframe created from the ~.TXT.CSV file for the share with either the full date range or a tail-piece date range,
    as controlled by start_date

    """

    csv_file_fq = f"{share_dest_path}\{share_num}\{share_num}.CSV"
    csv_file_size = os.path.getsize(csv_file_fq)
    if csv_file_size > g.CSV_TRADES_FILESIZE_MAX:
        size_warn = f'{share_name} ({share_num}) trades file {csv_file_fq} is too large! (size {csv_file_size}) Share will be skipped'
        logging.warn(size_warn)
        append_csv_maxsize_log(size_warn)
        return pd.DataFrame()  # an empty DataFrame

    # get rid of unwanted 'date_time,price,volume,vol_cum' footers
    scrub_csv_footers(csv_file_fq)

    # load entire csv file ALL HISTORY
    try:
        df_trades = pd.read_csv(csv_file_fq, index_col='date_time',
                                parse_dates=True, infer_datetime_format=True)
    except:
        # could be eg low memory error
        logging.error(f"Exception in read_csv: {sys.exc_info()[0]}")
        readcsv_warn = f"{share_name} ({share_num}) trades file '{csv_file_fq}' below {g.CSV_TRADES_FILESIZE_MAX} bytes in size, but a pd.read_csv exception still ocurred. Share will be skipped"
        logging.error(readcsv_warn)
        append_csv_maxsize_log(readcsv_warn)
        return pd.DataFrame()  # an empty DataFrame

    if len(df_trades.index) == 0:
        return pd.DataFrame()  # an empty DataFrame

    # we don't need this column
    del df_trades['vol_cum']

    # if we have an end_date, respect it
    if end_date != '':
        start_off_date = start_date.replace('_','-')
        cut_off_date = end_date.replace('_','-')
        #filter on the index
        df_trades = df_trades.loc[start_off_date:cut_off_date].copy()
        logging.debug(f'start_off_date={start_off_date}; Cutting off trades after {cut_off_date}')
        #print(df_trades.tail())
        #exit()

    if stage == 1:

        # before hours trades can occur (mostly from Frankfurt)
        #print(df_trades.index)

        df_early = df_trades.between_time('00:00:00','08:59:59')
        df_early_daily = df_early.resample('D', label='left', origin='start_day').agg(
            {'price': 'mean', 'volume': 'sum'}).pad()
        logging.debug(f'{df_early_daily.shape[0]} days in the period had early trading')

        # after hours trades can occur (mostly from Frankfurt)
        df_late = df_trades.between_time('17:36:00','23:59:59')
        df_late_daily = df_late.resample('D', label='left', origin='start_day').agg(
            {'price': 'mean', 'volume': 'sum'}).pad()
        logging.debug(f'{df_late_daily.shape[0]} days in the period had late trading')

        # now get rid of bands before 09:00:00 and after 17:35 each day
        # (their trades are now captured in df_early and df_late)
        df_trades = df_trades.between_time('09:00:00', '17:35')

        # and append the consolidated early / late trades to 
        # the opening / closing minutes of each day
        for idx,row in df_early_daily.iterrows():
            #ensure these go into the 09:00:00 slot
            row.name = idx + pd.offsets.Hour(9) 
            df_trades = df_trades.append(row,ignore_index=False)

        for idx,row in df_late_daily.iterrows():
            #ensure these go into the 17:35:00 slot
            row.name = idx + pd.offsets.Minute(17*60+35)
            df_trades = df_trades.append(row,ignore_index=False)

        # compact by resampling for minute intervals
        df = df_trades.resample('1Min', label='left', origin='start_day').agg(
            {'price': 'mean', 'volume': 'sum'}).pad()
        df = df[df.index.dayofweek < 5]

        # Prepare a dataframe which will help us to get rid of no-trading weekdays (ie holidays)
        # see https://stackoverflow.com/questions/44900011/how-to-delete-additional-days-added-by-pandas-resample
        # Lets have a dataframe with individual weekdays only -
        # it will be bereft of weekends and public holidays,
        # (since we explicitly remove weekends & there are no trades on public holidays):
        df_wanted_dates = df_trades.index.floor('D')
        df_wanted_dates = df_wanted_dates[df_wanted_dates.dayofweek < 5]

        # prepare a days only df from the 1 min resmapled trades
        df_dates_1min = df.index.floor('D')
        # and get rid of public holidays (no trade weekdays)
        df_unwanted_dates = df_dates_1min.difference(df_wanted_dates)
        # to leave only the wanted dates' trades
        df = df[~df_dates_1min.isin(df_unwanted_dates)]

    else:
        # resample on business days
        df = df_trades.resample('B', label='left', origin='start_day').agg(
            {'price': 'mean', 'volume': 'sum'}).pad()

        df_wanted_dates = df_trades.index.floor('D')
        df_wanted_dates = df_wanted_dates[df_wanted_dates.dayofweek < 5]

        # and get rid of public holidays (no trade weekdays)
        df_unwanted_dates = df.index.difference(df_wanted_dates)
        # print(df_unwanted_dates)

        # to leave only the wanted dates' trades
        df = df[~df.index.isin(df_unwanted_dates)]

    # if stage == 2:
    #     print(share_num)
    #     print(df.tail(5))

    # recall that when topping up, start_date has been determined beforehand
    # and is a more recent date
    start_date_fields = start_date.split('_')
    start_ts = Timestamp(int(start_date_fields[0]), int(
        start_date_fields[1]), int(start_date_fields[2]))

    # use a filter to filter in only the tailing rows from start_date to end of data
    try:
        tail_filter = df.index.to_series().between(start_ts, df.index[-1])
        # so the df now is either a 'smallish' one or a full-one, based
        # on whether we are topping up (former case) or doing a full process-3
        df = df[tail_filter]
    except IndexError as exc:
        pass

    if stage == 1:
        # NOTE shouldnt be necessary
        # get rid of bands before 09:00:00 and after 17:35 each day
        df = df.between_time('09:00:00', '17:35')



    # if stage == 2:
    #     print(df.head())
    #     exit()

    if stage == 1:
        # ensure it doesn't get bigger than 900 trading days
        # assuming 516 'minute' rows in a day
        rows_per_day = 516
        df = df.tail(g.CALCS_MAX_BUSDAYS * rows_per_day)
    else:
        # assuming 1 row = 1 day
        df = df.tail(g.CALCS_MAX_BUSDAYS)

    return df


def initialize_overview(sharelist_tuples: list, stage: int, sharelist_name :str):
    """ create an overview dataframe with sharenames and numbers and zero filled columns """

    ov_cols = [col for col in ov_columns.OV_STAGE_TO_COLS[stage]]
    ov = pd.DataFrame(columns=ov_cols)
    ov.allows_duplicate_labels = False

    # we add a row for each share to the global Overview dataframe, (global to save excessive passing)
    for share_name, share_number in sharelist_tuples:
        ov = ov.append({'ShareNumber': share_number,
                        'ShareName': share_name,
                        'Status': 'no data'}, ignore_index=True)

    ov.set_index('ShareNumber', drop=True, inplace=True)

    # drop duplicate rows in case sharelist tuples above not kosher (should NOT be required) 
    if not ov.index.is_unique:
        ov = ov.loc[~ov.index.duplicated(), :]

    ov = ov.fillna(0.0)
    ov['Lazy'] = True

    # if we're initializing a stage 2 overview, we can already carry forward
    # certain columns as duplicated values already computed in stage 1
    if stage == 2:
        data_store = pd.HDFStore(g.OVERVIEW_STORE_FQ.format(1))
        try:
            # extract dataframe
            df_ov1 = data_store[g.HDFSTORE_OV_KEY.format(sharelist_name.replace('.shl',''),1)]

            # drop duplicate rows in case necessary (should NOT BE!)
            if not df_ov1.index.is_unique:
                df_ov1 = df_ov1.loc[~df_ov1.index.duplicated(), :]

            # grab these columns from the stage1 Ov and lay over the current Ov we're initializing
            # should align on share number
            # for stage1_col in ov_columns.OV_STAGE1_CARRY_FORWARDS:
            #     ov[stage1_col] = df_ov1[stage1_col]

            # grab all columns we need for stage 2 from 
            # stage 1 if present and already computed
            # should align on share number
            for stage2_col in ov_columns.OV_COLUMNS:
                if stage2_col in df_ov1.columns:
                    ov[stage2_col] = df_ov1[stage2_col]

        except KeyError as ke:
            logging.error(f'Key Error {ke}')
            return ov

        finally:
            data_store.close()

    return ov


def daterange(start_date, end_date):
    """ generate a sequence of single dates between start and end """

    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)


def get_start_end_date(df: pd.DataFrame) -> tuple:
    """ returns the start and end dates for passed in df """

    # compute the date range
    starting_year = df.index.year[0]
    starting_month = df.index.month[0]
    starting_day = df.index.day[0]

    ending_year = df.index.year[-1]
    ending_month = df.index.month[-1]
    ending_day = df.index.day[-1]

    # work way thru the df, filtering on successive dates
    start_date = date(starting_year, starting_month, starting_day)
    end_date = date(ending_year, ending_month, ending_day)

    return (start_date, end_date)


def first_trading_row_index(df, cur_date, stage: int):
    ''' create an index which finds the first row of the given day - may fail and return an empty one '''

    year, month, day, hour, minute = get_datetime_indices(df)
    cur_year, cur_month, cur_day = unpack_date(cur_date)
    # obtain the first bus row (mostly its a day's normal first row)
    # create a filtered index of first day rows (will be only 1 or possibly no row)
    if stage == 1:
        first_row_idx = df.iloc[(year == cur_year) & (month == cur_month) & (day == cur_day) & (
            hour == g.FIRST_BUS_HOUR_SLOT) & (minute == g.FIRST_BUS_MIN_SLOT)].index
    else:
        first_row_idx = df.iloc[(year == cur_year) & (
            month == cur_month) & (day == cur_day)].index

    return first_row_idx


def last_trading_row_index(df, cur_date, stage: int):
    ''' create an index which finds the last row of the given day - may fail and return an empty one '''

    year, month, day, hour, minute = get_datetime_indices(df)
    cur_year, cur_month, cur_day = unpack_date(cur_date)
    # obtain the bottom row (mostly its a day's normal end row)
    # create a filtered index of end of day rows (will be only 1 or possibly no row)
    if stage == 1:
        bot_row_idx = df.iloc[(year == cur_year) & (month == cur_month) & (day == cur_day) & (
            hour == g.LAST_BUS_HOUR_SLOT) & (minute == g.LAST_BUS_MIN_SLOT)].index
    else:
        bot_row_idx = df.iloc[(year == cur_year) & (
            month == cur_month) & (day == cur_day)].index

    return bot_row_idx


def get_row_index_from_daily_df(df, cur_date):
    ''' create an index which finds a specific row in a df which only has day rows '''

    year, month, day, hour, minute = get_datetime_indices(df)
    cur_year, cur_month, cur_day = unpack_date(cur_date)

    row_idx = df.iloc[(year == cur_year) & (
        month == cur_month) & (day == cur_day)].index

    return row_idx


def one_day_filter(df, cur_date: date):
    ''' create a filtered index which includes all rows of a entire day '''

    cur_dt64 = to_dt64(cur_date)
    return df.index.to_series().between(cur_dt64, cur_dt64, inclusive=True)

def n_days_forward_filter(df, ref_date: date, days_ahead :int):
    ''' create a filtered index which includes all rows of a day range going forward n days '''

    start_dt64 = to_dt64(ref_date)

    end_dt = ref_date + pd.tseries.offsets.BusinessDay(days_ahead)

    return df.index.to_series().between(start_dt64, end_dt, inclusive=True)


def n_days_back_filter(df, ref_date: date, days_back: int):

    end_dt64 = to_dt64(ref_date)

    start_date = ref_date - pd.tseries.offsets.BusinessDay(days_back)

    return df.index.to_series().between(start_date, end_dt64, inclusive=True)


def last_days_filter(df, days_back: int):
    ''' create a filtered index covering the last num_days_back of the dataframe '''

    last_date = df.index[-1]
    #first_date = last_date - Timedelta(days=num_days_back)
    first_date = last_date - pd.tseries.offsets.BusinessDay(days_back)
    return df.index.to_series().between(first_date, last_date, inclusive=True)


def to_dt64(indate: date):
    ''' takes a plain date and returns a numpy datetime64 '''

    indate_dt = datetime.datetime(indate.year, indate.month, indate.day)
    return np.datetime64(indate_dt)


def get_datetime_indices(df: pd.DataFrame) -> tuple:
    """ pull out separate component indices from the datetime index of the passed in df """

    year = df.index.year
    month = df.index.month
    day = df.index.day
    hour = df.index.hour
    minute = df.index.minute
    return (year, month, day, hour, minute)


def unpack_date(run_date) -> tuple:
    """ return separate year, month day from passed in date """
    return (run_date.year, run_date.month, run_date.day)

# TODO function day_totals below is expensive! ~ 30 msec


def busdays_offset(ref_ts: pd.Timestamp, offset_bus_days: int) -> pd.Timestamp:
    ''' returns offset_days back or forwards from passed in reference timestamp '''

    return ref_ts + pd.tseries.offsets.BusinessDay(n=offset_bus_days)


def day_totals(df: pd.DataFrame, share_num: str, run_date: date, contributing_col: str, totals_col: str):
    """ General purpose function which updates an end-of-day 'totals_col' in dataframe by summing values from the contributing col

        The passed in dataframe is assumed to be datetime-indexed at 5 min sampling over 'business_hours'
    """

    assert totals_col in df.columns, f'{totals_col} not found in dataframe'

    # we need these indexes for the filtering to come
    year, month, day, hour, minute = get_datetime_indices(df)
    # determine start and end dates
    start_date, end_date = get_start_end_date(df)

    run_year, run_month, run_day = unpack_date(run_date)
    # sum  for the day
    day_total = df.iloc[(year == run_year) & (month == run_month) & (
        day == run_day), df.columns.get_loc(contributing_col)].sum()  # [0]

    # create a filtered index of end of day rows (will be only 1 or possibly no row)
    eod_idx = df.iloc[(year == run_year) & (month == run_month) & (
        day == run_day) & (hour == g.LAST_BUS_HOUR_SLOT) & (minute == g.LAST_BUS_MIN_SLOT)].index
    # eod_idx is a DatetimeIndex with 0 (if empty) or 1 entry, the datetime of the YYYY-MM-DD 17:55 5-min slot
    if eod_idx.size > 0:
        # day_volume is a series (with a multi index)
        df.at[eod_idx[0], totals_col] = day_total[0]
    elif run_date == end_date:
        df.at[df.index[-1], totals_col] = day_total[0]
        msg = f'last day {run_date.strftime("%Y-%m-%d")} but the rows did not appear to go all the way to 17:55'
        logging.warn(msg)
    elif run_date.weekday() < 5:  # weekdays are 0->4
        msg = f'df for share {share_num}. Missing data for date {run_date.strftime("%Y-%m-%d")} holiday ? Please INVESTIGATE?'
        logging.warn(msg)


def first_non_zero(df: pd.DataFrame, col: str) -> tuple:
    ''' return the first non zero value and position for passed in dataframe and colum'''
    first_nz = 0
    nonzeroes = df[col].ne(0)  # series of bool values
    for i, truth in enumerate(nonzeroes):
        if truth:
            first_nz = df[col][i]
            return (i, first_nz)

    return (None, None)


def single_day_condition(df: pd.DataFrame, cur_dt: datetime) -> pd.Series:

    cur_dt_str = cur_dt.strftime('%Y-%m-%d')
    left = cur_dt_str+' 09:00:00'
    right = cur_dt_str+' 17:35:00'

    return df.index.to_series().between(left, right)


def between_dates_condition(df: pd.DataFrame, start_dt: datetime, end_dt: datetime) -> pd.Series:
    ''' return a series condition for dates between start and end '''

    start_str = start_dt.strftime('%Y-%m-%d') + ' 09:00:00'
    end_str = end_dt.strftime('%Y-%m-%d') + ' 17:35:00'

    return df.index.to_series().between(start_str, end_str)
