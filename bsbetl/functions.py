from bsbetl.ov_calcs import frt_columns
import glob
import inspect
import json
import logging
import os
import re
import random
from contextlib import ExitStack
from datetime import datetime
from getpass import getpass
from os import listdir, mkdir, remove
from os.path import exists, isfile, join

import click
import numpy as np
from numpy.core.numeric import NaN
import pandas as pd
from pandas.core.frame import DataFrame
import requests
from numpy.lib.function_base import diff
from requests_ntlm import HttpNtlmAuth

from bsbetl import calc_helpers, func_helpers, g, helpers, results
from bsbetl.calc_helpers import sharenum_in_spinoff_list
from bsbetl.func_helpers import (build_results_starter_df, check_monotonicity, config_shares_list_2_names_or_numbers, load_overview_df, load_results_df, prepare_csv_outfile_paths,
                                 prepare_src_csv_files_list,
                                 save_runtime_config, update_share_hint_files)

from bsbetl.results._1St_results import (_1St_Condition_a, 
                                        _1St_Condition_b, 
                                        _1St_Condition_c, 
                                        _1St_Condition_d 
)
from bsbetl.results._2StPr_results import (_2StPr_Condition_a1,
                                            _2StPr_Condition_a2,
                                            _2StPr_Condition_a3,
                                            _2StPr_Condition_b,
                                            _2StPr_Condition_c,
                                            _2StPr_Condition_d,
                                            _2StPr_Condition_e,
                                            _2StPr_Condition_f,
                                            _2StPr_Condition_g,
                                            _2StPr_Condition_h,
                                            _2StPr_Condition_i,
                                            _2StPr_Condition_j
)
from bsbetl.results._2StVols_results import (_2StVols_Condition_a1,
                                             _2StVols_Condition_a2,
                                             _2StVols_Condition_b,
                                             _2StVols_Condition_c,
                                             _2StVols_Condition_d,
                                             _2StVols_Condition_e,
                                             _2StVols_Condition_f
)
from bsbetl.results._3jP_conditions import _3jP_conditions
from bsbetl.results._3jP_results import compute_djp

# once this limit is reached, no further 'empties' reporting to the log files:
EMPTY_TRADES_LOGGING_LIMIT = 5  # 0 turns off the warnings in the log file
SKIPPED_TRADES_LOGGING_LIMIT = 5  # 0 turns off the warnings in the log file

def hlp_startup_checks(container_path, sub_folders: list) -> bool:
    """ checks for existence of container_path plus each of its subfolder in the list """

    failure = False
    for index, folder_present in enumerate(hlp_folders_presence(container_path, sub_folders)):
        if not (folder_present):
            if index == 0:
                logging.error(
                    f'Required Container folder {container_path} not found!')  # earlier test should prevent this
            else:
                logging.error(
                    f"ALL Sub folders of {container_path} must be present, subfolder '{sub_folders[index-1]}' is missing")
            failure = True
    return failure


def hlp_folders_presence(container_folder: str, sub_folders: list) -> list:
    """ helper """

    ret_list = [exists(container_folder)]
    for folder in sub_folders:
        ret_list.append(exists(container_folder + '\\' + folder))
    # contains container_folder existence test result plus the subfolder tests results
    return ret_list


def hlp_update_master_share_dictionary(cur_run_dict: dict) -> int:
    """ Spin off an updated master share dictionary dictonary text file listing name, number, first_date in name order

    No longer compatible with the Winforms C# version of Shw !!!
    """

    func_name = inspect.stack()[0][3]
    logging.info(f'Command {func_name}...')

    # this is how current_run_share_dict looks:
    # cur_run_dict[share_num] = (share_name, trade_date)

    # this is how the master share dict looks
    # g.MASTER_SHARE_DICT[share_num] = (share_name, first_date, last_date)

    # first update the master in memory from the current_run dict, then save it to disk
    for share_num in cur_run_dict:
        # note. the share_num may be new
        cur_trade_date = cur_run_dict[share_num][1]
        share_name = cur_run_dict[share_num][0]
        if share_num in g.MASTER_SHARE_DICT:
            # share is not new, but we need to update its last_date
            master_last_date_update = cur_trade_date
            # plus fix (if necessary) the master's first_date
            if g.MASTER_SHARE_DICT[share_num][1] == 'DD.MM.YYYY':
                master_first_date_update = cur_trade_date
            else:
                # preserve it as is
                master_first_date_update = g.MASTER_SHARE_DICT[share_num][1]
            # do the update
            g.MASTER_SHARE_DICT[share_num] = (
                share_name, master_first_date_update, master_last_date_update)
        else:
            # new, add to dict
            g.MASTER_SHARE_DICT[share_num] = (
                share_name, cur_trade_date, cur_trade_date)

    # now save master to disk
    save_master_share_dictionary(g.MASTER_SHARE_DICT, g.MASTER_SHARE_DICT_FQ)
    convert_and_save_master_share_dictionary(g.MASTER_SHARE_DICT, g.MASTER_SHARE_DICT_FQ)

    return len(g.MASTER_SHARE_DICT.keys())


def save_master_share_dictionary(master_dict: dict,  master_share_dict_fq: str):

    # this is how the master_dict looks:
    # master_dict[share_num] = (share_name, first_date, last_date)

    with open(master_share_dict_fq, 'w') as outf:
        header = 'share_name'.ljust(31)+',number,first_date,last_date\n'
        outf.write(header)
        # want sort order to be share name
        for number, values in sorted(master_dict.items(), key=lambda item: item[1]):
            name = values[0].replace(',', '*')
            first_date = values[1]
            last_date = values[2]
            # discard shares whose names start with eg I.XTRA
            good_to_include = True
            for blacklisted in g.MASTER_SHARE_DICT_BLACKLIST:
                if name.startswith(blacklisted):
                    good_to_include = False
                    break
            if good_to_include:
                outf.write(
                    f'{name.ljust(31)},{number},{first_date},{last_date}\n')

def convert_and_save_master_share_dictionary(master_dict: dict,  master_share_dict_fq: str):

    # this is how the master_dict looks:
    # master_dict[share_num] = (share_name, first_date, last_date)
    # we want the first_date and last_date to be converted 
    # from DD.MM.YYYY to YYYY.MM.DD to enable proper sorting

    with open(master_share_dict_fq+'.converted', 'w') as outf:
        header = 'share_name'.ljust(31)+',number,first_date,last_date\n'
        outf.write(header)
        # want sort order to be share name
        for number, values in sorted(master_dict.items(), key=lambda item: item[1]):
            name = values[0].replace(',', '*')
            fdu = values[1] # first date unconverted DD.MM.YYYY
            ldu = values[2] # last date unconverted

            first_date = fdu[6:]+'.'+fdu[3:5]+'.'+fdu[0:2]
            last_date = ldu[6:]+'.'+ldu[3:5]+'.'+ldu[0:2]

            # discard shares whose names start with eg I.XTRA
            good_to_include = True
            for blacklisted in g.MASTER_SHARE_DICT_BLACKLIST:
                if name.startswith(blacklisted):
                    good_to_include = False
                    break
            if good_to_include:
                outf.write(
                    f'{name.ljust(31)},{number},{first_date},{last_date}\n')


def get_date_for_busdays_back(days_back: int) -> str:

    now = datetime.today()
    start_date = helpers.weekdays_back(now, days_back)
    return start_date.strftime('%Y_%m_%d')


def hlp_parse_trading_info(share_trades: int, line: str):
    """ extract and return trading info """

    share_trades = share_trades + 1
    trade_fields = re.split(';', line.strip())
    # grab specific fields
    trade_time = trade_fields[0]
    trade_price = trade_fields[1]
    trade_vol = trade_fields[2]
    trade_cum_vol = trade_fields[3]
    return trade_time, trade_price, trade_vol, trade_cum_vol, share_trades


def hlp_parse_new_share_trading_run(share_runs: int, line: str, current_run_share_dict: dict, trade_date: str, share_name: str, share_num: str):
    """ extract and return trading info and update share_num -> (share_name,trade_date) tuple for the passed in current_run_share_dict dictionary  """

    share_runs = share_runs + 1
    wertpapier_fields = re.split(';', line.strip())
    # grab the date, share name and number details for use with the (expected) trades on following lines
    trade_date = wertpapier_fields[1]  # eg '03.01.2018'
    share_name = wertpapier_fields[2]
    # share_num includes the .bourse part eg 'A1H8BV.ETR'
    share_num = wertpapier_fields[3]
    # section starts with share name
    # outf.write(f'SHARE: {share_name}\n')

    # validate to ensure fields are well formed
    trade_date_good = re.fullmatch("^\d{2}.\d{2}.\d{4}$", trade_date)
    share_num_good = re.fullmatch("^\w{6}\.(ETR|FFM)$", share_num)

    if trade_date_good and share_num_good:
        current_run_share_dict[share_num] = (share_name, trade_date)
        return share_name, share_num, trade_date, share_runs
    else:
        logging.warn(
            f"irregular 'WERTPAPIER' starter. Parsed trade_date as '{trade_date}' ({trade_date_good}) & share_num as '{share_num}' ({share_num_good}) from line: {line}")
        return share_name, share_num, trade_date, 0


def fetch_txt_catalog(catalog_url: str, share_service_user: str, local_txt_catalog_name: str) -> tuple:
    """ * download the TXT catalog from the remote service """

    # r = requests.get(url, auth=HTTPBasicAuth(USER, getpass()))
    # r = requests.get(url, auth=HTTPDigestAuth(USER, getpass()))

    # NTLM was the only auth I could get to work!
    # r = requests.get(url, auth=HttpNtlmAuth(USER, getpass()))

    # the session way
    session = requests.Session()
    pwd = getpass()
    session.auth = HttpNtlmAuth(share_service_user, pwd)
    r = session.get(catalog_url)

    result_msg = "fetch-catalog result unknown..."
    if r.status_code == 200:
        with open(local_txt_catalog_name, 'wb') as out:
            for bits in r.iter_content():
                out.write(bits)
            result_msg = f"{local_txt_catalog_name} downloaded"
            logging.info(result_msg)
    else:
        logging.error(r.headers)
        logging.error(r.request.headers)
        result_msg = 'fetch-catalog errors ocurred. See log file'
        pwd = ''  # return empty if fail

    return (pwd,result_msg)


def hlp_setup_session(url: str, share_service_user: str, pwd=''):
    """ set up and return a session with remote service """

    print('\a')  # beep since a password will be required
    session = requests.Session()
    if pwd == '':
        pwd = getpass()
    session.auth = HttpNtlmAuth(share_service_user, pwd)

    return session


def hlp_url_response(url_tuple: str, session):
    """ download a file from a remote url """

    # passed in url_struct is a 2 tuple eg:
    # ('\\BsbEtl\\TXT_Bank\\2020_08_27.TXT', 'http://www.bsb-software.de/rese/2020_08_27.TXT')
    local_path, url = url_tuple

    r = session.get(url)

    if r.ok:
        with open(local_path, 'wb') as f:
            for ch in r:
                f.write(ch)
            logging.debug(f'downloaded {local_path}')           

    return r


def fetch_txt_files(ctx, share_service_user: str, pwd: str):
    """ * Fetch TXT files from the remote service

        Assuming --date is supplied like so: YYYY_MM_DD,
        A 'download-list' of files (compiled from Inhalt.txt) >= --date will be retrieved

    """
    func_name = inspect.stack()[0][3]
    logging.info(f'Executing {func_name} ...')

    # unpack explicitly
    first_date = ctx.obj['first_date']

    share_service_url = g.SHARE_SERVICE_URL
    # share_service_user = g.SHARE_SERVICE_USER
    local_catalog_name_fq = f'{g.CONTAINER_PATH}\{g.SHARE_SERVICE_CATALOG_NAME}'
    txt_by_day_folder_fq = f'{g.CONTAINER_PATH}\{g.TXT_FOLDER}'

    # Build a download list from the (assumed recently downloaded) Inhalt TXT catalog file
    # (this helps to ensure we know the data *is* on the remote server)
    # We grab only the YYYY_MM_DD leading piece of each line
    catalog_list = []
    logging.debug(f'local_catalog_name_fq={local_catalog_name_fq}')
    with open(local_catalog_name_fq, "r") as catf:
        catalog_list = [line[0:10] for line in catf.readlines()]

    # find the first entry in the catalog list which matches first_date YYYY_MM_DD
    # start_index = catalog_list.index(first_date)
    # better: make a new list whose entries are same or later than first_date
    effective_catalog_list = [
        entry for entry in catalog_list if entry >= first_date]

    # print(effective_catalog_list)

    # build 2d array of local destination file paths and remote share service file urls eg
    # [('\\BsbEtl\\TXT_Bank\\2020_08_27.TXT', 'http://www.bsb-software.de/rese/2020_08_27.TXT'),
    #  ('\\BsbEtl\\TXT_Bank\\2020_08_28.TXT', 'http://www.bsb-software.de/rese/2020_08_28.TXT'),
    #  ...
    #  (,)]

    url_tuples = []
    for date_part in effective_catalog_list:
        txt_in_fq = f'{txt_by_day_folder_fq}\{date_part}.TXT'
        csv_byday_fq = f'{g.CSV_BY_DAY_PATH}\{date_part}.TXT.CSV'
        # only try downloading if file not already on board locally
        if ((not exists(txt_in_fq)) and (not exists(csv_byday_fq))):
            url_tuples.append(
                (txt_in_fq, share_service_url + f'{date_part}.TXT'))
        else:
            logging.info(
                f'Skipping {date_part}.TXT since its already present...')

    # setup a session
    print(f'share_service_url={share_service_url}, share_service_user={share_service_user}, pwd={pwd}')

    s = hlp_setup_session(share_service_url, share_service_user, pwd)

    # one file at a time
    click.secho('Please be patient for files to begin arriving...',
                fg='yellow', bold=True)
    num_fetched = 0
    with click.progressbar(url_tuples) as bar:
        for url_tuple in bar:
            r = hlp_url_response(url_tuple, s)
            if not r.ok:
                if r.status_code == 401:
                    logging.error('Password incorrect for user')
                    break
                else:
                    local_path, url = url_tuple
                    logging.error(
                        f'failed downloading {url} (status_code {r.status_code})')
            else:
                num_fetched = num_fetched+1
                g.CONFIG_RUNTIME['fetch-txt-last-downloaded'] = url_tuple[1]
                save_runtime_config()


    # multiple threads way --- not yet working
    # ThreadPool(9).imap_unordered(hlp_url_response, urls)
    logging.info(f'{num_fetched} TXT files fetched.')
    logging.info(f'End {func_name} execution.')

    return


def hlp_gen_csv_from_txt(ctx, txtf: str, current_run_share_dict: dict,
                         keep_txt: bool, txtfile_count: int, last_price_dict: dict):
    """ creates a 'day' CSV file corresponding to passed in 'day' TXT file """

    #txt_path = helpers.etl_path(ctx, g.TXT_FOLDER)
    #csv_byday_path = helpers.etl_path(ctx, g.CSV_BY_DAY_FOLDER)

    infile_name = f'{g.TXT_PATH}\{txtf}'
    consumed_infile_name = f'{g.TXT_PATH}\{g.CONSUMED_FOLDER}\{txtf}'
    outfile_name = f'{g.CSV_BY_DAY_PATH}\{txtf}.CSV'

    infile_was_deleted = False
    consumed = False
    empty_trades = 0
    skipped_trades = 0
    in_line_num = 1
    out_line_num = 0
    after_hours_trades = 0
    with open(infile_name, "r") as inf:
        with open(outfile_name, 'w') as outf:
            # Read first line
            in_line = inf.readline()
            share_runs = 0
            share_trades = 0
            share_name = ""  # initially unknown
            share_num = ""
            trade_date = ""
            while in_line:
                # WERTPAPIER;05.01.2018;NORMA GROUP SE NA O.N.;A1H8BV.ETR
                if in_line.startswith("WERTPAPIER;"):
                    # we have a (new) share run
                    share_name, share_num, trade_date, share_runs = hlp_parse_new_share_trading_run(
                        share_runs, in_line, current_run_share_dict, trade_date, share_name, share_num)
                    # was it ok?
                    if share_runs == 0:  # implies malformed line
                        # no, skip the following lines until a new WERTPAPIER line appears
                        share_name = ''
                        share_num = ''
                        trade_date = ''
                        skipped_trades = skipped_trades + 1
                    else:
                        skipped_trades = 0  # all good, so reset
                elif share_name != "":
                    # assume we have trading info: 10:30:36;20,4;80;975
                    try:
                        trade_time, trade_price, trade_vol, trade_cum_vol, share_trades = hlp_parse_trading_info(
                            share_trades, in_line)
                        # write out uniformly delimited csv
                        if out_line_num == 0:
                            # header
                            # 120470.ETR,03.01.2018,09:04:28,0.726,900,900
                            outf.write(
                                f'share_number,date,time,price,volume,volume_cumulative\n')
                        else:
                            price = trade_price.replace(",", ".")
                            # lump all trades from 17:36:00 and later into band 17:35:59
                            if trade_time > '17:35:59':
                                trade_time = '17:35:59'
                                after_hours_trades = after_hours_trades+1
                            outf.write(
                                f'{share_num},{trade_date},{trade_time},{price},{trade_vol},{trade_cum_vol}\n')
                            last_price_dict[share_num] = price
                        out_line_num = out_line_num + 1
                    except IndexError:
                        logging.error(f'IndexError parsing line {in_line_num}: {in_line} ')

                elif share_name == "":
                    if skipped_trades == 0:
                        empty_trades = empty_trades + 1
                        if empty_trades < EMPTY_TRADES_LOGGING_LIMIT:
                            logging.warn(
                                f'File {txtfile_count} ({txtf}), line {in_line_num}: share with no name! (number {share_num})  ignored/skipped')
                        elif empty_trades == EMPTY_TRADES_LOGGING_LIMIT:
                            logging.warn(
                                f'No further reporting of these EMPTY TRADES for this file...')
                    else:
                        if skipped_trades < SKIPPED_TRADES_LOGGING_LIMIT:
                            logging.warn(
                                f'File {txtfile_count} ({txtf}), line {in_line_num}: skipped due to malformed WERTPAPIER starter')
                        elif skipped_trades == SKIPPED_TRADES_LOGGING_LIMIT:
                            logging.warn(
                                f'No further reporting of these skipped TRADES for this run...')

                else:
                    raise Exception(
                        f"ERROR - File {txtfile_count} ({txtf}),line {in_line_num}: Malformed file must start with a 'WERTPAPIER' line!")
                # read next input line
                in_line = inf.readline()
                in_line_num = in_line_num+1

            # delete the infile (default)
            if not keep_txt:
                remove(infile_name)
                infile_was_deleted = True

            # infile done
            consumed = True
            logging.info(
                f'process-1: file {txtfile_count}, {txtf} {in_line_num} lines in, {out_line_num+1} out, {share_runs} runs, {share_trades} packets - {empty_trades} empty {after_hours_trades} after-hours trades')

    if consumed and (not infile_was_deleted):
        # move it into CONSUMED folder
        os.rename(infile_name, consumed_infile_name)
        g.CONFIG_RUNTIME['process-1-last-consumed'] = consumed_infile_name
        save_runtime_config()

    return


def gen_csv_byday(ctx, origination :str):
    """ takes all .TXT files in in_path, and produces, one for one, CSV files from from them

    The .TXT files are assumed to be available in in_path (sourced from bsb.de)
    They are optionally deleted once processed - a CSV version is produced in the out_path
    """

    func_name = inspect.stack()[0][3]
    logging.info(f'Executing {func_name} ...')

    # unpack explicitly the needed parameters
    keep_txt = ctx.obj['keep_txt']

    current_run_share_dict = {}  # this dictionary gets built during the process
    last_price_dict = {}

    # get list of ALL input TXT files
    txt_files = [f for f in listdir(g.TXT_PATH) if f.endswith('TXT') and isfile(join(g.TXT_PATH, f))]

    logging.info(f'{len(txt_files)} TXT files...')

    pass_number = 1
    txtfile_count = 0
    skipfile_count = 0

    # On first pass, check whether we have ANY work to do
    txtfile_count = 0
    skipfile_count = 0
    for txtf in txt_files:
        txtfile_count = txtfile_count + 1
        outfile_name = f'{g.CSV_BY_DAY_PATH}\{txtf}.CSV'
        if exists(outfile_name):
            skipfile_count = skipfile_count+1
            consumed_name = f'{g.TXT_PATH}\{g.CONSUMED_FOLDER}\{txtf}'
            # try to move the file into the COMSUMED folder
            if exists(consumed_name):
                logging.warn(
                    f'{txtf} has already been consumed, so removing it...')
                # if it exists there already, safely delete the TXT file
                # since we appear to have already processed it
                os.remove(f'{g.TXT_PATH}\{txtf}')
            else:
                # irregular situation - we have a TXT.CSV version of the TXT file
                # in the csv by day path, so must have been consumed,
                # yet its not in the CONSUMED folder!?
                logging.warn(
                    f'{txtf} has already been converted to CSV, but its not in the CONSUMED folder...')
                # move it there
                os.rename(f'{g.TXT_PATH}\{txtf}', consumed_name)
                logging.warn(f'{txtf} moved to the CONSUMED folder...')

    # second pass
    if skipfile_count == txtfile_count:
        logging.warn(
            f'ALL {skipfile_count} files already processed, NOTHING to do')
    else:
        # proceed to generate CSV files one by one for those files not yet having a CSV
        txtfile_count = 0
        skipfile_count = 0
        for txtf in txt_files:
            txtfile_count = txtfile_count + 1
            outfile_name = f'{g.CSV_BY_DAY_PATH}\{txtf}.CSV'
            # skip if output file already there
            if exists(outfile_name):
                skipfile_count = skipfile_count+1
                logging.warn(f'File {txtfile_count}, {txtf}.CSV already present, skipped')
            else:
                # generate csv from txt
                hlp_gen_csv_from_txt(ctx, txtf, current_run_share_dict, keep_txt, txtfile_count, last_price_dict)

    # update the master Share Dictionary
    if (len(current_run_share_dict) > 0):
        num_shares = hlp_update_master_share_dictionary(current_run_share_dict)
        logging.info(f'New Share Dictionary written. ({num_shares} shares)')
    else:
        logging.warn(f'New Share Dictionary was NOT written')

    # save last_price_dict to disk
    last_prices_fq = g.OUT_PATH + f'\\LastPrices.json'
    with open(last_prices_fq, 'w') as f:
        f.write(json.dumps(last_price_dict, indent=4))

    logging.info(
        f'End {func_name} execution. {txtfile_count} files, {skipfile_count} skipped')

    return current_run_share_dict


def hlp_repack_trade(src_csvline: str) -> str:
    """ repack src_csvline for more pandas convenience

        Drop share number, rearrange and combine date and time
        '511170.ETR,03.01.2018,09:31:16,155.4,3,362'  -->  '2018-01-03 09:31:16,155.4,3,362'
    """

    fields = src_csvline.split(',')
    date = fields[1]
    time = fields[2]
    price = fields[3]
    vol = fields[4]
    cum_vol = fields[5]

    # repack a new date_time
    datefields = date.split('.')
    dd = datefields[0]
    mm = datefields[1]
    yyyy = datefields[2]

    # drop share number also
    return f'{yyyy}-{mm}-{dd} {time},{price},{vol},{cum_vol}'


def hlp_delete_existing_output(excel_filename_fq, plot_filename_fq, parse_error_filename_fq, memory_error_filename_fq):
    """ remove files which are about to regenerated as well as any prior error files """

    if exists(excel_filename_fq):
        os.remove(excel_filename_fq)
    if exists(plot_filename_fq):
        os.remove(plot_filename_fq)
    if exists(parse_error_filename_fq):
        os.remove(parse_error_filename_fq)
    if exists(memory_error_filename_fq):
        os.remove(memory_error_filename_fq)


# def hlp_price_vol_output(csv_file: str, share_tuple: tuple):
#     """ produce a basic price_vol excel and plot file """

#     basic_suffix = 'price_vol'

#     (share_number, share_name) = share_tuple

#     # remove any existing basic output
#     # trades_filename_fq = f'{csv_file}_trades_diag.xlsx'
#     excel_filename_fq = f'{csv_file}_{basic_suffix}.xlsx'
#     plot_filename_fq = f'{csv_file}_{basic_suffix}{g.IMG_FORMAT}'
#     parse_error_filename_fq = f'{csv_file}_parse_error!'
#     memory_error_filename_fq = f'{csv_file}_memory_error!'

#     hlp_delete_existing_output(excel_filename_fq, plot_filename_fq,
#                                parse_error_filename_fq, memory_error_filename_fq)

#     # load the .TXT.CSV file
#     try:
#         df_trades = pd.read_csv(csv_file, index_col='date_time',
#                                 parse_dates=True, infer_datetime_format=True)

#         trade_rows, trade_cols = df_trades.shape
#         assert(trade_rows > 0)

#         del(df_trades['vol_cum'])  # not wanted

#         # convert to business hours by doing a resample
#         df_bh = df_trades.resample('5Min').agg(
#             {'price': ['mean'], 'volume': ['sum']}).pad()
#         df_bh.fillna(0)
#         # bus hours means Mon to Fri 9 thru 6 pm
#         df_bh = df_bh[(df_bh.index.dayofweek <= 4) & (
#             df_bh.index.hour >= 9) & (df_bh.index.hour <= 17)]

#         # spin dataframe off as excel
#         df_bh.to_excel(excel_filename_fq)

#         # do plots
#         plots.price_and_volume_plots(
#             df_bh, share_name, share_number, plot_filename_fq)

#     except pd.errors.ParserError as pe:
#         logging.error(f'Parse Error {pe}')
#         # get rid of these since they wont now be right
#         hlp_delete_existing_output(excel_filename_fq, plot_filename_fq,
#                                    parse_error_filename_fq, memory_error_filename_fq)
#         # but leave an error flag file
#         open(parse_error_filename_fq, 'a').close()

#     except MemoryError as me:
#         logging.error(f'Memory Error {me}')
#         # get rid of these since they wont now be right
#         hlp_delete_existing_output(excel_filename_fq, plot_filename_fq,
#                                    parse_error_filename_fq, memory_error_filename_fq)
#         # but leave an error flag file
#         open(memory_error_filename_fq, 'a').close()


def trawl_csvfiles_for_share(single_share_num: str, src_csv_files_list: list, csv_src_path: str, out_shf, start_date: str, last_trade_tstamp: str) -> str:
    """ Trawl thru *.CSV files looking for trades of the single share and append to out_shf

        Gathered trades must be later than start_date AND last_trade_tstamp (former is a date, latter is a date and time)
    """

    # user provided date must have underscores replaced
    start_date_tweaked = start_date.replace('_', '-')
    out_sharelines_written = 0
    last_written_trade = ''

    src_csvfile_count = 0
    for src_csv_file in src_csv_files_list:
        src_csvfile_count = src_csvfile_count + 1
        # determine fq csvfile name
        src_csvfile_fq_name = f'{csv_src_path}\{src_csv_file}'
        src_csvlines_read = 0
        src_csvline = ''
        with open(src_csvfile_fq_name, "r") as src_csvf:
            # assumed a header (share_number,date,time,price,volume,volume_cumulative)
            src_csvline = src_csvf.readline()
            src_csvlines_read = src_csvlines_read + 1
            while True:
                if src_csvline.startswith(single_share_num):
                    # repack per 'YYYY-MM-DD HH:MM:SS,price,volume,vol_cum'
                    repacked_trade = hlp_repack_trade(src_csvline)
                    # only write out if we're beyond start_date
                    if repacked_trade[0:10] >= start_date_tweaked:
                        # furthermore, we must also be later than last_trade_tstamp
                        if (last_trade_tstamp == '') or (repacked_trade[0:19] >= last_trade_tstamp):
                            out_shf.write(repacked_trade)
                            out_sharelines_written = out_sharelines_written + 1
                            last_written_trade = repacked_trade
                src_csvline = src_csvf.readline()  # read next csv line
                if not src_csvline:
                    break
                src_csvlines_read = src_csvlines_read + 1

        logging.info(
            f'Input file {src_csvfile_count} ({src_csv_file}) - {src_csvlines_read} lines, {out_sharelines_written} new trades appended. (share {single_share_num})')
    return (last_written_trade, out_sharelines_written)


def trawl_csvfile_for_alltrades(src_csvfile_fq_name: str, start_date: str, outfile_handles: list, share2handleindex_dict: dict, share2last_tstamp: dict):
    """ Read thru a particular source csv file and distribute ALL trades therein to separate share specific files in their own share specific folders 
        NOTE the outfile path may look eg 'C:\BsbEtl\OUT\By_Share\120470.ETR\120470.ETR.CSV'
        BUT *ALL* trades associated with the share '120470' (from bourses ETR as well as FFM) 
        will get gathered into this single file ie despite the 'ETR' segment being in the path
    """

    # user provided date must have underscores replaced
    start_date_tweaked = start_date.replace('_', '-')
    out_sharelines_written = 0
    last_written_trade = ''

    src_csvlines_read = 0
    src_csvline = ''
    # example entry outfile_handles[i].name ='C:\BsbEtl\OUT\By_Share\120470.ETR\120470.ETR.CSV'
    with open(src_csvfile_fq_name, "r") as src_csvf:
        # assumed a header (share_number,date,time,price,volume,volume_cumulative)
        # share_number,date,time,price,volume,volume_cumulative
        # 120470.ETR,03.01.2018,13:24:39,0.7238,1500,2400
        # 120470.ETR,03.01.2018,15:18:14,0.725,999,3399
        # 500800.FFM,08.01.2019,09:15:02,13.38,0,0  NOTE trades from other bourse as well
        # 500800.FFM,08.01.2019,17:37:36,13.64,220,220


        src_csvline = src_csvf.readline()
        src_csvlines_read = src_csvlines_read + 1
        while True:
            src_share_num = src_csvline[0:10]  # 120470.ETR
            src_share_key = src_share_num[0:-4]
            src_share_num_csv = src_share_num + ".CSV"  # 20470.ETR.CSV
            if src_share_key in share2handleindex_dict:
                # repack per 'YYYY-MM-DD HH:MM:SS,price,volume,vol_cum'
                repacked_trade = hlp_repack_trade(src_csvline)
                # only write out if we're beyond start_date
                if repacked_trade[0:10] >= start_date_tweaked:
                    # furthermore, we must also be later than last_trade_tstamp in the destination file
                    # note that last_trade_tstamp is to the second: eg 2020-11-23 20:08:46
                    last_trade_tstamp = share2last_tstamp[src_share_key]
                    if (last_trade_tstamp == '') or (repacked_trade[0:19] > last_trade_tstamp):
                        # retrieve the particular csv outfile sharehandle
                        out_shf = outfile_handles[share2handleindex_dict[src_share_key]]

                        out_shf.write(repacked_trade)

                        out_sharelines_written = out_sharelines_written + 1
                        last_written_trade = repacked_trade
            src_csvline = src_csvf.readline()  # read next csv line
            if not src_csvline:
                break
            src_csvlines_read = src_csvlines_read + 1

        logging.info(
            f'process-2: Trades By_Day {src_csvfile_fq_name} - ({src_csvlines_read} lines), distributed to trades By_Share folders. {out_sharelines_written} new trades')

    return


def gen_csv_oneshare(ctx, share_num: str, share_name: str, start_date: str = ''):
    """ extract the csv for a particular share from first_date"""

    func_name = inspect.stack()[0][3]
    print('\n')  # helps progressbar to stand out
    logging.info(
        f'Executing {func_name}...(some) parameters: share_num ={share_num}, start_date={start_date}')

    #csv_by_day_path = helpers.etl_path(ctx, g.CSV_BY_DAY_FOLDER)
    #csv_by_share_path = helpers.etl_path(ctx, g.CSV_BY_SHARE_FOLDER)

    # ensure folder exists for this share (share_path assumed to exist)
    single_share_directory = f'{g.CSV_BY_SHARE_PATH}\{share_num}'
    if not exists(single_share_directory):
        mkdir(single_share_directory)
        logging.warn(f'folder {single_share_directory} had to be created')

    # the name of the CSV file we'll be creating or appending to
    out_sharefile_fq_name = f'{g.CSV_BY_SHARE_PATH}\{share_num}\{share_num}.CSV'
    last_trade_time_stamp = func_helpers.get_last_trades_timestamp(out_sharefile_fq_name)  # this should return eg 2020-09-21 17:36:25 (or '')

    # peek into it (if existing) and retrieve the datetime stamp of the first trade
    first_trade_time_stamp = func_helpers.get_first_trade_timestamp(
        out_sharefile_fq_name)
    # this stamp needs to be cleaned up since it will form part of the info filename
    # replace non word chars with underscores
    first_trade_time_stamp = re.sub(r"[\W]", "_", first_trade_time_stamp)

    # select the appropriate slug
    hint_slug = start_date if first_trade_time_stamp == '' else first_trade_time_stamp

    # put down a hint file whose name informs user of the start date of trades
    scrubbed_share_name = re.sub(r"[\W]", "_", share_name)

    hint_filename_fq = single_share_directory + \
        f"\\_{hint_slug}_{scrubbed_share_name}.info"

    # NOTE share_name is '' when this routine is run manually once off
    if share_name != '':
        # remove former .info files
        for fl in glob.glob(f'{single_share_directory}\\*.info'):
            os.remove(fl)
        open(hint_filename_fq, 'a').close()

    init_src_csv_files_list = [f for f in listdir(g.CSV_BY_DAY_PATH) if f.endswith(
        'TXT.CSV') and isfile(join(g.CSV_BY_DAY_PATH, f))]

    # discard src_csv files whose date predates start_date
    src_csv_files_list = [
        f for f in init_src_csv_files_list if f >= f'{start_date}.TXT.CSV']

    logging.info(f'{len(src_csv_files_list)} CSV files...')

    # if sharefile will be new, write a header to it
    must_write_header = not exists(out_sharefile_fq_name)

    # open the sharefile for appending
    out_shf = open(out_sharefile_fq_name, 'a')
    if must_write_header:
        out_shf.write(g.SHARE_CSV_HEADER)

    # trawl all the .CSV files for trades for this single share and write to out_shf
    (last_written_trade, num_trades_written) = trawl_csvfiles_for_share(
        share_num, src_csv_files_list, g.CSV_BY_DAY_PATH, out_shf, start_date, last_trade_time_stamp)

    out_shf.close()

    # update hint file (only when run under gen_csv_byshare, not when once off)
    if share_name != '':
        with open(hint_filename_fq, 'w') as hintf:
            hintf.write(
                f'{num_trades_written} trades written. Last trade: {last_written_trade}')

    # spin off basic output dataframe xslx and plot image files
    if (num_trades_written > 0):
        # hlp_price_vol_output(out_sharefile_fq_name, (share_num, share_name))
        # logging.info(f'basic output produced')
        pass
    else:
        logging.warn(
            f'{num_trades_written} trades were found for share {share_num}. PLEASE INVESTIGATE.')

    logging.info(f'End {func_name} execution.')


# TODO: replace by using a one-pass method
def gen_csv_byshare(ctx):
    """ creates share specific csv files for every share in the sharelist file """

    func_name = inspect.stack()[0][3]
    logging.info(f'Executing {func_name} ...')

    # grab params from passed context
    start_date = ctx.obj['start_date']
    sharelist_name = ctx.obj['sharelist_name']
    only_share = ctx.obj['only_share']

    sharelist_name_fq = helpers.etl_path(
        ctx, f'{g.SHARELISTS_FOLDER}\{sharelist_name}')

    # obtain a list of share_name, share_number tuples from the sharelist
    sharelist_tuples = calc_helpers.get_sharelist_list(sharelist_name_fq)

    shares_actually_processed = 0
    if len(sharelist_tuples) > 0:
        with click.progressbar(sharelist_tuples, label="Performing 'process-2' (distributing CSV data into share folders)") as bar:
            for share_name, share_number in bar:
                if (share_name and only_share == '') or (share_number == only_share):
                    if calc_helpers.check_share_num(share_number):
                        gen_csv_oneshare(ctx, share_number,
                                         share_name, start_date)
                        shares_actually_processed = shares_actually_processed+1
                    else:
                        logging.warn(
                            f'share_number {share_number} has incorrect format. missing or incorrect bourse suffix?')

            print('\n')  # helps keep progressbar on its own line
            logging.info(
                f'{len(sharelist_tuples)} shares in sharelist. {shares_actually_processed} actually processed')

    else:
        logging.error(
            f"Share list file '{sharelist_name_fq}' empty or not found")

    logging.info(f'End {func_name} execution...')
    return


def farm_out_all_csv(ctx, sharelist_tuples: list, start_date: str):
    """ works its way thru all csv by day files and writes trades out into csv by share files

        unless user only wants a CSV By Share health check, in which case thats all it does
    """

    func_name = inspect.stack()[0][3]
    logging.info(f'Executing {func_name} ...')

    #csv_by_day_path = helpers.etl_path(ctx, g.CSV_BY_DAY_FOLDER)
    #csv_by_share_path = helpers.etl_path(ctx, g.CSV_BY_SHARE_FOLDER)

    # prepare list of output file names  we'll be writing plus obtain last timestamp of each share
    # remeber sharelist_tuples will appear to be only for .ETR shares, but that wont be the case
    # ie data from .FFM shares gets included (combined) with ETR trade data
    (outfile_names, out_share2last_tstamp) = prepare_csv_outfile_paths(sharelist_tuples, g.CSV_BY_SHARE_PATH)

    # find the oldest last_tstamp (they should all be equal usually)
    # and bump start_date forward to this date to help speed things up
    bumped_start_date = '2099-12-31 23:59:59'  # note: not underscores
    padded_start_date = start_date.replace('_', '-') + ' 00:00:00'
    most_out_of_date_sharenum = ''
    for (share_num, tstamp) in out_share2last_tstamp.items():
        # tstamp example: 2020-09-03 13:17:00
        if tstamp == '':
            bumped_start_date = padded_start_date
            most_out_of_date_sharenum = share_num
        elif tstamp < bumped_start_date and tstamp > padded_start_date:
            bumped_start_date = tstamp
            most_out_of_date_sharenum = share_num

    # ensure '-' becomes '_' again and strip hh:mm:ss off for onward use
    bumped_start_date = bumped_start_date.replace('-', '_')[:10]

    # compare bumped_start_date to today
    bumped_dt = datetime.strptime(bumped_start_date, '%Y_%m_%d')
    diff_days = datetime.now() - bumped_dt
    # print(f'diff_days={diff_days.days}')

    # safety check
    try:
        assert bumped_start_date >= start_date, f'bumped_start_date {bumped_start_date} should be >= start_date. Will use {start_date}'
    except AssertionError as error:
        logging.error(f'AssertionError: {error}')
        bumped_start_date = start_date

    logging.info(
        f"date '{bumped_start_date}' will be the start date for new CSV By_Share farmout")
    if diff_days.days > 10:
        print('\nRemove share {most_out_of_date_sharenum} from the current sharelist if its been delisted, else it will continue to slow farmout performance in the future\n')

    # All opened files will automatically be closed at the end of
    # the with ExitStack statement below, even if attempts to open files later
    # in the list raise an exception
    with ExitStack() as stack:

        # make a list of source 'by day' csv files
        src_csv_files = prepare_src_csv_files_list(g.CSV_BY_DAY_PATH, bumped_start_date)
        logging.info(f'{len(src_csv_files)} CSV files to trawl...')

        # Open all outfile handles for appending in ONE go.
        outfile_handles = [stack.enter_context(open(fname, 'a')) for fname in outfile_names]

        # sweep thru the list, writing header to each new output files
        # note: these handles are all open!
        for fp in outfile_handles:
            # print(fp.name)
            # if sharefile will be new, write a header to it
            must_write_header = fp.tell() == 0
            if must_write_header:
                fp.write(g.SHARE_CSV_HEADER)

        # we will need to lookup filehandles based on share_num
        # eg share2handleindex['A14Y6H.ETR'] = 7
        # NOTE we will use the same handle index for the A14Y6H.FFM trades as well
        share2handleindex = func_helpers.build_share2handleindex_dict(outfile_handles)
        #print(share2handleindex)
        #exit()

        # read thru all src files, distributing csv trades into csv files in individual share files
        for src_csv in src_csv_files:
            # fully qualified src file name
            src_csv_fq = join(g.CSV_BY_DAY_PATH, src_csv)
            trawl_csvfile_for_alltrades(src_csv_fq, bumped_start_date, outfile_handles, share2handleindex, out_share2last_tstamp)
            g.CONFIG_RUNTIME['process-2-last-csv-trawled'] = src_csv_fq
            save_runtime_config()

    # write all share hint files
    update_share_hint_files(ctx, sharelist_tuples, start_date)

    logging.info(f'End {func_name} execution...')


def gen_csv_byshare_onepass(ctx):
    """ IN ONE PASS, creates share specific csv files for every share in the sharelist file """

    func_name = inspect.stack()[0][3]
    logging.info(f'Executing {func_name} ...')

    # grab params from passed context
    start_date = ctx.obj['start_date']
    sharelist_name = ctx.obj['sharelist_name']
    #only_share = ctx.obj['only_share']
    # health_check = ctx.obj['health_check'] not referenced

    sharelist_name_fq = helpers.etl_path(
        ctx, f'{g.SHARELISTS_FOLDER}\{sharelist_name}')

    # obtain a list of share_name, share_number tuples from the sharelist
    # NOTE we the sharelist file will be composed of shares from one bourse 
    # by convention the ETR (Xetra)  bourse and so share numbers will end NNNNNNN.ETR
    # but since the NNNNNN part is common for FMM (Frankfurt) bourse also the ETR suffix in the 
    # share_number part will be ignored as far as trade importing is concerned
    # ie ALL trades will go into a single ByShare folder even though that folder gets named
    # with an ETR ending
    logging.info(f'preparing lists of shares and files...')
    sharelist_tuples = calc_helpers.get_sharelist_list(sharelist_name_fq)

    shares_actually_processed = 0
    if len(sharelist_tuples) > 0:

        if True: #(only_share == ''):
            # do bulk farm out
            g.CONFIG_RUNTIME['process-2-last-sharelist-name'] = sharelist_name_fq
            save_runtime_config()
            farm_out_all_csv(ctx, sharelist_tuples, start_date)
        # else:
        #     # doing ONLY ONE share, but allow progressbar to rapidly move thru all shares
        #     with click.progressbar(sharelist_tuples, label="Performing 'process-2' (distributing CSV data into share folders)") as bar:
        #         for share_name, share_number in bar:
        #             if (share_number == only_share):
        #                 if calc_helpers.check_share_num(share_number):
        #                     gen_csv_oneshare(ctx, share_number,
        #                                      share_name, start_date)
        #                     shares_actually_processed = shares_actually_processed+1
        #                 else:
        #                     logging.warn(
        #                         f'share_number {share_number} has incorrect format. missing or incorrect bourse suffix?')
        #         print('\n')  # helps keep progressbar on its own line
        #         logging.info(
        #             f'{len(sharelist_tuples)} shares in sharelist. {shares_actually_processed} actually processed')

    else:
        logging.error(
            f"Share list file '{sharelist_name_fq}' empty or not found")

    logging.info(f'End {func_name} execution...')
    return


def write_health_report(ctx):
    ''' '''

    report_wanted = ctx.obj['health_target']
    sharelist_name = ctx.obj['sharelist_name']
    #csv_by_share_path = helpers.etl_path(ctx, g.CSV_BY_SHARE_FOLDER)
    sharelist_name_fq = helpers.etl_path(
        ctx, f'{g.SHARELISTS_FOLDER}\{sharelist_name}')

    # obtain a list of share_name, share_number tuples from the sharelist
    sharelist_tuples = calc_helpers.get_sharelist_list(sharelist_name_fq)

    # HEALTH_REPORT_TARGETS = ['Stored-AllTables', 'By-Share-CSVs']
    logging.info(f'{report_wanted} health check...')
    if report_wanted == g.HEALTH_REPORT_TARGETS[0]:
        # assume its for the all-tables
        perform_alltable_health_check(sharelist_tuples, ctx.obj['stage'])
        pass
    elif report_wanted == g.HEALTH_REPORT_TARGETS[1]:
        # assume its for the 'By-Share-CSVs'
        perform_csv_by_share_health_check(
            sharelist_tuples, g.CSV_BY_SHARE_PATH)
    else:
        logging.error('unrecognized health target')


def write_status_report_txt(ctx) -> list:
    """ write a status report as plain text """

    func_name = inspect.stack()[0][3]
    logging.info(f'Executing {func_name} ...')

    #container_path = helpers.etl_path(ctx, '')

    report_txt = []
    report_txt.append(
        f"0  {datetime.now().strftime('%c')}\n")
    report_txt.append("1  \n")

    # os.walk doesnt give us the stats in the best order
    # we want TXT folder info first, then CSV, then by share.
    # Hence the leading numbers 1, 2, 3 ... below

    # r=>root, d=>directories, f=>files
    for r, d, f in os.walk(g.CONTAINER_PATH, topdown=True):
        if r.endswith(g.TXT_FOLDER):
            f.sort()
            if len(f) > 0:
                report_txt.append(
                    f'2  {r} ({len(f)} files): {f[0]} --> {f[-1]} \n\n')
            else:
                report_txt.append(
                    f"2  {r} (0) files -- all consumed  \n\n")
        if r.endswith(g.CONSUMED_FOLDER):
            f.sort()
            if len(f) > 0:
                report_txt.append(
                    f'2  {r} ({len(f)} files): {f[0]} --> {f[-1]} \n\n')
            else:
                report_txt.append(f'2  {r} ({len(f)} files) \n\n')
        elif r.endswith(g.CSV_BY_DAY_FOLDER):
            f.sort()
            if len(f) > 0:
                report_txt.append(
                    f'3  {r} ({len(f)} files): {f[0]} --> {f[-1]}\n\n')
            else:
                report_txt.append(f'2  {r} ({len(f)} files) \n\n')
        elif r.endswith(g.CSV_BY_SHARE_FOLDER):
            report_txt.append(f'4  {r} ({len(d)} share folders):\n')

    # also show current sharelists
    report_txt.append("5  \n")
    report_txt.append(f'6  Sharelists: {g.SHARELISTS}\n')

    # report in a specific order
    report_txt.sort()
    for index, line in enumerate(report_txt):
        report_txt[index] = report_txt[index][2:]

    status_report_name_fq = f'{g.CONTAINER_PATH}\{g.STATUS_REPORT_NAME}'
    with open(status_report_name_fq, 'a') as statusf:
        statusf.writelines(report_txt)
        statusf.write("----------"*8)
        statusf.write("\n")

    logging.info(f'End {func_name} execution...')
    return report_txt


def perform_csv_by_share_health_check(sharelist_tuples: list, csv_by_share_path: str) -> dict:
    ''' report on the monoticity of the timestamps in each CSV By Share file '''

    out_sharefile_health = {}
    issue_count = 0

    report_fq = f'{g.CONTAINER_PATH}\{g.REPORTS_FOLDER}\By_Share_health_check.txt'
    f = open(report_fq, 'w')
    rpt_msg = f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
    f.write(rpt_msg)

    for share_name, share_num in sharelist_tuples:
        if calc_helpers.check_share_num(share_num):
            # ensure folder exists for this share (share_path assumed to exist)
            single_share_directory = f'{csv_by_share_path}\{share_num}'
            if not exists(single_share_directory):
                # mkdir(single_share_directory)
                rpt_msg = f'health_check: folder {single_share_directory} not found'
                f.write(f'{rpt_msg}\n')
                logging.warn(rpt_msg)
                continue

            # the name of the CSV file we'll be checking
            out_sharefile_fq_name = f'{csv_by_share_path}\{share_num}\{share_num}.CSV'
            # obtain a single monotonicity value for this file
            out_sharefile_health[share_num] = check_monotonicity(
                out_sharefile_fq_name)
            thumbs_up = out_sharefile_health[share_num][0] == 0
            if not thumbs_up:
                issue_count = issue_count+1
                rpt_msg = f'{share_num} loses monotonicity on line {out_sharefile_health[share_num][0]} at {out_sharefile_health[share_num][1]}'
                f.write(f'{rpt_msg}\n')
                logging.error(rpt_msg)
        else:
            rpt_msg = f'health_check: share_number {share_num} has incorrect format. missing or incorrect bourse suffix?'
            f.write(f'{rpt_msg}\n')
            logging.warn(rpt_msg)

    rpt_msg = f'{issue_count} files had monotonicity issues'
    f.write(f'{rpt_msg}\n')
    logging.info(rpt_msg)

    f.close()
    return out_sharefile_health


def write_status_report_md() -> list:
    """ write a status report in markdown format """

    func_name = inspect.stack()[0][3]
    logging.info(f'Executing {func_name} ...')

    # container_path = g.CONTAINER_PATH  # helpers.etl_path(ctx, '')

    report_md = []
    report_md.append(
        f"0  **SW BSBETL Status Report** at {datetime.now().strftime('%c')}  \n")
    report_md.append("1    \n")

    # os.walk doesnt give us the stats in the best order
    # we want TXT folder info first, then CSV, then by share.
    # Hence the leading numbers 1, 2, 3 ... below

    # r=>root, d=>directories, f=>files
    for r, d, f in os.walk(g.CONTAINER_PATH, topdown=True):
        if r.endswith(g.TXT_FOLDER):
            if len(f) > 0:
                f.sort()
                report_md.append(
                    f'2  * `{r}` ({len(f)} TXT files): {f[0][0:-4]} ==> {f[-1][0:-4]}  \n')
            else:
                report_md.append(
                    f'2  * `{r}` (0 TXT files): **all consumed** \n')
            report_md.append(
                "2  > associated command: _fetch-txt_ will fetch more TXT files from the download service\n")
        elif r.endswith(g.CONSUMED_FOLDER):
            if len(f) > 0:
                f.sort()
                report_md.append(
                    f'3  * `{r}` ({len(f)} TXT files): {f[0][0:-4]} ==> {f[-1][0:-4]}  \n')
            else:
                report_md.append(
                    f'3  * `{r}` ({len(f)} TXT files):   \n')
        elif r.endswith(g.CSV_BY_DAY_FOLDER):
            if len(f) > 0:
                f.sort()
                report_md.append(
                    f'3  * `{r}` ({len(f)} TXT.CSV files): {f[0][0:-8]} ==> {f[-1][0:-8]}  \n')
            else:
                report_md.append(
                    f'3  * `{r}` ({len(f)} TXT.CSV files):   \n')
            report_md.append(
                "3  > associated command: _process-1_ will transfer the TXT files as ~TXT.CSV files to the `OUT\By_Day` folder\n")
        elif r.endswith(g.CSV_BY_SHARE_FOLDER):
            report_md.append(f'4  * `{r}` ({len(d)} share folders): \n')
            report_md.append(
                "4  > associated command: _process-2_ extracts new trades from the `By_Day` files and distribute to share-specific CSV files in the `By_Share` folders\n")

    # also show current sharelists
    report_md.append("5  \n")
    report_md.append('6  \n**Sharelist files**:  \n')
    report_md.append("7  \n")
    report_md.append('8  \n' + ', '.join(g.SHARELISTS) + '\n')
    report_md.append("9  \n")
    #last_processed_sharelist = g.CONFIG_RUNTIME['last_processed_sharelist']
    #report_md.append(f"  Last processing was under **'{last_processed_sharelist}'** sharelist  \n")
    report_md.append(f"  Last **process-3** parameters: **{g.CONFIG_RUNTIME['process-3-last-parameters']}**  \n")
    # report_md.append('A  \n**Processing**:')
    # report_md.append(f"B  \n{g.CONFIG_RUNTIME['last_processed_sharelist']}")
    # report_md.append(f'B  \n' + json.dumps(g.CONFIG_RUNTIME, indent='\n',))

    # report in a specific order
    # report_md.sort()
    # strip off sorting guide numbers
    for index, line in enumerate(report_md):
        report_md[index] = report_md[index][2:]

    status_report_name_fq = f'{g.CONTAINER_PATH}\{g.STATUS_REPORT_NAME}.MD'
    with open(status_report_name_fq, 'w') as statusf:
        for line in report_md:
            statusf.write(line)

    logging.info(f'End {func_name} execution...')
    return report_md


def read_status_report_md() -> str:

    status_report_name_fq = f'{g.CONTAINER_PATH}\{g.STATUS_REPORT_NAME}.MD'
    with open(status_report_name_fq, 'r') as statusf:
        return statusf.read()


def get_stored_df_summary_by_share_num(share_num: str, stage: int = 1) -> tuple:
    """ extract some info for share dataframe from HDFStore and return as a tuple """

    data_store = pd.HDFStore(g.SHARE_STORE_FQ.format(stage))
    try:
        assert len(share_num) == 10, f'share_num {share_num} malformed'
        share_key = share_num[-3:] + '_' + share_num[0:-4]
        # extract dataframe
        df = data_store[share_key]
        return (df.index[0], df.index[-1], df.shape[0], df.shape[1])

    except AssertionError as ae:
        logging.error(f'Assertion Error {ae}')
        return None

    except KeyError as ke:
        # print(f'Key Error {ke}')
        logging.error(f'Key Error {ke}')
        return None

    finally:
        data_store.close()


def perform_alltable_health_check(shlist_tuples: list, stage: int):

    report_fq = f'{g.CONTAINER_PATH}\{g.REPORTS_FOLDER}\\AllTable_health_check.txt'
    f = open(report_fq, 'w')
    rpt_msg = f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
    f.write(rpt_msg)
    f.write('stage-1 alltables:\n\n')
    for _, share_number in shlist_tuples:
        summary = get_stored_df_summary_by_share_num(share_number, stage)
        rpt_msg = f'{share_number}: {summary[2]} rows x {summary[3]} cols, {summary[0]} -> {summary[1]}'
        logging.info(rpt_msg)
        f.write(f'{rpt_msg}\n')

    f.close()


def num_unconsumed_txt_files() -> int:
    ''' determines the number if any of TXT files residing in the IN folder '''

    glob_spec = g.CONTAINER_PATH+'\\'+g.TXT_FOLDER+'\\*.TXT'
    list_of_txts = glob.glob(glob_spec)
    return len(list_of_txts)

def get_df_from_store(store_fq,key) -> pd.DataFrame:

    try:
        store = pd.HDFStore(store_fq)
        df = store[key]
    except KeyError as ke:
        df = pd.DataFrame()
        logging.warn(f'Key Error {ke} ({store_fq}) - empty one will be used')                
    finally:
        store.close()
        return df

def compile_results_1St(overwrite_results :bool, sharelist :str) -> dict:
    ''' go thru all overviews and the daily price conditions for the initial stage
    '''

    logging.info(f'Performing results-1 ...')

    fmt="applying _1St_condition {0}"
    activity=f'extracting Ov from store'

    dependencies = {}

    # we work with stage 2 overviews since it ought to have all the needed values
    ov_df = load_overview_df(sharelist, 2)

    try:
        
        results_df = None
        if overwrite_results:
            # ensure an empty results dataframe starter 9 - a row for every share 
            # containing Status,ShareName,Date with a ShareNumber index
            results_df=build_results_starter_df(reference_ov=ov_df)
            #print(results_df.head(30))
        else:
            # we must update an existing results file (if present)
            results_df = load_results_df(g._1ST_RESULTS_STORE_FQ, results_key=sharelist)


        report_f = open(g.REPORTS_PATH + "\\_1St_results_report.txt", "w", encoding="utf-8")
        activity=fmt.format('a')
        dependencies['a'] = _1St_Condition_a(ov_df, results_df, report_f)
        #print(f'results_df={results_df.shape[0]}')

        activity=fmt.format('b')
        dependencies['b'] = _1St_Condition_b(ov_df, results_df, report_f)

        activity=fmt.format('c')
        dependencies['c'] = _1St_Condition_c(ov_df, results_df, report_f)

        activity=fmt.format('d')
        dependencies['d'] = _1St_Condition_d(ov_df, results_df, report_f)

        # finally save the results
        calc_helpers._1St_results_dataframe_to_store(results_df, sharelist)

        # spin off an excel spreadsheet for quick audit reference
        xslx_name_fq = f'{g.OUT_PATH}\\_1St_results.xlsx'
        results_df.to_excel(xslx_name_fq)

    except KeyError as ke:
        logging.error(f'Key Error {ke}, activity: {activity}')

    finally:
        report_f.close()
    
    return dependencies

def compile_results_2StPr(overwrite_results :bool, sharelist :str) -> dict:
    ''' go thru all overviews and the price conditions for the 2StPr
    '''
    logging.info(f'Performing results-2StPr ...')

    fmt="applying _2StPr_condition {0}"
    activity=f'extracting Ov from store'

    dependencies = {}
    # we work with stage 2 overviews since it ought to have all the needed values
    ov_df = load_overview_df(sharelist, 2)

    try:

        results_df = None
        if overwrite_results:
            # ensure an empty results dataframe starter
            results_df=build_results_starter_df(reference_ov=ov_df)
            #print(results_df.head(30))
        else:
            # we must update an existing results file (if present)
            results_df = load_results_df(g._2STPR_RESULTS_STORE_FQ, results_key=sharelist)

        report_f = open(g.REPORTS_PATH + "\\_2StPr_results_report.txt", "w", encoding="utf-8")

        activity=fmt.format('a1')
        dependencies['a1'] = _2StPr_Condition_a1(ov_df, results_df, report_f)

        activity=fmt.format('a2')
        dependencies['a2'] = _2StPr_Condition_a2(ov_df, results_df, report_f)

        activity=fmt.format('a3')
        dependencies['a3'] = _2StPr_Condition_a3(ov_df, results_df, report_f)

        activity=fmt.format('b')
        dependencies['b'] = _2StPr_Condition_b(ov_df, results_df, report_f)

        activity=fmt.format('c')
        dependencies['c'] = _2StPr_Condition_c(ov_df, results_df, report_f)

        activity=fmt.format('d')
        dependencies['d'] = _2StPr_Condition_d(ov_df, results_df, report_f)

        activity=fmt.format('e')
        dependencies['e'] = _2StPr_Condition_e(ov_df, results_df, report_f)

        activity=fmt.format('f')
        dependencies['f'] = _2StPr_Condition_f(ov_df, results_df, report_f)

        activity=fmt.format('g')
        dependencies['g'] = _2StPr_Condition_g(ov_df, results_df, report_f)

        activity=fmt.format('h')
        dependencies['h'] = _2StPr_Condition_h(ov_df, results_df, report_f)

        activity=fmt.format('i')
        dependencies['i'] = _2StPr_Condition_i(ov_df, results_df, report_f)

        activity=fmt.format('j')
        dependencies['j'] = _2StPr_Condition_j(ov_df, results_df, report_f)

        # finally save the results
        calc_helpers._2StPr_results_dataframe_to_store(results_df, sharelist)

        # spin off an excel spreadsheet for quick audit reference
        xslx_name_fq = f'{g.OUT_PATH}\\_2StPr_results.xlsx'
        results_df.to_excel(xslx_name_fq)

    except KeyError as ke:
        logging.error(f'Key Error {ke}, activity: {activity}')

    finally:
        report_f.close()
    
    return dependencies

def compile_results_2StVols(overwrite_results :bool, sharelist :str) -> dict:
    ''' go thru all overviews and the price conditions for the 2StPr
    '''

    logging.info(f'Performing results-2StVols ...')
    fmt="applying _2StVols_condition {0}"
    activity=f'extracting Ov from store'

    dependencies = {}
    # we work with stage 2 overviews since it ought to have all the needed values
    ov_df = load_overview_df(sharelist, 2)

    #strip 'no data' shares
    #ov_df = ov_df[ov_df['Status'] != 'no data'].copy()

    try:

        results_df = None
        if overwrite_results:
            # ensure an empty results dataframe starter
            results_df=build_results_starter_df(reference_ov=ov_df)
        else:
            # we must update an existing results file (if present)
            results_df = load_results_df(g._2STVOLS_RESULTS_STORE_FQ, results_key=sharelist)

        report_f = open(g.REPORTS_PATH + "\\_2StVols_results_report.txt", "w", encoding="utf-8")
        activity=fmt.format('a1')
        dependencies['a1'] = _2StVols_Condition_a1(ov_df, results_df, report_f)

        activity=fmt.format('a2')
        dependencies['a2'] = _2StVols_Condition_a2(ov_df, results_df, report_f)

        activity=fmt.format('b')
        dependencies['b'] = _2StVols_Condition_b(ov_df, results_df, report_f)
        activity=fmt.format('c')
        dependencies['c'] = _2StVols_Condition_c(ov_df, results_df, report_f)
        activity=fmt.format('d')
        dependencies['d'] = _2StVols_Condition_d(ov_df, results_df, report_f)
        activity=fmt.format('e')
        dependencies['e'] = _2StVols_Condition_e(ov_df, results_df, report_f)
        activity=fmt.format('f')
        dependencies['f'] = _2StVols_Condition_f(ov_df, results_df, report_f)

        # finally save the results
        calc_helpers._2StVols_results_dataframe_to_store(results_df,sharelist)

        #spin off an excel spreadsheet for quick audit reference
        xslx_name_fq = f'{g.OUT_PATH}\\_2StVols_results.xlsx'
        results_df.to_excel(xslx_name_fq)

    except KeyError as ke:
        logging.error(f'Key Error {ke}, activity: {activity}')

    finally:
        report_f.close()
    
    return dependencies

def compile_3jP_part1(overwrite_results :bool, sharelist :str) -> dict:
    ''' create a source Overview per Gunther rules to arrive at the 'source' set of shares
        per 3. St jP 1.:
        NOTE sharelist is expected to be Default 
        Creates 1) a results_3jP.shl sharelist (after placing/updating _3jP_list in config_runtime.json)
        and 2) a saved results_3jp dataframe
    '''

    logging.info(f"Performing compile_3jP_part1(overwrite_results={overwrite_results}, sharelist={sharelist})")

    activity=f'compile_3jP_part1'

    dependencies = {}
    report_f = open(g.REPORTS_PATH + "\\_3jP_part1_results_report.txt", "w", encoding="utf-8")
    
    # we work with stage 2 overviews since it ought to have all the needed values
    ov_df = load_overview_df(sharelist, 2)

    try:
        
        results_df = None
        if overwrite_results:
            # ensure an empty results dataframe starter
            results_df=build_results_starter_df(reference_ov=ov_df)
        else:
            # we must update an existing results file (if present)
            results_df = load_results_df(g._3JP_RESULTS_PART1_STORE_FQ, results_key=sharelist)

        # now to thin out the overview based on Gunther's 3 jumped Price 210623.odt
        # by using the prior combined results below, we can access any condition's results 
        # via a single dataframe. here ShareNumber will be the index
        combined_results_df = prepare_combined_1_2_results(sharelist) # combines 1St,2StPr and 2StVols results
        # get rid of the NaNs
        combined_results_df.fillna('',inplace=True)
        #print(combined_results_df.head())

        #grab a copy of the combined results now as results-3jP
        #we will display this full unfiltered dataframe in the web app results-3jP page (saved later below)
        results_3jP_part1_df = combined_results_df.copy()
        # create a '_3jP_list' column (with default value FAIL) of the 3jP results table the user will be able to see
        results_3jP_part1_df['3. StjP1'] = g.FAIL

        # filter out failing conditions
        results_3jP_passing_df = create_combined_passing_ov(report_f, combined_results_df)

        # go on to prepare _3jP_list (stored in config_runtime.json) of shares which this stage chooses 
        results_3jP_passing_df.reset_index(inplace=True,drop=True) # ShareNumber is already a column
        # extract list of ShareNumbers and ShareNames
        final_passing_shares = results_3jP_passing_df['ShareNumber'].to_list()
        final_passing_sharenames = results_3jP_passing_df['ShareName'].to_list()

        # update '3. StjP1' column of results_3jP_part1 based on presence in the passing shares list
        results_3jP_part1_df.loc[results_3jP_part1_df['ShareName'].isin(final_passing_sharenames), '3. StjP1'] = g.PASS
        # save results df so user may view
        calc_helpers._3jP_results_dataframe_to_store(results_3jP_part1_df, sharelist, '_3jP_part1')

        # save _3jP_list in runtime config: (a list of [ShareNumber, ShareName] lists) so that
        # we may create a results_3jP sharelist
        ov_df.reset_index(inplace=True)
        part1_ov_df = ov_df[ov_df['ShareNumber'].isin(final_passing_shares)]
        _3jP_chosens = zip(part1_ov_df['ShareNumber'], part1_ov_df['ShareName'])
        g.CONFIG_RUNTIME['_3jP_list']  = list(_3jP_chosens)
        save_runtime_config()

        # spin off the sharelist as mentioned above - this will be in use immediately after 
        # this function ends (see command results_3stjp_1 in cli.py) 
        calc_helpers.create_results_3jP_sharelist()

        # write this list of chosen shares to the audit report also
        report_f.write(f"3jP chosen list ({len(g.CONFIG_RUNTIME['_3jP_list'])} shares):  \n")
        for share_pair in g.CONFIG_RUNTIME['_3jP_list']:
            report_f.write(f'**{share_pair[0]}** {share_pair[1]}   \n') # number name

        # NOTE we will switch to results_3jP sharelist and 
        # re-run process-3 under that sharelist - this will get PSMV computed in both Ats and Ov
        logging.info(f"'results_3jP' sharelist with {len(part1_ov_df)} qualifying shares now available ...")    

        # NOTE later
        # report_f = open(g.REPORTS_PATH + "\\_2StVols_results_report.txt", "w", encoding="utf-8")
        # spin off an excel spreadsheet for quick audit reference
        #xslx_name_fq = f'{g.OUT_PATH}\\_3jP_part1_results.xlsx'
        #part1_ov_df.to_excel(xslx_name_fq)

    except KeyError as ke:
        logging.error(f'Key Error {ke}, activity: {activity}')

    finally:
        report_f.close()
        #ov_data_store.close()
    
    return dependencies

def create_combined_passing_ov(report_f, combined_results_ov):
    ''' apply conditions per 2. Stage Prices to combined results and return a reduced row count combined_results '''

    # filter per above
    pass_mask = (combined_results_ov['_1St.Con_a'].str.contains(g.PASS)) | \
                (combined_results_ov['_1St.Con_b'].str.contains(g.PASS)) | \
                (combined_results_ov['_1St.Con_c'].str.contains(g.PASS)) | \
                (combined_results_ov['_1St.Con_d'].str.contains(g.PASS))

    # this gets all those shares passing stage 1
    # NOTE _1st.Con_a thru _1st.Cond_d are all either ticks or crosses
    combined_passing_ov = combined_results_ov[pass_mask] 
    report_f.write(f"**{len(combined_passing_ov)}** shares pass *_1St.Con_a OR _1St.Con_b OR _1St.Con_c OR _1St.Con_d*  \n  \n")

    # we filter again
    # ... and in the "2. Stage Prices" condition a1) 
    # NOTE _2StPr.Con_a1 can be assumed to be numbers only
    combined_passing_ov = combined_passing_ov[combined_passing_ov['_2StPr.Con_a1'] > 3]
    report_f.write(f"**{len(combined_passing_ov)}** shares remain after additionally applying *_2StPr.Con_a1 (which holds DHPlasthi) > 3*  \n  \n")

    # finally
    # ... and which passed Condition c) with ... please (see choice in "2 Prices..." ) code a soft param CjP.
    #     (DHPD / DHOCPD-1)eDH/LOCP  > CjP  
    #     CjP = 1.00 ... 1.20 
    #so we need the CjP setting in _3jP_conditions
    CjP = _3jP_conditions['Con_a']['CjP'] # used later below

    #filter in those shares passing _2StPr.Con_c1 thru 5
    # NOTE these columns contain numbers with trailing ticks and crosses, '-' as well
    pass_mask = (combined_passing_ov['_2StPr.Con_c1'].str.contains(g.PASS)) | \
                (combined_passing_ov['_2StPr.Con_c2'].str.contains(g.PASS)) | \
                (combined_passing_ov['_2StPr.Con_c3'].str.contains(g.PASS)) | \
                (combined_passing_ov['_2StPr.Con_c4'].str.contains(g.PASS)) | \
                (combined_passing_ov['_2StPr.Con_c5'].str.contains(g.PASS))

    combined_passing_ov = combined_passing_ov[pass_mask] 

    #we want only those who passed with values > CjP
    #strip the PASS symbol (if any)
    if len(combined_passing_ov) > 0:
        con_c_cols = ['_2StPr.Con_c1','_2StPr.Con_c2','_2StPr.Con_c3','_2StPr.Con_c4','_2StPr.Con_c5']
        for col in con_c_cols:
            # NOTE there will be no FAILs, nor any 'no data' values
            # convert what remains into floats or NaNs
            combined_passing_ov[col] = combined_passing_ov[col].str.replace(g.PASS,'')
            combined_passing_ov[col] = combined_passing_ov[col].str.replace('-','')
            combined_passing_ov[col] = combined_passing_ov[col].replace('',NaN)
            #now filter in only those shares whose Con_c_column > CjP
            #convert to float (blanks become NaNs)
        for col in con_c_cols:
            combined_passing_ov[col] = combined_passing_ov[col].astype(float)
            #print(combined_passing_ov[Con_c_columns].head(20))

            # select if ANY share passes any of these conditions 
        cjp_mask =  (combined_passing_ov['_2StPr.Con_c1'] > CjP) | \
                        (combined_passing_ov['_2StPr.Con_c2'] > CjP) | \
                        (combined_passing_ov['_2StPr.Con_c3'] > CjP) | \
                        (combined_passing_ov['_2StPr.Con_c4'] > CjP) | \
                        (combined_passing_ov['_2StPr.Con_c5'] > CjP) 

        combined_passing_ov = combined_passing_ov[cjp_mask]
        # passing_ov now contains ONLY those shares which will be select for the _3jP list
        #print(passing_ov[con_c_cols].head(20))

    report_f.write(f"**{len(combined_passing_ov)}** shares remain (for the 3jP chosen list) after additionally requiring *_2StPr.Con_c1 thru _2StPr.Con_c5* to exceed {CjP}  \n  \n")
    return combined_passing_ov

def compile_3jP_part2(sharelist :str) -> dict:
    ''' 3. St jP 2.:
        Check how long it is exceptional:
        .. and onwards..
        NOTE sharelist will be a reduced results_3jP sharelist
    '''

    cur_func_desc = f"Performing compile_3jP_part2(sharelist={sharelist})"
    logging.info(cur_func_desc)
    dependencies = {}

    # load stage 2 Default ov
    ov_df = load_overview_df('Default', 2)

    try:
        # load 3jP results saved in part 1        
        results_df = load_results_df(g._3JP_RESULTS_PART1_STORE_FQ, results_key='Default')

        activity=cur_func_desc + ': compute_djp'
        compute_djp(ov_df, results_df)

        # finally save the 3jP part_2 results 
        activity=cur_func_desc + ': _3jP_results_dataframe_to_store'
        calc_helpers._3jP_results_dataframe_to_store(results_df, 'Default', '_3jP_part2')

        # plus save an ov
        # we want only the shares in _3jP_list
        activity=cur_func_desc + ': plus save an ov...'
        final_shares = [sp[0] for sp in g.CONFIG_RUNTIME['_3jP_list']]
        #final_ov_df = ov_df[ov_df['ShareNumber'].isin(final_shares)]
        final_ov_df = ov_df[ov_df.index.isin(final_shares)]
        logging.info(f"_3jP_list overview has {len(final_ov_df)} shares")
        calc_helpers.ov_dataframe_to_store(final_ov_df,g.HDFSTORE_OV_KEY.format('results_3jP.shl',2),2,'results_3jP')

        # spin off an excel spreadsheet for quick audit reference
        activity=cur_func_desc + ': spin off excel...'
        xslx_name_fq = f'{g.OUT_PATH}\\_3jP_results_part2.xlsx'
        results_df.to_excel(xslx_name_fq)

    except KeyError as ke:
        logging.error(f'Key Error {ke}, activity: {activity}')
    except Exception as exc:
        logging.error(f'Exception {exc}, activity: {activity}')

    return dependencies

def compile_3V2d_part1(overwrite_results :bool, sharelist :str) -> dict:
    ''' 3. Stage, Vol up few days (no big jump) "V2d":
        NOTE sharelist ('Default.shl') has .shl ending
        Prepares a V2d sharelist such that BackwardsSlowDailyVol computations can be performed
        afterwards in preparation for part 2 which will create a results table and save a final overview,
        overwriting the preliminary one saved here
    '''

    logging.info(f"Performing compile_3V2d_part1(overwrite_results={overwrite_results}, sharelist={sharelist}) ... to create a 'results_V2d' (initial) ov & sharelist")    
    activity=f'compile_3V2d_part1'
    dependencies = {}
    report_f = open(g.REPORTS_PATH + "\\_3V2d_results_report.txt", "w", encoding="utf-8")

    try:
        # we work with latest stage 2 overviews on Default sharelist 
        ov_df = load_overview_df(sharelist, 2)
        #print(ov_df[['RbSDV.D-4','RbSDV.D-7']])
        #exit()

        results_df = None
        if overwrite_results:
            # ensure an empty results dataframe starter
            results_df=build_results_starter_df(reference_ov=ov_df)
        else:
            # we must update an existing results file (if present)
            results_df = load_results_df(g._3V2D_RESULTS_STORE_FQ, results_key=sharelist)

        #NOTE get combined_1_2_results() (referenced immediately below) 
        combined_res_ov = load_results_df(g._COMBINED_1_2_RESULTS_STORE_FQ, results_key='Default')

        logging.info(f'Selecting shares from Combined Results dataframe...')
        
        # filter per above
        pass_mask = (combined_res_ov['_1St.Con_a'].str.contains(g.PASS)) | \
                    (combined_res_ov['_1St.Con_b'].str.contains(g.PASS)) | \
                    (combined_res_ov['_1St.Con_c'].str.contains(g.PASS)) | \
                    (combined_res_ov['_1St.Con_d'].str.contains(g.PASS))
        # this gets all those shares passing stage 1
        combined_passing_ov = combined_res_ov[pass_mask]
        report_f.write(f"**{len(combined_passing_ov)}** shares pass *_1St.Con_a OR _1St.Con_b OR _1St.Con_c OR _1St.Con_d*  \n  \n")

        # we filter again
        # ... and in the "2. Stage Prices" condition a1) 
        # pass_mask = combined_passing_ov['_2StPr.Con_a1'] > 3
        # combined_passing_ov = combined_passing_ov[pass_mask]
        # report_f.write(f"**{len(combined_passing_ov)}** shares remain after additionally applying *_2StPr.Con_a1 > 3 (_2StPr.Con_a1 actually holds DHPlasthi)*  \n  \n")

        # ... and which passed condition "Vol In. Con.e)" in the "2. Stage Vols".
        pass_mask = combined_passing_ov['_2StVols.Con_e'].str.contains(g.PASS)
        combined_passing_ov = combined_passing_ov[pass_mask]
        report_f.write(f"**{len(combined_passing_ov)}** shares remain after additionally requiring *_2StVols.Con_e* pass  \n  \n")
        #report_f.write('\npart2 to follow...  \n')

        combined_passing_ov.reset_index(inplace=True, drop=True)
        final_passing_shares = combined_passing_ov['ShareNumber'].to_list()

        # add these columns now  grabbing values from ov (for part 2 coming up)
        results_df['RbSDV.D-4'] = ov_df['RbSDV.D-4']
        results_df['RbSDV.D-7'] = ov_df['RbSDV.D-7']

        ov_df.reset_index(inplace=True)
        part1_ov_df = ov_df[ov_df['ShareNumber'].isin(final_passing_shares)]

        _V2d_chosens_zip = zip(part1_ov_df['ShareNumber'], part1_ov_df['ShareName'])
        g.CONFIG_RUNTIME['_V2d_list']  = list(_V2d_chosens_zip)
        save_runtime_config()
        #spin off a sharelist as well - this will be in use immediately after 
        # this function ends (see command results_3stv2d_1 in cli.py) 
        calc_helpers.create_results_V2d_sharelist()
        logging.info(f"Created 'results_V2d' sharelist with {len(part1_ov_df)} qualifying shares...")    

        report_f.write(f"v2d chosen list ({len(g.CONFIG_RUNTIME['_V2d_list'])} shares):  \n")
        for share_pair in g.CONFIG_RUNTIME['_V2d_list']:
            report_f.write(f'**{share_pair[0]}** {share_pair[1]}  \n')

        # save an Ov for 'results_V2d.shl' (preliminary - gets overwritten in part 2)
        ov_key=g.HDFSTORE_OV_KEY.format('results_V2d.shl',2)
        calc_helpers.ov_dataframe_to_store(part1_ov_df, ov_key, 2, 'results_V2d')

        # We save a results dataframe as well for viewing on the 3V2d page
        # NOTE it will get amended and resaved in part 2
        results_df['_1St.Con_a'] = combined_res_ov['_1St.Con_a']
        results_df['_1St.Con_b'] = combined_res_ov['_1St.Con_b']
        results_df['_1St.Con_c'] = combined_res_ov['_1St.Con_c']
        results_df['_1St.Con_d'] = combined_res_ov['_1St.Con_d']
        results_df['_2StVols.Con_e'] = combined_res_ov['_2StVols.Con_e']

        # finally save results 
        calc_helpers._3V2d_results_dataframe_to_store(results_df,sharelist)

        # spin off an excel spreadsheet for quick audit reference
        xslx_name_fq = f'{g.OUT_PATH}\\_3V2d_part1_results.xlsx'
        results_df.to_excel(xslx_name_fq)
    
    except KeyError as ke:
        logging.error(f'Key Error {ke}, activity: {activity}')
    except Exception as exc:
        logging.error(f'Exception {exc}, activity: {activity}')

    finally:
        report_f.close()
    
    return dependencies

def compile_3V2d_part2(overwrite_results :bool, sharelist :str) -> dict:
    ''' 3. Stage, Vol up few days (no big jump) "V2d": part 2
        sharelist will be = 'results_V2d.shl'
    '''

    logging.info(f'Performing compile_3V2d_part2... sharelist={sharelist} overwrite_results={overwrite_results}')
    activity=f'compile_3V2d_part2'

    dependencies = {}

    try:
        # we work with latest stage 2 overviews on the V2d sharelist 
        ov_df = load_overview_df(sharelist, 2)

        # we work with the (assumed) already created results from part 1
        results_df = load_results_df(g._3V2D_RESULTS_STORE_FQ, results_key='Default')

        report_f = open(g.REPORTS_PATH + "\\_3V2d_results_report.txt", "a", encoding="utf-8")

        # populate these results columns now
        results_df['RbSDV.D-7÷RbSDV.D-4'] = results_df['RbSDV.D-7'] / results_df['RbSDV.D-4']
        # pass or fail indicators
        results_df['RbSDV.D-7÷RbSDV.D-4'] = results_df['RbSDV.D-7÷RbSDV.D-4'].apply(lambda x: f'{x} {g.FAIL}' if x > 0.7 else f'{x} {g.PASS}')
        results_df['RbSDV.D-7÷RbSDV.D-4'] = results_df['RbSDV.D-7÷RbSDV.D-4'].apply(lambda x: NaN if x.startswith('nan') else x)
        #print(results_df.head(20))

        # save an Ov for 'results_V2d.shl' (overwriting the premliminary one from part 1)
        ov_key = g.HDFSTORE_OV_KEY.format(sharelist,2)
        calc_helpers.ov_dataframe_to_store(ov_df,ov_key, 2, sharelist)
        logging.info(f'{len(ov_df)} Qualifying shares saved in the Overview for results V2d  \n  \n')        

        # NOTE here we save an updated results datafame for viewing on page 3V2d

        calc_helpers._3V2d_results_dataframe_to_store(results_df,'Default') #sharelist)

        # spin off an excel spreadsheet for quick audit reference
        xslx_name_fq = f'{g.OUT_PATH}\\_3V2d_part2_results.xlsx'
        results_df.to_excel(xslx_name_fq)

    except KeyError as ke:
        logging.error(f'Key Error {ke}, activity: {activity}')
    except Exception as exc:
        logging.error(f'Exception {exc}, activity: {activity}')

    finally:
        report_f.close()

    return dependencies

def compile_3nH(sharelist :str) -> dict:
    ''' 3. Stage, New Heights "3nH":
        NOTE sharelist ('Default.shl') has .shl ending
    '''

    logging.info(f'Performing compile_3nH... sharelist={sharelist}')
    activity='compile_3nH'
    dependencies = {}
    report_f = open(g.REPORTS_PATH + "\\_3nH_results_report.txt", "a", encoding="utf-8")

    try:
        # we work with latest stage 2 overviews on Default sharelist 
        ov_df = load_overview_df(sharelist, 2)

        # ensure an empty results dataframe starter
        results_df=build_results_starter_df(reference_ov=ov_df)

        #NOTE get combined_1_2_results() (referenced immediately below) 
        combined_results = load_results_df(g._COMBINED_1_2_RESULTS_STORE_FQ, results_key='Default')

        #Take the shares which passed the 1. Stage...
        pass_mask = (combined_results['_1St.Con_a'].str.contains(g.PASS)) | \
                    (combined_results['_1St.Con_b'].str.contains(g.PASS)) | \
                    (combined_results['_1St.Con_c'].str.contains(g.PASS)) | \
                    (combined_results['_1St.Con_d'].str.contains(g.PASS))
        # this gets all those shares passing stage 1
        coll0_df = combined_results[pass_mask]
        report_f.write(f"**{len(coll0_df)}** shares pass *_1St.Con_a thru _1St.Con_d* \n  \n")
        
        #update results_df as we go along
        #first add the needed columns 
        results_df['_1St.Con_a'] = combined_results['_1St.Con_a']
        results_df['_1St.Con_b'] = combined_results['_1St.Con_b']
        results_df['_1St.Con_c'] = combined_results['_1St.Con_c']
        results_df['_1St.Con_d'] = combined_results['_1St.Con_d']
        results_df['_2StPr.Con_a1'] = combined_results['_2StPr.Con_a1']
        results_df['SDLOCPGrsl'] = ov_df['SDLOCPGrsl']
        results_df['_2StPr.Con_a3'] = combined_results['_2StPr.Con_a3']
        results_df['DLOCup'] = ov_df['DLOCup']

        # let coll0_df be the update source
        #results_df.update(coll0_df)

        # we filter again
        # ... and in the "2. Stage Prices" condition a1) 
        coll0_df = coll0_df[coll0_df['_2StPr.Con_a1'] > 3]

        #update results_df as we go along
        #results_df.update(coll0_df['_2StPr.Con_a1'])

        report_f.write(f"**{len(coll0_df)}** shares remaining after applying *_2StPr.Con_a1 > 3*  \n  \n")
        # convert to a list
        activity=f'resetting index on coll0_df'
        coll0_df.reset_index(inplace=True,drop=True)
        coll0_shares = coll0_df['ShareNumber'].to_list()

        # work with successive separate collections
        # shares which the SDLOCPGrsl D (calced in "2. Stage Prices" , 5.) is SDLOCPGrsl D > 1
        coll1_df = ov_df[ov_df['SDLOCPGrsl']  > 1]
        report_f.write(f"**{len(coll1_df)}** shares pass the condition *(SDLOCPGrsl > 1)*  \n  \n")

        #update results_df as we go along
        #results_df.update(ov_df['SDLOCPGrsl'])

        activity=f'resetting index on coll1_df'
        coll1_df.reset_index(inplace=True)
        coll1_shares = coll1_df['ShareNumber'].to_list()        

        coll2_df = combined_results[combined_results['_2StPr.Con_a3']  >= 50]
        #update results_df as we go along
        #results_df.update(coll2_df['_2StPr.Con_a3'])

        report_f.write(f"**{len(coll2_df)}** shares (from combined results) pass the condition *(2StPr.Con_a3 >= 50)*  \n  \n")
        activity=f'resetting index on coll2_df'
        coll2_df.reset_index(inplace=True,drop=True)
        coll2_shares = coll2_df['ShareNumber'].to_list()        
        # gather collection 1 and collection 2 in a set union
        coll_union_12 = set(coll1_shares).union(coll2_shares)

        # gather some more
        mask1 = ov_df['SDLOCPGrsl'] > 1.000010
        mask2 = ov_df['DLOCup']>30
        coll3_df =   ov_df[mask1 | mask2]
        #update results_df as we go along
        #results_df.update(coll3_df['DLOCup'])

        report_f.write(f"**{len(coll3_df)}** shares pass the condition *(SDLOCPGrsl > 1.000010) OR (DLOCup > 30)*  \n  \n")
        activity=f'resetting index on coll3_df'
        coll3_df.reset_index(inplace=True)
        coll3_shares = coll3_df['ShareNumber'].to_list()        
        # we already have collection 2 so we can re-use it
        coll_union_32 = set(coll3_shares).union(coll2_shares)

        # gather all the sub collections into a single list of shares
        final_shares = set(coll0_shares).intersection(coll1_shares).intersection(coll2_shares).intersection(coll3_shares)

        activity=f'resetting index on ov_df'
        ov_df.reset_index(inplace=True)
        final_ov_df = ov_df[ov_df['ShareNumber'].isin(final_shares)]

        chosens_zip = zip(final_ov_df['ShareNumber'], final_ov_df['ShareName'])
        g.CONFIG_RUNTIME['_3nH_list']  = list(chosens_zip)
        save_runtime_config()

        #spin off a sharelist as well - this will be in use immediately after 
        calc_helpers.create_results_3nH_sharelist()
        logging.info(f"'results_3nH' sharelist with {len(final_ov_df)} qualifying shares now available ...")    

        # write this list of chosen shares to the audit report also
        report_f.write(f"3nH chosen list ({len(g.CONFIG_RUNTIME['_3nH_list'])}) :  \n")
        for share_pair in g.CONFIG_RUNTIME['_3nH_list']:
            report_f.write(f'**{share_pair[0]}** {share_pair[1]}   \n') # number name

        # Save an Ov
        calc_helpers.ov_dataframe_to_store(final_ov_df,g.HDFSTORE_OV_KEY.format('results_3nH.shl',2), 2, 'results_3nH')

        # NOTE here we save an updated results dataframe for viewing on page 3nH
        calc_helpers._3nH_results_dataframe_to_store(results_df,'Default')
        #print(results_df.head())

        # report_f.write(f'Member shares are in the **Overview** for results 3nH  \n  \n')        
        # NOTE later
        # report_f = open(g.REPORTS_PATH + "\\_2StVols_results_report.txt", "w", encoding="utf-8")
        # spin off an excel spreadsheet for quick audit reference
        xslx_name_fq = f'{g.OUT_PATH}\\_3nH_results.xlsx'
        final_ov_df.to_excel(xslx_name_fq)

    except KeyError as ke:
        logging.error(f'Key Error {ke}, activity: {activity}')
    except Exception as exc:
        logging.error(f'Exception {exc}, activity: {activity}')

    finally:
        report_f.close()

    return dependencies

def prepare_combined_1_2_results(sharelist :str) ->pd.DataFrame:
    ''' combine the individual results dataframes into one and save to datastore '''

    _1St_df = get_df_from_store(g._1ST_RESULTS_STORE_FQ, g.HDFSTORE_1ST_RESULTS_KEY.format(sharelist))
    _1St_df.reset_index(inplace=True) # convert ShareNumber to a column for the merge joins we do below

    _2StPr_df = get_df_from_store(g._2STPR_RESULTS_STORE_FQ, g.HDFSTORE_2STPR_RESULTS_KEY.format(sharelist))
    _2StPr_df.reset_index(inplace=True)

    _2StVols_df = get_df_from_store(g._2STVOLS_RESULTS_STORE_FQ, g.HDFSTORE_2STVOLS_RESULTS_KEY.format(sharelist))
    _2StVols_df.reset_index(inplace=True)

    # create a new combined df by combining the preceding dfs
    combined_1_2_results_df = pd.DataFrame()

    # in order to have unique meaningful column names, 
    # prefix source dataframe columns with a results indicator
    _1St_cols = []
    for col in _1St_df.columns:
        if col in ['ShareNumber','ShareName','Date']:
            _1St_cols.append(col)
        else:
            _1St_cols.append('_1St.' + col)

    _2StPr_cols = []
    for col in _2StPr_df.columns:
        if col in ['ShareNumber','ShareName','Date']:
            _2StPr_cols.append(col)
        else:
            _2StPr_cols.append('_2StPr.' + col)

    _2StVols_cols = []
    for col in _2StVols_df.columns:
        if col in ['ShareNumber','ShareName','Date']:
            _2StVols_cols.append(col)
        else:
            _2StVols_cols.append('_2StVols.' + col)

    # change source col names
    _1St_df.columns = _1St_cols
    _2StPr_df.columns = _2StPr_cols
    _2StVols_df.columns = _2StVols_cols

    # start with _1St
    combined_1_2_results_df = _1St_df.loc[:,:]
    # merge in _2StPr
    combined_1_2_results_df = combined_1_2_results_df.merge(_2StPr_df.loc[:,:], on=['ShareNumber']) #,'ShareName','Date'])
    # merge in _2StVols
    combined_1_2_results_df = combined_1_2_results_df.merge(_2StVols_df.loc[:,:], on=['ShareNumber']) #,'ShareName','Date'])

    #get rid of the extra columns the merge function added
    #rename to ensure ShareNumber, Name and Date are on the left hand side
    combined_1_2_results_df.drop(['ShareName_y','Date_y','ShareName','Date','_2StPr.Status', '_2StVols.Status', ],inplace=True, axis=1)
    combined_1_2_results_df.rename(columns={'ShareName_x': 'ShareName', 'Date_x': 'Date', '_1St.Status': 'Status'}, inplace=True)

    # let the ShareNumber be the index
    combined_1_2_results_df.set_index('ShareNumber', inplace=True, drop=False)

    # save it in its store for later reference ALWAYS as Default.shl
    calc_helpers._combined_1_2_results_dataframe_to_store(combined_1_2_results_df, 'Default.shl') # sharelist)
    # spin off an excel spreadsheet for quick audit reference
    xslx_name_fq = f'{g.OUT_PATH}\\_combined_1_2_results.xlsx'
    combined_1_2_results_df.to_excel(xslx_name_fq)

    return combined_1_2_results_df


def prepare_new_frt(ov_df,combined_df,_3jP_df,_3V2d_df,_3nH_df):
    ''' combine default ov with all results tables (selected columns only) '''

    # NOTE we are going to only merge the 3jP, V2d and 3nH dataframes
    all_df=pd.DataFrame()

    #ov_df and combined_df together already have unique column names
    # lets also grab _3jP, _3V2d and _3nH additional columns
    _3jP_cols = ['3. StjP1', 'DjP']
    _3V2d_cols = ['RbSDV.D-7÷RbSDV.D-4']
    _3nH_cols = []

    # start with the ov
    all_df = ov_df.copy()
    logging.info(f"starting with daily ov, {len(ov_df)} shares...")

    # update from 3 stage dataframes
    all_df.update(_3jP_df)
    all_df.update(_3V2d_df)
    all_df.update(_3nH_df)


    # # merge in combined_df
    # #print(f'num ov cols={len(ov_df.columns)}')
    # #print(f'num combined_df cols={len(combined_df.columns)}')
    # all_df = all_df.merge(combined_df, on=['ShareNumber']) #, on=['ShareNumber']) #,'ShareName','Date'])
    # #print(f'ov merged with combined_df columns={all_df.columns}')

    # merge in particular _3jP_df columns
    if len(_3jP_df) > 0:
        logging.info(f"merging 3jP {len(_3jP_df)} shares...")
        try:
            all_df = all_df.merge(_3jP_df.loc[:,_3jP_cols], on=['ShareNumber']) #,'ShareName','Date'])
        except KeyError:
            pass # possibility that the _3jP_cols may not be present if no shares were selected
    else:
        logging.warn(f'3jP list has zero shares')
    
    # merge in particular _3V2d_df columns
    if len(_3V2d_df) > 0:
        logging.info(f"merging V2d {len(_3V2d_df)} shares...")
        try:        
            all_df = all_df.merge(_3V2d_df.loc[:,_3V2d_cols], on=['ShareNumber']) #,'ShareName','Date'])
        except KeyError:
            pass # possibility that the _3V2d_cols may not be present if no shares were selected
    else:
        logging.warn(f'V2d list has zero shares')


    # now from each minutely ov update CV1 in the frt 
    minutely_ov_df = load_overview_df('results_3jP', 1)      
    all_df.update(minutely_ov_df['CV1'])

    minutely_ov_df = load_overview_df('results_V2d', 1)      
    all_df.update(minutely_ov_df['CV1'])

    minutely_ov_df = load_overview_df('results_3nH', 1)      
    all_df.update(minutely_ov_df['CV1'])

    # rename those columns the merge function renamed
    all_df.rename(columns={'ShareName_x': 'ShareName', 'Date_x': 'Date', 'Status_x': 'Status'}, inplace=True)
    # let the ShareNumber be the index NOTE ShareNumber is already the index
    #all_df.set_index('ShareNumber', inplace=True, drop=False)
    # #print(all_df.index)

    # add required columns if necessary
    for col in frt_columns.FRT_COLUMNS:
        if not col in all_df.columns:
            all_df[col] = ''

    #these columns need to be strings
    #all_df = all_df.astype({'3jP': int,'V2d': int,'3nH': int})

    # delete rows not in the Stage 3 lists
    _3jPs = config_shares_list_2_names_or_numbers(g.CONFIG_RUNTIME['_3jP_list'],numbers_wanted=True)
    _V2ds = config_shares_list_2_names_or_numbers(g.CONFIG_RUNTIME['_V2d_list'],numbers_wanted=True)
    _3nHs = config_shares_list_2_names_or_numbers(g.CONFIG_RUNTIME['_3nH_list'],numbers_wanted=True)

    scores = {}

    discards=[]
    for share_num in all_df.index:
        # build dict of share scores
        if share_num not in scores:
            scores[share_num]=0
        # gather up those shares we wont be wanting
        if share_num not in _3jPs and share_num not in _V2ds and share_num not in _3nHs:
            discards.append(share_num)
        else:
            # count number of appearances a share makes
            if share_num in _3jPs:
                scores[share_num] += 1
                all_df.at[share_num,'3jP'] = g.PASS
            if share_num in _V2ds:
                scores[share_num] += 1
                all_df.at[share_num,'V2d'] = g.PASS
            if share_num in _3nHs:
                scores[share_num] += 1
                all_df.at[share_num,'3nH'] = g.PASS

    # drop all the unwanted shares
    all_df = all_df.drop(index=discards)

    # drop unwanted columns
    unwanted_cols=[col for col in all_df.columns if col not in frt_columns.FRT_COLUMNS]
    all_df.drop(unwanted_cols,'columns',inplace=True)

    # tote up Score
    for share_num in all_df.index:
        all_df.loc[share_num,'Score'] = scores[share_num]

    # rename some columns to satisfy '3 Final Result Table FRT 210831' document
    #all_df = all_df.rename({'DCP': 'PriceOfDOLE',}, axis=1)

    # timestamp the shares before saving
    all_df['DateOfLastEntry'] = datetime.now()


    logging.info(f"{len(all_df)} shares in new FRT. {len(discards)} shares discarded")



    # save it in its store for later reference ALWAYS as Default.shl
    # NO, we return it below for use as an overlay on top of any existing FRT
    # calc_helpers.frt_results_dataframe_to_store(all_df, 'Default.shl') # sharelist)
    
    # spin off an excel spreadsheet for quick audit reference
    xslx_name_fq = f'{g.OUT_PATH}\\frt_results.xlsx'
    all_df.to_excel(xslx_name_fq)

    return all_df

def update_cur_frt(cur_frt_df, new_frt_df):
    ''' takes current shares frt df and overlays latest (newly computed) frt and saves 
    '''
    from datetime import date, timedelta

    # timestamp the shares before saving
    new_frt_df['DateOfLastEntry'] = datetime.now()
    # update current frt from the new.
    # this leaves shares AS IS in the current one which are not present in the new
    cur_frt_df.update(new_frt_df)

    # shares should stay there until the "Date of last entry" is older than 60 days (or 40 trading days).
    sixty_days_ago = datetime.now() - timedelta(60)
    logging.info(f"dropping entries compiled earlier than {sixty_days_ago} ...")
    cur_frt_df.drop(cur_frt_df[cur_frt_df['DateOfLastEntry'] < sixty_days_ago].index, inplace=True)

    calc_helpers.frt_results_dataframe_to_store(cur_frt_df, 'Default.shl') # sharelist)


def produce_frt(overwrite :bool):
    ''' composes or updates the Final Results dataframe 
        called from command line or via go-gui
    '''

    logging.info(f"Performing compile_final_results(overwrites={overwrite})")    
    activity=f'produce_frt'
    dependencies = {}
    report_f = open(g.REPORTS_PATH + "\\_FRT_results_report.txt", "w", encoding="utf-8")

    try:
        # we start with latest stage 2 overviews on Default sharelist 
        def_key = 'Default'
        ov_df = load_overview_df(def_key, 2)      

        # and combine in the (already combined combined_1_2_results + 3jP + 3V2d + 3nH dataframes)
        # first load the dataframes
        logging.info(f'loading combined_df...')
        combined_df = get_df_from_store(g._COMBINED_1_2_RESULTS_STORE_FQ, g.HDFSTORE_COMBINED_1_2_RESULTS_KEY.format(def_key))
        #we wont be needing this column, since we rely on the index as being the ShareNumber
        if 'ShareNumber' in combined_df.columns:
            del(combined_df['ShareNumber'])

        logging.info(f'loading 3jp_df...')
        _3jP_df = get_df_from_store(g._3JP_RESULTS_PART2_STORE_FQ, g.HDFSTORE_3JP_RESULTS_PART2_KEY.format(def_key))
        #we wont be needing this column, since we rely on the index as being the ShareNumber
        if 'ShareNumber' in _3jP_df.columns:
            del(_3jP_df['ShareNumber'])

        logging.info(f'loading 3V2d_df...')
        _3V2d_df = get_df_from_store(g._3V2D_RESULTS_STORE_FQ, g.HDFSTORE_3V2D_RESULTS_KEY.format(def_key))
        #we wont be needing this column, since we rely on the index as being the ShareNumber
        if 'ShareNumber' in _3V2d_df.columns:
            del(_3V2d_df['ShareNumber'])

        logging.info(f'loading 3nH_df...')
        _3nH_df = get_df_from_store(g._3NH_RESULTS_STORE_FQ, g.HDFSTORE_3NH_RESULTS_KEY.format(def_key))
        #we wont be needing this column, since we rely on the index as being the ShareNumber
        if 'ShareNumber' in _3nH_df.columns:
            del(_3nH_df['ShareNumber'])

        # do the combining to produce an FRT dataframe which we use to overlay any existing one
        activity='produce_frt:prepare_new_frt'
        new_frt_df =prepare_new_frt(ov_df,combined_df,_3jP_df,_3V2d_df,_3nH_df)
        report_f.write(f"FRT table has {len(new_frt_df.columns)} columns. Choose columns using the 'Toggle Columns' button")

        # TODO
        results_df = None
        if overwrite or not exists(g._FRT_RESULTS_STORE_FQ):
            # first one, save it in its store
            logging.info(f"saving (first) FRT...")
            calc_helpers.frt_results_dataframe_to_store(new_frt_df, 'Default.shl') # sharelist)
        elif exists(g._FRT_RESULTS_STORE_FQ):
            # we must create for the first time or update an existing results file
            logging.info(f"retrieving existing FRT...")
            cur_frt_df = get_df_from_store(g._FRT_RESULTS_STORE_FQ, g.HDFSTORE_FRT_RESULTS_KEY.format('Default'))

            # NOTE this is where it happens
            logging.info(f"updating FRT...")
            activity='produce_frt:update_cur_ft'
            final_frt_df = update_cur_frt(cur_frt_df, new_frt_df)

    except KeyError as ke:
        logging.error(f'Key Error {ke}, activity: {activity}')
    except Exception as exc:
        logging.error(f'Exception {exc}, activity: {activity}')

    finally:
        report_f.close()

    return

def generate_random_sharelist(size :int):
    ''' from the master sharelist, select size shares into a sharelist named "random_{size}.shl" '''

    bouquet = []
    with open(g.MASTER_SHARE_DICT_FQ, "r") as f:
        for line in f:
            # ensure we only select from ETR bourse
            if '.ETR' in line:
                #AAP IMPLANTATE AG O.N.         ,A3H210.FFM,13.11.2020,26.03.2021
                bouquet.append(line[0:31] + line[32:38] + '.ETR')

    random_share_indexes = random.sample(range(len(bouquet)), size)

    random_shl_fq = g.SHARELISTS_FOLDER_FQ + '\\' + f'random_{size}.shl'
    with open(random_shl_fq,'w', encoding='utf8') as shlf:
        #SHARELIST_HEADER = 'share_name                     number'
        shlf.write(f'{g.SHARELIST_HEADER}\n')
        for index in random_share_indexes:
            shlf.write(f'{bouquet[index]}\n') 


def delete_process3_dependent_results(from_stage :str):

    if from_stage == '1':

        # these lists must be recreated from scratch by the results commands
        g.CONFIG_RUNTIME['_3jP_list'] = []
        g.CONFIG_RUNTIME['_V2d_list'] = []
        g.CONFIG_RUNTIME['_3nH_list'] = []
        save_runtime_config()

        # also get rid of corresponding actual sharelists
        _3jP_sharelist_fq = g.SHARELISTS_FOLDER_FQ + "\\results_3jP.shl"
        _V2d_sharelist_fq = g.SHARELISTS_FOLDER_FQ + "\\results_V2d.shl"
        _3nH_sharelist_fq = g.SHARELISTS_FOLDER_FQ + "\\results_3nH.shl"    
        if exists(_3jP_sharelist_fq):
            os.remove(_3jP_sharelist_fq)
        if exists(_V2d_sharelist_fq):
            os.remove(_V2d_sharelist_fq)
        if exists(_3nH_sharelist_fq):
            os.remove(_3nH_sharelist_fq)
        logging.info('dependent sharelists 3jP, V2d, and 3nH deleted...')

        if exists(g._1ST_RESULTS_STORE_FQ):
            os.remove(g._1ST_RESULTS_STORE_FQ)
            logging.info(f'result store {g._1ST_RESULTS_STORE_FQ} deleted')
        report_fq = g.REPORTS_PATH + "\\_1St_results_report.txt"
        if exists(report_fq):
            os.remove(report_fq)

    if from_stage in ['1', '2StPr']:
        if exists(g._2STPR_RESULTS_STORE_FQ):
            os.remove(g._2STPR_RESULTS_STORE_FQ)
            logging.info(f'result store {g._2STPR_RESULTS_STORE_FQ} deleted')
        report_fq = g.REPORTS_PATH + "\\_2StPr_results_report.txt"
        if exists(report_fq):
            os.remove(report_fq)

    if from_stage in ['1', '2StPr','2StVols']:
        if exists(g._2STVOLS_RESULTS_STORE_FQ):
            os.remove(g._2STVOLS_RESULTS_STORE_FQ)
            logging.info(f'result store {g._2STVOLS_RESULTS_STORE_FQ} deleted')
        report_fq = g.REPORTS_PATH + "\\_2StVols_results_report.txt"
        if exists(report_fq):
            os.remove(report_fq)

    if from_stage in ['1', '2StPr','2StVols','Comb']:
        if exists(g._COMBINED_1_2_RESULTS_STORE_FQ):
            os.remove(g._COMBINED_1_2_RESULTS_STORE_FQ)
            logging.info(f'result store {g._COMBINED_1_2_RESULTS_STORE_FQ} deleted')

    if from_stage in ['1', '2StPr','2StVols','Comb','3jP']:
        if exists(g._COMBINED_1_2_RESULTS_STORE_FQ):
            os.remove(g._COMBINED_1_2_RESULTS_STORE_FQ)
            logging.info(f'result store {g._COMBINED_1_2_RESULTS_STORE_FQ} deleted')
        if exists(g._3JP_RESULTS_PART1_STORE_FQ):
            os.remove(g._3JP_RESULTS_PART1_STORE_FQ)
            logging.info(f'result store {g._3JP_RESULTS_PART1_STORE_FQ} deleted')
        if exists(g._3JP_RESULTS_PART2_STORE_FQ):
            os.remove(g._3JP_RESULTS_PART2_STORE_FQ)
            logging.info(f'result store {g._3JP_RESULTS_PART2_STORE_FQ} deleted')
        report_fq = g.REPORTS_PATH + "\\_3jP_part1_results_report.txt"
        if exists(report_fq):
            os.remove(report_fq)

    if from_stage in ['1', '2StPr','2StVols','Comb','3jP','3V2d']:
        if exists(g._3V2D_RESULTS_STORE_FQ):
            os.remove(g._3V2D_RESULTS_STORE_FQ)
            logging.info(f'result store {g._3V2D_RESULTS_STORE_FQ} deleted')
        report_fq = g.REPORTS_PATH + "\\_3V2d_results_report.txt"
        if exists(report_fq):
            os.remove(report_fq)

    if from_stage in ['1', '2StPr','2StVols','Comb','3jP','3V2d','3nH']:
        if exists(g._3NH_RESULTS_STORE_FQ):
            os.remove(g._3NH_RESULTS_STORE_FQ)
            logging.info(f'result store {g._3NH_RESULTS_STORE_FQ} deleted')
        report_fq = g.REPORTS_PATH + "\\_3nH_results_report.txt"
        if exists(report_fq):
            os.remove(report_fq)


def provide_datepicker(target :str):

    sd = g.CONFIG_RUNTIME['setting_chart_start']
    ed = g.CONFIG_RUNTIME['setting_chart_end']

    start_days_back = g.CONFIG_RUNTIME['default_days_back']
    if target=='min_date_allowed':    
        #mda = get_date_for_busdays_back(start_days_back).replace('_','-')
        mda = g.CONFIG_RUNTIME['last_calculations_start_date'].replace('_','-')
        #print(f'mda={mda}')
        return mda
    elif target=='max_date_allowed':
        return get_date_for_busdays_back(0).replace('_','-')
    elif target=='start_date':
        if sd is not None:
            return sd
        else:
            return get_date_for_busdays_back(7).replace('_','-')
    elif target=='end_date':
        if ed is not None:
            return ed
        else:
            return get_date_for_busdays_back(1).replace('_','-')
    else:
        print('invalid date target for datepicker')
        return get_date_for_busdays_back(0).replace('_','-')

def is_st3_selected_share(shlist_name, share_num):
    ''' looks at sharelist and share number and decides whether the share is one of the 'selected' ones '''

    if shlist_name == 'results_3jP.shl' and sharenum_in_spinoff_list(share_num,'_3jP_list'):
        return True
    elif shlist_name == 'results_V2d.shl' and sharenum_in_spinoff_list(share_num,'_V2d_list'):
        return True
    elif shlist_name == 'results_3nH.shl' and sharenum_in_spinoff_list(share_num,'_3nH_list'):
        return True

    return False