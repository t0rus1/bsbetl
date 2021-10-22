from bsbetl.helpers import append_nodata_log, silentremove
import datetime
import inspect
import logging
import os
from datetime import date, datetime, timedelta
from os.path import exists

import click
import pandas as pd

from bsbetl import g
# alltable calculation parameters
from bsbetl.alltable_calcs.at_run_all import run_all_alltable_calcs
# alltable calculations
from bsbetl.calc_helpers import (df_from_csv, daterange,
                                 get_sharelist_list, get_start_end_date,
                                 initialize_overview, ov_dataframe_to_store,
                                 share_dataframe_to_store)
from bsbetl.func_helpers import get_last_stored_df, is_initial_process_3_stage
# overview calculations
from bsbetl.ov_calcs.ov_Laziness import ov_Laziness
# overview calculation parameters
from bsbetl.ov_calcs.ov_params import ov_calc_params
from bsbetl.ov_calcs.ov_run_all import run_all_final_ov_calcs

# ...
#####################################################


def all_calcs(df, single_share_path: str, share_num: str, stage: int, only_share: str, top_up: bool, topup_date: str, shlist_name :str):
    """ perform all share calculations sequentially on dataframe then update its Overview entry
        TODO: improve speed.
        datetimes, price and volume assumed already in the dataframe
    """

    func_name = inspect.stack()[0][3]
    shim = f'Topping up from {topup_date}' if top_up else ''
    logging.info(f'{func_name}...share_num {share_num}...{shim}')

    # determine start and end dates
    # 'date' and not 'datetime' types are returned
    start_date, end_date = get_start_end_date(df)
    if top_up:
        # bring the start_date forward
        start_date = datetime.strptime(topup_date, '%Y_%m_%d').date()

    # prepare a list of individual dates assumed in the df
    # NOTE this make no assumption whether the sampling in the df is daily or 5Min or 1Min
    # we use the term adj to indicate 'adjusted dates' ie reduced (if topping up) to include only the topup dates
    adj_dates_in_df = [d for d in daterange(start_date, end_date + timedelta(days=1))]

    adj_weekdates_in_df = [d for d in adj_dates_in_df if d.weekday() < 5]

    # NOTE although this function computes all the all_table calcs,
    # it ALSO updates the overview during the calculating, where required

    # Open a trace file (appending) to which we can write a trace of calculations performed/skipped
    # This share assoc at_trace file is deleted prior to each stage 1
    at_tracef = open(single_share_path + f"\\at_trace_{share_num}.txt", "a", encoding="utf-8")
    run_all_alltable_calcs(df, share_num, adj_weekdates_in_df, top_up, stage, shlist_name, at_tracef, only_share)
    at_tracef.close()

    # complete Overview calculations for the share's single row in the Ov
    run_all_final_ov_calcs(df, single_share_path, share_num, stage)

    # save df in HDFStore
    share_dataframe_to_store(df, share_num, stage)

    logging.info(f'End {func_name} {df.shape} (rows,cols).')

    return


def calc_alltable_from_csv(share_num: str, share_name: str, only_share: str, stage: int, start_date: str, end_date :str,  top_up: bool, shlist_name :str):
    """ perform all calculations from csv for a particular share and stage from first_date onwards and produce an alltable dataframe """

    func_name = inspect.stack()[0][3]
    print('\n')  # helps make progress bar stand out
    stage_explain = 'MINUTELY' if stage==1 else 'DAILY'
    logging.info(
        f'STAGE {stage_explain}: {func_name}...share_num {share_num} ({shlist_name}), start_date {start_date} {share_name} ')

    share_path = g.CSV_BY_SHARE_PATH
    # check folder exists for this share (share_path assumed to exist)
    single_share_path = f'{share_path}\{share_num}'
    if not exists(single_share_path):
        error_msg = f"{single_share_path} share folder not found. You need to have run 'process-2' command"
        logging.error(error_msg)
        return

    # convert share csv to  bus hours dataframe with data starting at start_date
    # note: this is called the 'Load' stage ... see g.CALCS_STAGES
    # if stage == 1:
    #     sampling = 'B'
    #     sampling_desc = 'Business Day'
    # else:
    #     sampling = '1Min'
    #     sampling_desc = sampling

    # this df is properly initialized later
    df_last_stored = pd.DataFrame()

    df_joined = pd.DataFrame()
    topup_dt = None

    if top_up:
        # we need to determine start_date based on date of last row in the stored dataframe
        # param start_date ought to be empty
        df_last_stored = get_last_stored_df(share_num, stage)
        if isinstance(df_last_stored, pd.DataFrame) and df_last_stored.shape[0] > 0:
            last_dt = df_last_stored.index[-1]
            # we need a NEW start_date in the form YYYY_MM_DD
            # add 1 day to prevent having to recalc the last day again
            topup_dt = last_dt + timedelta(days=1)
            start_date = topup_dt.strftime('%Y_%m_%d')
        else:
            logging.warn(
                f"couldn't topup for share {share_num} due to there being either NO dataframe in the store for it, or some other error")
            return

    # ***************************************************************
    # NOTE
    # If we're topping up:
    # ~~~~~~~~~~~~~~~~~~~~
    # start_date will have been bumped forward, and so df_newdata returned
    # will be only a tail-piece dataframe and will be appended to df_last_stored.
    # If not topping up:
    # ~~~~~~~~~~~~~~~~~~
    # df_newdata will be the only and entire dataframe from the passed in start_date
    # with df_last_stored being ignored
    # ****************************************************************

    if is_initial_process_3_stage(): 
        # process-3 run
        df_newdata = df_from_csv(share_path, share_num, '', start_date, end_date, stage)
        logging.info(f"loaded {stage_explain} At from .CSV file for share {share_num} ...")
    else:
        # one of the results- runs, so DO NOT INITIALIZE, use existing all-table
        logging.info(f"performing a 'results-' update...")
        df_newdata = get_last_stored_df(share_num,stage)
        logging.info(f"loaded last saved {stage_explain} At for share {share_num} ...")

    if top_up and ((df_newdata.shape[0] == 0) or (df_newdata.index[-1] < topup_dt)):
        # sanity check on what we're about to append
        logging.warn(f'No new data found to top up share {share_num}')
        return

    # if we're topping up the df_resampled returned above is merely a tail-piece of 1 (or a few) days data
    # in that case we need to append this df_resampled to the end of last_stored_df
    # before proceeding. Note that in this case the calculations below still start from start_date, but start_date is
    # somewhere near the end of the dataframe as opposed to the beginning of the dataframe, like when a full process-3 is performed

    # start with a new at_trace file (only at stage 1 - stage 2 trace messages get appended to this same file)
    at_trace_fq = single_share_path + f"\\at_trace_{share_num}.txt"
    if stage==1 and exists(at_trace_fq):
            os.remove(at_trace_fq)

    if top_up:
        if len(df_newdata) > 0:
            df_joined = df_last_stored.append(df_newdata)
            logging.info(
                f'{share_num} top-up of {df_newdata.shape[0]} rows, per stage {stage}')
            # HERE IS WHERE IT ALL HAPPENS - TOP UP
            all_calcs(
                df_joined, single_share_path, share_num, stage, only_share, top_up=True, topup_date=start_date, shlist_name=shlist_name)
        else:
            logging.info(f'Skipping top up for {share_num} - no new CSV data')
    else:
        # non top-up, full calc case
        if len(df_newdata) > 0:
            # overwrites the 'no data' initialization
            g.df_ov.at[share_num,'Status'] = ''
            logging.info(
                f'{share_num} full-calcs for {df_newdata.shape[0]} rows, per stage {stage}')
            # HERE IS WHERE IT ALL HAPPENS - NON TOP UP
            all_calcs(
                df_newdata, single_share_path, share_num, stage, only_share, top_up=False, topup_date=start_date, shlist_name=shlist_name)
        else:
            # affirms the 'no data' initialization
            g.df_ov.at[share_num,'Status'] = 'no data'
            warning = f'no CSV data could be found for {share_num} ({share_name}) for start_date {start_date} -> {end_date}'
            logging.warn(warning)
            append_nodata_log(warning)

    logging.info(f'End {func_name} execution.')
    logging.info('')

    return


def produce_alltables_from_CSVs(stages: list, shlist_name: str, start_date: str, end_date: str, only_share: str, top_up: bool):
    """ Computes stage calculations (fully or top-up) for every share in a sharelist.

        Stores resulting dataframe in stage level HDF store
        (unless only_share specifies one share only)
        Builds also an overview of the results in CSV_BY_SHARE_FOLDER
    """

    func_name = inspect.stack()[0][3]
    logging.info(f'Executing {func_name} ...')

    assert (start_date == '' and top_up) or (len(start_date) == 10 and (
        not top_up)), 'cannot pass a start_date if topping up | start_date missing'
    
    assert (end_date >= start_date), f'end_date {end_date} must be >= start_date {start_date}'

    #base_good = base_usable(start_date, top_up)
    shlist_name_fq = f'{g.CONTAINER_PATH}\{g.SHARELISTS_FOLDER}\{shlist_name}'

    # obtain a list of share_name, share_number tuples from the sharelist
    shlist_tuples = get_sharelist_list(shlist_name_fq)

    for stage in stages:
        # instantiate the global overview dataframe for the stage for populating during the calcs to follow
        # start these logs afresh
        silentremove(g.PROCESS3_WARNLOG_NAME_FQ)
        silentremove(g.CSVMAXSIZE_WARNLOG_NAME_FQ)

        g.df_ov = initialize_overview(shlist_tuples, stage, shlist_name)

        stage_desc = '1 (minutely)'
        if stage==2:
            stage_desc = '2 (daily)'

        if len(shlist_tuples) > 0:
            topup_shim = '-topup' if top_up else ''
            label_shim = f'({shlist_name}) Stage {stage_desc} calcs from {start_date} to {end_date}'
            with click.progressbar(shlist_tuples, label=f"'process-3{topup_shim}': {label_shim}") as bar:
                for share_name, share_number in bar:
                    # gen csv for this share, provided the share has name
                    if (share_name and only_share == '') or (share_number == only_share):
                        calc_alltable_from_csv(share_number, share_name,
                                               only_share, stage, start_date, end_date, top_up, shlist_name)
        else:
            logging.error(
                f"Share list file '{shlist_name_fq}' empty or not found")

        # spinoff overview dataframe as excel (regardless)
        ov_fn_fq = f'{g.CONTAINER_PATH}\{g.CSV_BY_SHARE_FOLDER}\\ov_{shlist_name}_{stage}.xlsx'
        g.df_ov.to_excel(ov_fn_fq)
        logging.info(f'ov_{shlist_name}_{stage}.xlsx saved')

        ov_dataframe_to_store(g.df_ov, f"{shlist_name}_{stage}", stage, shlist_name)

    logging.info(f'End {func_name} execution...')
