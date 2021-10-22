import logging
import os
import re
import sys
from datetime import date, datetime, timedelta
from logging import handlers
from os.path import exists
import glob
import click
import json
from numpy.core.numeric import NaN

import pandas as pd
import numpy as np
from bsbetl import g


def etl_path(ctx, branch: str):
    """ append branch to container path """

    return ctx.obj['container_path'] + '\\' + branch if branch else ctx.obj['container_path']


def mandatory_path_check(mandatory_path: str):
    if not exists(mandatory_path):
        print(
            f'ERROR! mandatory path {mandatory_path} not found. Make sure you specify a valid container folder')
        sys.exit()


def setup_logging(container_path, logginglevel):
    """ setup logging for global use """

    logfile_name = container_path + '\\' + g.DEFAULT_LOGNAME

    ch = logging.StreamHandler(sys.stdout)
    fh = handlers.RotatingFileHandler(
        logfile_name, maxBytes=(1048576*5), backupCount=7)
    logging.root.handlers = []
    logging.basicConfig(
        level=logginglevel,
        format="%(asctime)s [%(threadName)-12.12s] [%(levelname)-7.7s]  %(message)s",
        handlers=[
            ch,
            fh
        ]
    )


def weekdays_back(ref_date: datetime, days_back: int) -> datetime:
    """ returns the date which is days_back week-days back from passed in date """

    run_date = ref_date-timedelta(days=0)
    weekday_count = 0
    trys = 0
    for days_count in range(0, 1000):
        trys = days_count
        run_date = ref_date-timedelta(days=days_count)
        if run_date.weekday() <= 4:
            weekday_count = weekday_count + 1
        if weekday_count >= days_back:
            return run_date

    assert trys == 0, f"trying to go back too many weekdays ({days_back}. Got back to {run_date.strftime('%Y_%m%d')})"


def weeks_back(weeks_back=1) -> datetime:
    """ return YYYY_MM_DD form of weeks_back """

    back_date = datetime.now() + timedelta(days=-7*weeks_back)
    return back_date.strftime('%Y_%m_%d')

def compute_trading_days(start_date :str, end_date :str) ->int:
    ''' computes trading days between start_date and end_date '''

    sd = start_date.replace('_','-') # accept our '_' separator per YYYY_MM_DD
    ed = end_date.replace('_','-')
    return len(pd.bdate_range(sd,ed))

def suggest_default_sharelist(sharelists=g.SHARELISTS):

    if 'Default' in sharelists:
        return 'Default'
    else:
        return None  # sharelists[0]


def validate_date(ctx, param, value: str):
    """ support either busdaysbackN or YYYY_MM_DD """

    if False and value.startswith('busdaysback'):
        # DISABLED since calculating daysback from current date is not helpful
        # What is needed is to be able calculate days back from last date in the available data
        m = re.match(r'busdaysback(\d+)', value)
        if not m:
            raise click.BadParameter(
                f"{param} this form: 'busdaysbackN' where N is one or more integers")
        else:
            now = datetime.today()
            busdays_back = m.group(1)
            start_date = helpers.weekdays_back(now, int(busdays_back))
            return start_date.strftime('%Y_%m_%d')
    else:
        p = re.compile('\d{4}_\d{2}_\d{2}')
        m = p.match(value)

        if not m:
            raise click.BadParameter(
                f"{param} is expected to have the following form: 'YYYY_MM_DD'")
        else:
            return value


def validate_sharelist_name(ctx, param, value: str):
    if not value.endswith('.shl'):
        raise click.BadParameter(
            f"{param} must be a plain file name ending in '.shl'")
    else:
        return value


def validate_share_num(ctx, param, value: str):

    ok = False
    for index, bourse in enumerate(g.BOURSES_LIST):
        if value.endswith(bourse):
            ok = True
            break
        elif value == 'ignore':
            ok = True
            break

    if not ok:
        raise click.BadParameter(
            f"{param} expected to have of the following endings {g.BOURSES_LIST}")
    else:
        return value


def validate_calc_stages(ctx, param, value: list) -> list:
    ''' ensure passed in list has no entries other than that permitted by g.CALC_STAGES '''
    ok = True
    for stage in value:
        if not int(stage) in g.CALC_STAGES:
            ok = False
            break

    if not ok:
        raise click.BadParameter(
            f"{param} expected to be a subset of {g.CALC_STAGES}")
    else:
        return [int(stage) for stage in value]


def chink_on(date_str: str, advance_by_days: int):
    ''' given a date in the string form YYYY_MM_DD, return date in the same form but advanced by passed in days '''

    dt = datetime.strptime(date_str, '%Y_%m_%d')
    dt = dt + timedelta(days=advance_by_days)
    return dt.strftime('%Y_%m_%d')


def latest_TXT_date() -> str:
    ''' Return name part of last (name-sorted) file in folder. 

    '''

    glob_spec = g.CONTAINER_PATH+'\\'+g.TXT_FOLDER+'\\*.TXT'
    #print(f'inspecting {glob_spec}...')
    list_of_files = glob.glob(glob_spec)

    if len(list_of_files) > 0:
        _, tail = os.path.split(max(list_of_files))
        latest_date_str = tail[:-4]  # strip off .TXT so YYYY_MM_DD
        return chink_on(latest_date_str, 1)

    else:
        # when IN folder is completely empty
        glob_spec = g.CONTAINER_PATH+'\\' + \
            g.TXT_FOLDER+'\\'+g.CONSUMED_FOLDER+'\\*.TXT'
        #print(f'IN folder empty, now inspecting {glob_spec}...')
        list_of_files = glob.glob(glob_spec)
        if len(list_of_files) > 0:
            _, tail = os.path.split(max(list_of_files))
            latest_date_str = tail[:-4]  # strip off .TXT so YYYY_MM_DD
            return chink_on(latest_date_str, 1)
        else:
            # should rarely get here
            #print(f'\n\nIN and CONSUMED folder both empty !?!\nIs this is a first time situation?\n\n')
            return 'YYYY_MM_DD'


# def base_usable(start_date: str, top_up: bool) -> bool:
#     '''
#     Is there a level 0 base layer we can use (allowing us to skip
#     the starting from CSV and recalculating DAP phase) and does it start early enough
#     '''

#     base_good = True
#     # can we consult this runtime setting?
#     if isinstance(g.CONFIG_RUNTIME['last_calculations_start_date'], str):
#         # yes
#         base_store = g.SHARE_STORE_FQ.format(0)  # SHARES_0.h5
#         if exists(base_store):
#             # further test - compare passed in start_date with timestamp of the last used start_date
#             if top_up == False and start_date < g.CONFIG_RUNTIME['last_calculations_start_date']:
#                 # we're going to have to do a full process-3-topup and create a NEW the base level from scratch
#                 base_good = False  # new earlier start base must be created
#             elif top_up:
#                 base_good = True
#         else:
#             base_good = False
#     else:
#         base_good = False

#     return base_good

def get_last_n_lines(file_name, N):
    ''' This function accepts 2 arguments i.e. a file path as a string and number of lines to be read from last. 
        It returns a list of last N lines of the file.
        We use it to obtain the latest on-hand share price
    '''

    # Create an empty list to keep the track of last N lines
    list_of_lines = []
    # Open file for reading in binary mode
    with open(file_name, 'rb') as read_obj:
        # Move the cursor to the end of the file
        read_obj.seek(0, os.SEEK_END)
        # Create a buffer to keep the last read line
        buffer = bytearray()
        # Get the current position of pointer i.e eof
        pointer_location = read_obj.tell()
        # Loop till pointer reaches the top of the file
        while pointer_location >= 0:
            # Move the file pointer to the location pointed by pointer_location
            read_obj.seek(pointer_location)
            # Shift pointer location by -1
            pointer_location = pointer_location - 1
            # read that byte / character
            new_byte = read_obj.read(1)
            # If the read byte is new line character then it means one line is read
            if new_byte == b'\n':
                # Save the line in list of lines
                list_of_lines.append(buffer.decode()[::-1])
                # If the size of list reaches N, then return the reversed list
                if len(list_of_lines) == N:
                    return list(reversed(list_of_lines))
                # Reinitialize the byte array to save next line
                buffer = bytearray()
            else:
                # If last read character is not eol then add it in buffer
                buffer.extend(new_byte)
        # As file is read completely, if there is still data in buffer, then its first line.
        if len(buffer) > 0:
            list_of_lines.append(buffer.decode()[::-1])
    # return the reversed list
    return list(reversed(list_of_lines))


def get_latest_prices_from_last_gen_csv_by_day_run() -> dict:
    ''' deserialize LastPrices.json '''

    last_prices_fq = g.OUT_PATH + '\\LastPrices.json'
    if exists(last_prices_fq):
        with open(last_prices_fq, 'r') as f:
            return json.load(f)
    return {}


# NOTE this function is now replaced by the one above
def get_latest_prices_from_share_by_day_folders() -> pd.DataFrame:

    glob_spec = g.CSV_BY_SHARE_PATH + "\\*"
    share_folders = glob.glob(glob_spec)
    arr = []
    rows = []

    # print(share_folders)
    for folder in share_folders:
        # print(folder)
        if folder.endswith('.ETR'):
            # construct csv file names from last 10 chars of the share folder
            share_number = folder[-10:]
            csv_by_share_name_fq = folder + f"\\{share_number}.CSV"
            # print(csv_by_share_name_fq)

            # 2021-01-27 15:59:31,96.26,32,425977
            last_lines = get_last_n_lines(csv_by_share_name_fq, 2)
            # print(last_lines)
            last_line_fields = last_lines[0].split(',')
            if len(last_line_fields) == 4:
                arr.append(float(last_line_fields[1]))
                rows.append(share_number)

    # return a single column dataframe with share number as the index and latest price as the value
    df = pd.DataFrame(data=arr, index=rows, columns=['bsb_price'])

    return df

def silentremove(filename):
    try:
        os.remove(filename)
    except OSError:
        pass

def append_nodata_log(message):
    with open(g.PROCESS3_WARNLOG_NAME_FQ, "a") as logf:
        logf.write(f"{message}\n")   

def append_csv_maxsize_log(message):
    with open(g.CSVMAXSIZE_WARNLOG_NAME_FQ, "a") as logf:
        logf.write(f"{message}\n")   

def format_and_flag(updatee_df, updatee_col, indicator, resmap = g.RESMAP):
    ''' Format a dataframe column for display with trailing pass/fail indicator 
        Furthermore, in the case of updatee_df being a Results table, 
        replace values in the 'Status' row with a NaN
    '''

    updatee_df[updatee_col] = updatee_df[updatee_col].map(resmap.format)  # '{0:.5f}'
    updatee_df[updatee_col] = updatee_df[updatee_col].astype(str) + f' {indicator}'
    if 'Status' in updatee_df.columns:
        updatee_df.loc[updatee_df['Status']=='no data',updatee_col] = NaN

def update_column_format_and_flag(updatee_df, updatee_col, source_df, source_col, indicator, resmap = g.RESMAP):
    ''' Format for display an updatee cell (updatee_df, updatee_col) 
        by copying values from a source df and column (source_df, source_col) and
        append a passing or failing flag.
        If the updatee is a Results frame then those shares having Status of 'no data' 
        will have the corresponding row set to NaN.  NOTE formats and flags an entire column
    '''
    #early exit if updatee_df is empty (we dont want to add rows)
    if len(updatee_df) == 0:
        return

    updatee_df[updatee_col] = source_df[source_col]
    format_and_flag(updatee_df,updatee_col,indicator,resmap)

def copy_column_format_and_flag(updatee_df, new_col, source_col, indicator, resmap = g.RESMAP):
    ''' format for display a new column (updatee_df, new_col) 
        based on *same* df and source variable (source_col) and
        flag as either passing or failing
        NOTE formats and flags an entire column
    '''

    #early exit if updatee_df is empty (we dont want to add rows)
    if len(updatee_df) == 0:
        return
    updatee_df[new_col] = updatee_df[source_col]
    updatee_df[new_col] = updatee_df[new_col].map(resmap.format)  # '{0:.5f}'
    updatee_df[new_col] = updatee_df[new_col].astype(str) + f' {indicator}'

    # in the case of updatee_df being a Results table, replace values in the 'Status' row
    if 'Status' in updatee_df.columns:
        updatee_df.loc[updatee_df['Status']=='no data',new_col] = NaN

def initialize_condition_column(cond_col, results, ov) ->int:
    '''
    establish an initial con_key column in the results (with NaN in the column)
    and return the number of 'no-data' shares
    '''
    # add the column and establish an 'initial' value
    results[cond_col] = NaN
    # flag those shares in the ov with 'no data' by filtering 
    # the ov and adding a column to the filtered ov with value 'no data'
    ov_nodata = ov[ov['Status']== 'no data']
    #ov_nodata[cond_col] = 'no data'
    # update the results column for the condition column
    #results.update(ov_nodata[cond_col])

    return len(ov_nodata)
