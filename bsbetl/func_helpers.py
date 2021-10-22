import glob
import json
import logging
import os.path
import re
from datetime import datetime
from os import mkdir
from os.path import exists, isfile, join

import pandas as pd

from bsbetl import calc_helpers, g, helpers


def save_runtime_config():
    ''' call this after runtime values need to be persisted '''

    with open(g.CONFIG_RUNTIME_FQ, 'w') as f:
        json.dump(g.CONFIG_RUNTIME, f, indent=4)


def save_and_reload_page_size(page_size_setting :str, page_size_wanted :int) ->int:
    ''' save a page size setting to runtime config '''

    print(f"get_save_page_size(page_size_setting='{page_size_setting}',page_size_wanted={page_size_wanted}) ...")

    # allow user to decide his own page size. 0 means sensible defaults
    if isinstance(page_size_wanted, int) and page_size_wanted > 0:
        # save the new page size
        g.CONFIG_RUNTIME[page_size_setting] = page_size_wanted
        save_runtime_config()

    # reload from config
    page_size = g.CONFIG_RUNTIME[page_size_setting] 

    return page_size

# def get_last_trade_timestamp(hint_filename_fq) -> str:
#     """ extracts the 'Last trade' timestamp from a hint file """

#     if not os.path.exists(hint_filename_fq):
#         return ''

#     f = open(hint_filename_fq, 'r')
#     # read contents eg '1581 trades written. Last trade: 2020-09-21 17:36:25,9.15,0,2403'
#     hint_contents = f.read()
#     f.close()

#     # this should return eg '2020-09-21 17:36:25' from the above example
#     match_obj = re.search(
#         r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", hint_contents)

#     if match_obj is not None:
#         return match_obj.group()
#     else:
#         return ""


def tail(file, n=1, bs=1024):
    """ Read Last n Lines of file

    credit:
    https://www.roytuts.com/read-last-n-lines-from-file-using-python/
    https://github.com/roytuts/python/blob/master/read-lines-from-last/last_lines_file.py
    """

    f = open(file)
    f.seek(0, 2)
    l = 1-f.read(1).count('\n')
    B = f.tell()
    while n >= l and B > 0:
        block = min(bs, B)
        B -= block
        f.seek(B, 0)
        l += f.read(block).count('\n')
    f.seek(B, 0)
    l = min(l, n)
    lines = f.readlines()[-l:]
    f.close()
    return lines


def get_first_trade_timestamp(trades_csv_fq: str) -> str:

    if not os.path.exists(trades_csv_fq):
        return ''

    with open(trades_csv_fq, 'r') as f:
        first_line = f.readline()
        if first_line.startswith('date_time,'):
            first_line = f.readline()

    match_obj = re.search(
        r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", first_line)

    if match_obj is not None:
        return match_obj.group()
    else:
        return ""


def get_last_trades_timestamp(trades_csv_fq: str) -> str:

    if not os.path.exists(trades_csv_fq):
        return ''

    last_line = ''
    end_bit = tail(trades_csv_fq, n=1)
    if len(end_bit) > 0:
        last_line = end_bit[0]
    else:
        return ''
    # last line could be '' or
    # date_time,price,volume,vol_cum
    # or
    # 2020-01-10 14:49:50,13,160,160
    match_obj = re.search(
        r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", last_line)

    if match_obj is not None:
        return match_obj.group()
    else:
        return ""


def check_monotonicity(trades_csv_fq: str) -> tuple:
    ''' returns line number where monotonicity fails, else 0 if all good '''

    monotonic = True
    line_num = 0
    last_stamp = '0000-00-00 00:00:00'

    logging.info(f'monotonicity checking {trades_csv_fq} ...')

    with open(trades_csv_fq, 'r') as f:
        for line in f:
            line_num = line_num+1
            if len(line) > 0 and (not line.startswith('date_time')):
                # make sure its a valid timestamp
                match_obj = re.search(
                    r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", line)
                # test
                if (match_obj is not None) and (match_obj.group() < last_stamp):
                    # break in monotonicity
                    monotonic = False
                    break
                elif match_obj is not None:
                    last_stamp = match_obj.group()

    if monotonic:
        return (0, '')
    else:
        return (line_num, last_stamp)


def customize_plot_grid(ax):

    # Don't allow the axis to be on top of your data
    ax.set_axisbelow(True)
    # Turn on the minor TICKS, which are required for the minor GRID
    ax.minorticks_on()
    # Customize the major grid
    ax.grid(which='major', linestyle='-', linewidth='0.5', color='red')
    # Customize the minor grid
    ax.grid(which='minor', linestyle=':', linewidth='0.5', color='black')
    return


def prepare_csv_outfile_paths(sharelist_tuples: list, csv_by_share_path: str) -> tuple:
    """ Ensure By_Day folders exist for each share

        Also return a tuple consisting of
        (list of out_sharefile_paths, share_num keyed dictionary of last written timestamp)
    """

    out_sharefile_paths = []
    out_sharefile_last_tstamp = {}
    for share_name, share_num in sharelist_tuples:
        share_num_without_bourse = share_num[0:-4] # used as a key below
        if calc_helpers.check_share_num(share_num):
            # (csv_by_share_path assumed to exist)
            single_share_directory = f'{csv_by_share_path}\{share_num}'
            if not exists(single_share_directory):
                mkdir(single_share_directory)
                logging.warn(
                    f'folder {single_share_directory} had to be created')

            # the name of the CSV file we'll be creating or appending to
            out_sharefile_fq_name = f'{csv_by_share_path}\{share_num}\{share_num}.CSV'
            # gather list of output filenames for use below
            out_sharefile_paths.append(out_sharefile_fq_name)
            # also obtain timestamp of the last record currently in the outfile
            # index it without the bourse suffix
            out_sharefile_last_tstamp[share_num_without_bourse] = get_last_trades_timestamp(out_sharefile_fq_name)
        else:
            logging.warn(
                f'share_number {share_num} has incorrect format. missing or incorrect bourse suffix?')
    return (out_sharefile_paths, out_sharefile_last_tstamp)


def prepare_src_csv_files_list(csv_by_day_path: str, start_date: str) -> list:
    # prepare src_csv_files_list
    init_src_csv_files_list = [f for f in os.listdir(csv_by_day_path) if f.endswith(
        'TXT.CSV') and isfile(join(csv_by_day_path, f))]

    # discard src_csv files whose date predates start_date
    src_csv_files_list = [
        f for f in init_src_csv_files_list if f >= f'{start_date}.TXT.CSV']

    return src_csv_files_list


def build_share2handleindex_dict(file_handles: list) -> dict:
    """ given list of open file handles, create a dictionary relating share_num part to index within file_handles list"""

    dict_out = {}
    for i, fh in enumerate(file_handles):
        name = fh.name  # ='C:\BsbEtl\OUT\By_Share\120470.ETR\120470.ETR.CSV'
        share_part = name[-14:-8]  # 120470 # NOTE bourse part .ETR is stripped as the key
        dict_out[share_part] = i

    return dict_out


def write_share_hint_file(ctx, share_name: str, share_num: str, start_date: str):
    """ writes a text file to the share folder whose name indicates the full name of the share and whose content tels the user the trading range """

    csv_by_share_path = helpers.etl_path(ctx, g.CSV_BY_SHARE_FOLDER)
    out_sharefile_fq_name = f'{csv_by_share_path}\{share_num}\{share_num}.CSV'

    # peek into it (if existing) and retrieve the datetime stamp of the first trade
    first_trade_time_stamp = get_first_trade_timestamp(
        out_sharefile_fq_name)
    # this stamp needs to be cleaned up since it will form part of the info filename
    # replace non word chars with underscores
    first_trade_time_stamp = re.sub(r"[\W]", "_", first_trade_time_stamp)

    #last_trade_time_stamp = get_last_trade_timestamp(out_sharefile_fq_name)  # this should return eg 2020-09-21 17:36:25 (or '')

    single_share_directory = f'{csv_by_share_path}\{share_num}'

    # select the appropriate slug
    hint_slug = start_date if first_trade_time_stamp == '' else first_trade_time_stamp

    # put down a hint file whose name informs user of the start date of trades
    scrubbed_share_name = re.sub(r"[\W]", "_", share_name)

    hint_filename_fq = single_share_directory + \
        f"\\_{hint_slug}_{scrubbed_share_name}.info"

    # remove former .info file
    for fl in glob.glob(f'{single_share_directory}\\*.info'):
        os.remove(fl)

    # write the hint file
    open(hint_filename_fq, 'a').close()


def update_share_hint_files(ctx, sharelist_tuples: list, start_date: str):
    """ loop thru all share folders depositing updated share hint files  """

    for share_name, share_number in sharelist_tuples:
        write_share_hint_file(ctx, share_name, share_number, start_date)


def get_last_stored_df(share_num: str, stage: int = 1) -> pd.DataFrame:
    """ extract share dataframe from stage appropriate HDFStore and return it """

    data_store = pd.HDFStore(g.SHARE_STORE_FQ.format(stage))
    try:
        assert len(share_num) == 10, f'share_num {share_num} malformed'
        share_key = share_num[-3:] + '_' + share_num[0:-4]
        # extract dataframe
        df = data_store[share_key]
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

def add_df_columns(dest_df :pd.DataFrame, src_df :pd.DataFrame, columns_to_add :list):

    for col in columns_to_add:
        if not col in dest_df.columns:
            dest_df.loc[:,col] = src_df[col]

def load_overview_df(sharelist,stage):
    ''' load and return an overview '''

    try:
        ov_fn = g.OVERVIEW_STORE_FQ.format(stage)
        ov_key=g.HDFSTORE_OV_KEY.format(sharelist,stage)
        ov_data_store = pd.HDFStore(ov_fn)

        logging.info(f"loading overview {ov_fn} under key {ov_key}")
        ov_df = ov_data_store[ov_key]

        if not ov_df.index.is_unique:
            ov_df = ov_df.loc[~ov_df.index.duplicated(), :]

        return ov_df
    
    except KeyError as exc:
        logging.error(f"load_overview(sharelist={sharelist}, stage={stage}) KeyError {exc}")
        return pd.DataFrame()
    finally:
        ov_data_store.close()


def load_results_df(results_fn, results_key) ->pd.DataFrame:
    ''' load and return a previously saved results dataframe '''
    try:
        # get res df from its store
        results_data_store = pd.HDFStore(results_fn)
        # extract dataframe, (replacing the above created, empty one)
        logging.info(f"loading results {results_fn} under key {results_key}")
        results_df = results_data_store[results_key]
        return results_df

    except KeyError as ke:
        # probably results dataframe not found ensure an empty one is created
        results_df = pd.DataFrame()
        logging.error(f'Key Error {ke} (results datastore) - empty one returned')                
    finally:
        results_data_store.close()


def build_results_starter_df(reference_ov :pd.DataFrame) ->pd.DataFrame:

    ''' build an empty 'results' dataframe with rows filled with 
        ShareName and Data columns taken from passed in overview 
    '''
    results_df = pd.DataFrame()
    results_df.allows_duplicate_labels = False

    append_df = reference_ov[['Status','ShareName','Date']]
    results_df = pd.concat([results_df,append_df])
    return results_df


''' conditions evaluations: '''
def report_ov_shares_passing(f,results):
    f.write(f"{len(results)} Ov shares pass this condition  \n")

def report_ov_shares_simply_displayed(f,results):
    f.write(f"{len(results)} Ov shares simply displayed  \n")

def report_results_so_far(f,results):
    f.write(f"Results: {len(results)} shares gathered so far  \n  \n")

def report_all_fail(f, con_name :str = ''):
     ''' helper '''
     f.write(f"0 shares pass {con_name}  \n") 


def config_shares_list_2_names_or_numbers(config_list, numbers_wanted :bool) ->list:
    ''' extract list share numbers (or names) from passed in config list like eg g.CONFIG_RUNTIME['_3Jp_list'] 
    '''
    
    retlist=[]
    if numbers_wanted:
        retlist = [list_pair[0] for list_pair in config_list]
    else:
        retlist = [list_pair[1] for list_pair in config_list]

    return retlist
    


def is_initial_process_3_stage() ->bool:

    return len(g.CONFIG_RUNTIME['_3jP_list']) == 0 and \
           len(g.CONFIG_RUNTIME['_V2d_list']) == 0 and \
           len(g.CONFIG_RUNTIME['_3nH_list']) == 0
           