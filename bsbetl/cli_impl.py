import glob
import inspect
import logging
import os
from datetime import datetime

from bsbetl import functions, g, helpers, processing
from bsbetl.func_helpers import save_runtime_config

''' one for one implementation of cli commands - see cli.py '''

def impl_process_1(ctx, origination, keep: bool):

    logging.info(
        f'/ Command {inspect.stack()[0][3]} ...Parameters: keep_txt={keep}')
    startTime = datetime.now()

    ctx.obj['keep_txt'] = keep
    num2name = functions.gen_csv_byday(ctx, origination)

    logging.info(
        f"\ End Command {inspect.stack()[0][3]}. Duration: {datetime.now() - startTime}")

def grim_reap(hit_list):
    ''' '''

    deletion_error_msg = "Error while deleting file : "
    for filePath in hit_list:
        try:
            os.remove(filePath)
            print(f'{filePath} deleted...')
        except:
            print(deletion_error_msg, filePath)


def delete_all_alltables():
    '''
    To ensure we have a clean re-creation of the share files based on ALL ON HAND CSV data
    and to force re-creation of all all-tables, get rid of ALL By_Share folders 
    and files viz *.ETR folders, *.h5 files , *.xlsx files
    THIS IS MEANT TO BE RUN AT THE START OF process-2 AND WILL REQUIRE 
    process-2 and process-3 to be run to completion in order to refresh/restore everything
    '''

    deathList_xlsx = glob.glob(f"{g.CSV_BY_SHARE_PATH}\\*.xlsx") 
    deathList_h5 = glob.glob(f"{g.CSV_BY_SHARE_PATH}\\*.h5") 
    deathList_results_h5 = glob.glob(f"{g.OUT_PATH}\\*.h5")
    deathList_results_xlsx = glob.glob(f"{g.OUT_PATH}\\*.xlsx")
    deathList_ETR = glob.glob(f"{g.CSV_BY_SHARE_PATH}\\**\\*.ETR.CSV", recursive=True) 
    deathList_ETR_info = glob.glob(f"{g.CSV_BY_SHARE_PATH}\\**\\*.info", recursive=True) 

    grim_reap(deathList_xlsx)
    grim_reap(deathList_h5)
    grim_reap(deathList_results_h5)
    grim_reap(deathList_results_xlsx)

    grim_reap(deathList_ETR)
    grim_reap(deathList_ETR_info)


def impl_process_2(ctx, sharelist: str, recreate :bool):

    masd = 'minimum analysis_start_date'
    if masd  in g.CONFIG_RUNTIME:
        start_date = g.CONFIG_RUNTIME[masd]
    else:
        start_date = g.MINIMUM_ANALYSIS_START_DATE #functions.get_date_for_busdays_back(480)
        g.CONFIG_RUNTIME[masd] = start_date

    logging.info(
        f"/ Command {inspect.stack()[0][3]}...  Parameters: sharelist={sharelist}, recreate={recreate}. start_date will be {start_date}")
    startTime = datetime.now()

    ctx.obj['sharelist_name'] = sharelist + '.shl'
    #ctx.obj['only_share'] = one_share_only if one_share_only != 'ignore' else ''
    # note the user no longer passes a start_date on the command line
    ctx.obj['start_date'] = start_date  # see NOTE above

    #To ensure we have a clean re-creation of the share files based on ALL ON HAND CSV data
    #and to force re-creation of all all-tables, get rid of ALL By_Share folders 
    #and files viz *.ETR folders, *.h5 files , *.xlsx files
    if recreate:
        delete_all_alltables()

    # functions.gen_csv_byshare(ctx)
    num_unconsumed_txts = functions.num_unconsumed_txt_files()
    if num_unconsumed_txts == 0:
        functions.gen_csv_byshare_onepass(ctx)
    else:
        logging.warn(
            f"there are {num_unconsumed_txts} unconsumed TXT files in the IN folder.")
        print("\nPlease run 'process-1' to convert this backlog to CSV before proceeding with a 'process-2' command\n")

    logging.info(
        f"\ End {inspect.stack()[0][3]} command. Duration: {datetime.now() - startTime}")

def impl_process_3(sharelist: str, one_share_only: str, start_date: str, end_date:str, stages: list):

    logging.info(
        f"/ Command {inspect.stack()[0][3]}...  Parameters: sharelist={sharelist}, start_date={start_date}, end_date={end_date}, stages={stages}, one_share_only={one_share_only}")
    startTime = datetime.now()

    sharelist_name = sharelist + '.shl'
    only_share = '' if one_share_only == 'ignore' else one_share_only

    # this action forces the user to re-run the results conditions after process-3 activities
    functions.delete_process3_dependent_results('1')

    processing.produce_alltables_from_CSVs(
        stages, sharelist_name, start_date, end_date, only_share, top_up=False)

    trading_days = helpers.compute_trading_days(start_date,end_date)
    #summary 
    g.CONFIG_RUNTIME['process-3-last-parameters'] = f'{start_date} to {end_date} for sharelist {sharelist}. ({trading_days} trading days)'
    #individual pieces
    g.CONFIG_RUNTIME['process-3-last-start'] = start_date
    g.CONFIG_RUNTIME['process-3-last-end'] = end_date
    g.CONFIG_RUNTIME['process-3-last-sharelist'] = sharelist
    g.CONFIG_RUNTIME['process-3-last-tradingdays'] = trading_days
    #charts (hence '-' instaed of '_')
    g.CONFIG_RUNTIME['setting_chart_start'] = start_date.replace('_','-')
    g.CONFIG_RUNTIME['setting_chart_end'] = end_date.replace('_','-')
    save_runtime_config()

    logging.info(
        f"\ End {inspect.stack()[0][3]} command. Duration: {datetime.now() - startTime}")

def impl_process_3_topup(sharelist: str, one_share_only: str):

    logging.info(
        f"/ Command {inspect.stack()[0][3]}...  Parameters: sharelist={sharelist}, one_share_only={one_share_only}")
    startTime = datetime.now()

    sharelist_name = sharelist + '.shl'
    only_share = '' if one_share_only == 'ignore' else one_share_only

    # this action forces the user to re-run the results conditions after process-3 activities
    functions.delete_process3_dependent_results('1')

    stages = g.CALC_STAGES
    processing.produce_alltables_from_CSVs(
        stages, sharelist_name, start_date='', end_date='', only_share=only_share, top_up=True)

    if only_share == '':
        #functions.update_process_3_topup_runtime_stats(sharelist)
        g.CONFIG_RUNTIME['process-3-last-topup'] = f"performed {datetime.now().strftime('%Y_%m_%d %H:%M:%S')} for sharelist {sharelist}"
        save_runtime_config()

    logging.info(
        f"\ End {inspect.stack()[0][3]} command. Duration: {datetime.now() - startTime}")

def impl_results_1(origination, sharelist):

    logging.info(
        f"/ Command {inspect.stack()[0][3]}...  Parameters: sharelist={sharelist}")
    startTime = datetime.now()

    # ensure user will have to re-process these
    functions.delete_process3_dependent_results('1')

    g.CONFIG_RUNTIME['audit_structure_1St'] = functions.compile_results_1St(overwrite_results=True, sharelist=sharelist)
    save_runtime_config()

    logging.info(
        f"\ End {inspect.stack()[0][3]} command. Duration: {datetime.now() - startTime}")
    #print('\nresults-2st-pr should be run next...\n')

def impl_results_2St_Pr(ctx, sharelist):

    logging.info(
        f"/ Command {inspect.stack()[0][3]}...  Parameters: sharelist={sharelist}")
    startTime = datetime.now()

    functions.delete_process3_dependent_results('2StPr')
    g.CONFIG_RUNTIME['audit_structure_2StPr'] = functions.compile_results_2StPr(overwrite_results=True, sharelist=sharelist)
    save_runtime_config()

    logging.info(
        f"\ End {inspect.stack()[0][3]} command. Duration: {datetime.now() - startTime}")
    #print('\nresults-2st-vols should be run next...\n')

def impl_results_2St_Vols(ctx, sharelist):

    logging.info(
        f"/ Command {inspect.stack()[0][3]}...  Parameters: sharelist={sharelist}")
    startTime = datetime.now()

    functions.delete_process3_dependent_results('2StVols')
    g.CONFIG_RUNTIME['audit_structure_2StVols'] = functions.compile_results_2StVols(overwrite_results=True, sharelist=sharelist)
    save_runtime_config()

    # prepare 3jP sharelist now by creating combined_1_2_results and a _3jP_list of selections
    # in order to know how many shares will be included in 3jP sharelist (and so to be able to gauge processing time required)
    # NOTE MOVED from end of impl_results_3St_jp
    functions.compile_3jP_part1(overwrite_results=True, sharelist=sharelist)


    logging.info(
        f"\ End {inspect.stack()[0][3]} command. Duration: {datetime.now() - startTime}")
    #print('\nresults-3st-jp should be run next...\n')

def impl_results_3st_jp(ctx, start_date, end_date, sharelist):

    logging.info(
        f"/ Command {inspect.stack()[0][3]}...  Parameters: sharelist={sharelist}, start_date={start_date} end_date={end_date}")
    startTime = datetime.now()


    # NOTE This has been MOVED to end of impl_results_2StVols above
    # prepare 3jP results and sharelist by creating combined_1_2_results and a _3jP_list of selections
    # functions.compile_3jP_part1(overwrite_results=True, sharelist=sharelist)

    # now automatically do a 'normal' processing run with 'results_3jP.shl' sharelist
    # NOTE however, with this sharelist, the calc M_ParticularSumOfMV and others
    # is also performed during process-3
    reduced_sharelist = 'results_3jP'
    reduced_sharelist_fn = reduced_sharelist + '.shl'
    qualifiers = len(g.CONFIG_RUNTIME['_3jP_list'])
    proceed = qualifiers > 0
    if proceed:
        stages = [1,2]
        logging.info('')
        logging.info(f'Now performing normal process-3 run with reduced sharelist {reduced_sharelist_fn} ...')
        # NOTE this run produces an reduced members overview under key {shlist_name}_{stage}
        processing.produce_alltables_from_CSVs(stages, reduced_sharelist_fn, start_date=start_date, end_date=end_date, only_share='', top_up=False)
        # compute DjP, save Ov2 of sharelist results_3jP with DjP assigned
        functions.compile_3jP_part2(sharelist=reduced_sharelist)
        end_msg = f"{qualifiers} shares qualified and had 'jP' related calculations performed. results-3st-v2d can be run next..."
    else:
        end_msg = f"{qualifiers} shares qualified for 'jP' related calculations. See audit report. Adjust relevant conditions...?"

    #NOTE moved from impl_results_3st_v2d below
    #create a reduced sharelist results_V2d.shl plus a reduced overview with only those shares
    #in the aforementioned sharelist - no extra calculations / columns performed
    functions.delete_process3_dependent_results('3V2d')
    functions.compile_3V2d_part1(overwrite_results=True, sharelist=sharelist) 


    #functions.update_process_3_runtime_stats(start_date, reduced_sharelist)
    logging.info(f"\ End {inspect.stack()[0][3]} command. Duration: {datetime.now() - startTime}")
    print(f'\n{end_msg}\n')


def impl_results_3st_v2d(ctx, start_date, end_date, sharelist):

    logging.info(
        f"/ Command {inspect.stack()[0][3]}...  Parameters: sharelist={sharelist} start_date={start_date} end_date={end_date}")
    startTime = datetime.now()

   
    #NOTE moved to impl_results_3st_jp above
    #create a reduced sharelist results_V2d.shl plus a reduced overview with only those shares
    #in the aforementioned sharelist - no extra calculations / columns performed
    #functions.delete_process3_dependent_results('3V2d')
    #functions.compile_3V2d_part1(overwrite_results=True, sharelist=sharelist) 

    # now automatically do a 'normal' processing run with 'results_V2d.shl' sharelist
    qualifiers = len(g.CONFIG_RUNTIME['_V2d_list'])
    proceed = qualifiers > 0
    stages = [1,2]
    sharelist_to_use = 'results_V2d'
    sharelist_to_use_fn = sharelist_to_use + '.shl'
    if proceed:
        logging.info('')
        logging.info(f'Now performing normal process-3 run with reduced sharelist {sharelist_to_use_fn} ...')
        processing.produce_alltables_from_CSVs(stages, sharelist_to_use_fn, start_date=start_date, end_date=end_date, only_share='', top_up=False)
        end_msg1 = f"{qualifiers} shares qualified and had 'V2d' related calculations performed. results_3st_x3nh can be run next..."

        # now that BackwardsSlowDailyVol calcs can assumed to have been performed 
        # go on to create and save a results table and overview
        functions.compile_3V2d_part2(overwrite_results=True, sharelist=sharelist_to_use)

        end_msg = end_msg1
    else:
        end_msg = f"{qualifiers} shares qualified for 'V2d' related calculations. See audit report. Adjust relevant conditions...?"

    # NOTE moved here from impl_results-3st_x3nh below
    # create 3nh sharelist now in order to know what we're in for
    functions.delete_process3_dependent_results('3nH')
    functions.compile_3nH(sharelist=sharelist)

    #functions.update_process_3_runtime_stats(start_date, sharelist_to_use)
    logging.info(
        f"\ End {inspect.stack()[0][3]} command. Duration: {datetime.now() - startTime}")
    print(f'\n{end_msg}\n')

def impl_results_3st_x3nH(ctx, start_date, end_date, sharelist):

    logging.info(
        f"/ Command {inspect.stack()[0][3]}...  Parameters: sharelist={sharelist} start_date={start_date} end_date={end_date}")
    startTime = datetime.now()

    # NOTE moved to impl_results_3st-v2d above
    # functions.delete_process3_dependent_results('3nH')
    # functions.compile_3nH(sharelist=sharelist)

    # now automatically do a 'normal' processing run with 'results_3nH.shl' sharelist
    qualifiers = len(g.CONFIG_RUNTIME['_3nH_list'])
    proceed = qualifiers > 0
    stages = [1,2]
    sharelist_to_use = 'results_3nH'
    sharelist_to_use_fn = sharelist_to_use + '.shl'
    if proceed:
        logging.info('')
        logging.info(f'Now performing normal process-3 run with reduced sharelist {sharelist_to_use_fn} ...')
        processing.produce_alltables_from_CSVs(stages, sharelist_to_use_fn, start_date=start_date, end_date=end_date, only_share='', top_up=False)
        end_msg = f"{qualifiers} shares qualified and had '3nH' related calculations performed."
    else:
        end_msg = f"{qualifiers} shares qualified for '3nH' related calculations. See audit report. Adjust relevant conditions...?"

    logging.info(
        f"\ End {inspect.stack()[0][3]} command. Duration: {datetime.now() - startTime}")
    print(f'\n{end_msg}\n')

def _impl_results_4st_frt(ctx, overwrite :bool):
    ''' update or create from scratch the Final Results table from Default sharelist results '''

    logging.info(
        f"/ Command {inspect.stack()[0][3]}...  Parameters: ovewrite={overwrite}")
    startTime = datetime.now()

    functions.produce_frt(overwrite)

    end_msg = "FRT done"

    logging.info(
        f"\ End {inspect.stack()[0][3]} command. Duration: {datetime.now() - startTime}")
    print(f'\n{end_msg}\n')
