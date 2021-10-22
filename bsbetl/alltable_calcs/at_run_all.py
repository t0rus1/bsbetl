from bsbetl.functions import is_st3_selected_share
import logging
import traceback
import datetime

from numpy.core.fromnumeric import trace

from bsbetl import g, ov_helpers
from bsbetl.alltable_calcs import at_columns
from bsbetl.alltable_calcs._1St_DailyPrices import _1St_DailyPrices
from bsbetl.alltable_calcs._2StPr_AvgOfDailyHighPriceGradient import \
    _2StPr_AvgOfDailyHighPriceGradient
from bsbetl.alltable_calcs._2StPr_HundredDaysBroadness import \
    _2StPr_HundredDaysBroadness
from bsbetl.alltable_calcs._2StPr_PriceHighestSince import \
    _2StPr_PriceHighestSince
from bsbetl.alltable_calcs._2StPr_SlowBroadness import _2StPr_SlowBroadness
from bsbetl.alltable_calcs._2StPr_SlowDailyLowerOCPriceGradient import \
    _2StPr_SlowDailyLowerOCPriceGradient
from bsbetl.alltable_calcs._2StVols_ModifiedDailyVol import \
    _2StVols_ModifiedDailyVol
from bsbetl.alltable_calcs._2StVols_SlowDailyVols import _2StVols_SlowDailyVols
from bsbetl.alltable_calcs.D_BackwardsSlowDailyVol import \
    D_BackwardsSlowDailyVol
from bsbetl.alltable_calcs.M_DailyHighPrice import M_DailyHighPrice
from bsbetl.alltable_calcs.M_ParticularSumOfMV import M_ParticularSumOfMV
from bsbetl.alltable_calcs.M_RelativeMinutelyVolume import \
    M_RelativeMinutelyVolume
from bsbetl.alltable_calcs.M_SpecialSlowMinutePrices import \
    M_SpecialSlowMinutePrices
from bsbetl.calc_helpers import (get_row_index_from_daily_df,
                                 n_days_back_filter, sharenum_in_spinoff_list)
from bsbetl.func_helpers import get_last_stored_df, is_initial_process_3_stage
from numpy.core.numeric import NaN, full

''' a single function which runs each of the all-table calcs sequentially '''

def init_stage2_at_from_stage1(df_stage2, share_num):
    ''' we need to grab selected columns (needed for Ovs) from stage1 At and place in the stage2 df  '''

    df_stage1 = get_last_stored_df(share_num, 1)

    for col in at_columns.AT_STAGE1_CARRY_FORWARDS:
        # summing effectively grabs the last value of the day
        try:
            colnum = df_stage2.columns.get_loc(col)

            stage1_series = df_stage1[col].resample('B', label='left', origin='start_day').sum()
            df_stage2[col] = stage1_series

            # also the overview entry
            ov_helpers.global_ov_update(share_num, col, df_stage2.iloc[-1,colnum])

        except KeyError as ke:
            logging.error(f'KeyError {ke} caused by init_stage2_at_from_stage1, col={col}, colnum={colnum}')



def day_by_day_calcs(df, share_num: str, calc_dates_in_df: list, top_up: bool,  stage: int, at_tracef, shlist_name):

    # DAILY VOLS
    # here are computations which depend on prior day results
    # instantiate the needed calculators

    # for At: ['DaysDVup', 'SDVBsl', 'SDVBm', 'SDVBf', 'SDVCsl', 'SDVCm', 
    #          'SDVCf1', 'SDVCf2', 'DVFDf', 'DVFf1', 'DVFf2', 'DVFm', 'DVFsl']
    # for Ov: none at present
    SDV_calc = _2StVols_SlowDailyVols()
    logging.debug(f'{SDV_calc.description} - class instantiated')

    # we also need to reference 'DV' in the dataframe so add it now
    # if not 'DV' in df.columns:
    #     df['DV'] = 0.

    # Daily Vol 2. Make the modified Daily Vol "DV"
    # for At: ['DV', 'DVv']
    # for Ov: none at present
    MDV_calc = _2StVols_ModifiedDailyVol()
    logging.debug(f'{MDV_calc.description} - class instantiated')


    SDLOCP_calc = _2StPr_SlowDailyLowerOCPriceGradient()
    logging.debug(f'{SDLOCP_calc.description} - class instantiated')


    keep_going = True
    prior = None
    stuck_count = 0
    which_calc = ''
    # due to the requirements of the MDV_calc specifications
    # we need an explicit iterator to control advancement
    # so we don't use a standard for - in loop: like
    # for cur_dt in calc_dates_in_df:
    dt_iter = iter(calc_dates_in_df)
    cur_dt = next(dt_iter)
    while keep_going:
        # get index to the row we will be computing
        idx = get_row_index_from_daily_df(df, cur_dt)
        # print(idx)
        if len(idx) > 0:
            # do each calculation one day at a time, in sequence
            # NOTE we do the MDV first, since it calculates a DV we can use
            try:
                which_calc = 'MDV'
                MDV_calc.day_calculate(df, share_num, idx, prior, top_up, stage)
                # now SDV
                which_calc = 'SDV'
                SDV_calc.day_calculate(df, share_num, idx, prior, top_up, stage)

                # 2. St. Pr. 5.: 
                # Make Slow Daily Lower Open Close Price Gradient, SLOCPGr
                which_calc = 'SDLOCP'
                SDLOCP_calc.day_calculate(df, share_num, idx, prior, top_up, stage)

            except Exception as exc:
                logging.error(f"day_by_day {which_calc} exception:\n {exc}\n (stage {stage})\nAbnormal termination\n")
                exit()
            # back to MDV related matter...
            # check if in the last 20 days the following condition (at least once) was fulfilled?:
            # DVD > 2 * SDVBm D-1
            df_20 = df[n_days_back_filter(df, cur_dt, 20)]
            # count occurences
            DV_overs = 0
            DV_thresh = 0
            if prior is not None:
                DV_thresh = 2 * df.at[prior[0], 'SDVBm']
            for index, row in df_20.iterrows():
                if row['DV'] > DV_thresh:
                    DV_overs = DV_overs+1
                    break

            # do not move on if DV_overs==0
            if df_20.shape[0] < 20 or DV_overs > 0 or stuck_count > 100:
                try:
                    # moving on to next row
                    cur_dt = next(dt_iter)
                    stuck_count = 0
                except StopIteration:
                    keep_going = False
            else:
                stuck_count = stuck_count+1
        else:
            try:
                cur_dt = next(dt_iter)
            except StopIteration:
                keep_going = False

        # save idx as prior
        # before looping to the next row
        if len(idx) > 0:
            prior = idx

    # final wrap up 
    SDV_calc.wrap_up(df, share_num, calc_dates_in_df, top_up, stage)
    SDLOCP_calc.wrap_up(df, share_num, calc_dates_in_df, top_up, stage)

    logging.info('day_by_day calculations (MDV,SDV,SDLOCP) done.')
    at_tracef.write(f'({stage}) day_by_day calculations (MDV,SDV,SDLOCP) done, sharelist={shlist_name}\n')

    return


def run_all_alltable_calcs(df, share_num: str, calc_dates_in_df: list, top_up: bool,  stage: int, 
                            shlist_name :str, at_tracef, only_share :str):
    ''' execute each at_calc in turn

        NOTE: if topping up:
        Even though df will be the entire df (ie incl rows from the original start_date),
        dates_in_df will be a reduced 'tail' range. The idea is to compute only the tail piece and not to alter any of the history.
    '''

    # start trace with a timestamp
    at_tracef.write(f'{share_num}\n')
    at_tracef.write('{:%Y-%m-%d %H:%M:%S} \n\n'.format(datetime.datetime.now()))

    # up front ensure every needed column is present
    for col in at_columns.AT_COLS:
        if not col in df.columns:
            df[col] = 0.0000 #seems like 0 is a better initial value than NaN

    curr_calc = ''
    try:
        if stage == 1:  # Minutes granularity
            # can skip this step if we are running a 'results' command, since this step will have been done
            if len(only_share) > 0 or is_initial_process_3_stage():
                curr_calc = 'DHP'
                # normal process-3 processing
                M_DailyHighPrice().calculate(df, share_num, calc_dates_in_df, top_up, stage)
                at_tracef.write(f'({stage}) M_DailyHighPrice (process-3 cmd assumed, sharelist={shlist_name})\n')

            if (len(only_share) > 0) or (not is_initial_process_3_stage() and is_st3_selected_share(shlist_name,share_num)):
                curr_calc = 'PSMV'
                # NOTE try to improve performance of the function below
                M_ParticularSumOfMV().calculate(df, share_num, calc_dates_in_df, top_up, stage)                
                at_tracef.write(f'({stage}) M_ParticularSumOfMV (sharelist={shlist_name})\n')
                curr_calc='SMP'
                M_SpecialSlowMinutePrices().calculate(df, share_num, calc_dates_in_df, top_up, stage)
                at_tracef.write(f'({stage}) M_SpecialSlowMinutePrices (sharelist={shlist_name})\n')
                curr_calc = 'RMV'
                M_RelativeMinutelyVolume().calculate(df, share_num, calc_dates_in_df, top_up, stage)
                at_tracef.write(f'({stage}) M_RelativeMinutelyVolume (sharelist={shlist_name})\n')

        elif stage == 2: 
            # in this section we do EACH CALCULATION FOR THE ENTIRE DATE RANGE
            # fill eg the DAP and other columns from stage 1's alltable
            init_stage2_at_from_stage1(df, share_num)

            if len(only_share) > 0 or is_initial_process_3_stage():

                curr_calc = '_1St_DailyPrices'
                _1St_DailyPrices().calculate(df, share_num, calc_dates_in_df, top_up, stage)
                at_tracef.write(f'({stage}) _1St_DailyPrices (process-3 cmd, sharelist={shlist_name})\n')

                # 2. Stage Prices:
                # 2. St. Pr. 1: Make Hundred days Broadness Figure HBF:
                curr_calc = '_2StPr_HundredDaysBroadness'
                _2StPr_HundredDaysBroadness().calculate(df, share_num, calc_dates_in_df, top_up, stage)
                at_tracef.write(f'({stage}) _2StPr_HundredDaysBroadness (process-3 cmd, sharelist={shlist_name})\n')

                # 2. St. Pr. 2.: Find Price highest since ...  
                curr_calc = '_2StPr_PriceHighestSince'
                _2StPr_PriceHighestSince().calculate(df, share_num, calc_dates_in_df, top_up, stage)
                at_tracef.write(f'({stage}) {curr_calc}  (process-3 cmd, sharelist={shlist_name})\n')

                # 2. St. Pr. 4.: 
                # Find the Average of the Daily High Price Gradient,  "DHPGrAv" and the Distances from it, "DHPGrDi":
                curr_calc = '_2StPr_AvgOfDailyHighPriceGradient'
                _2StPr_AvgOfDailyHighPriceGradient().calculate(df, share_num, calc_dates_in_df, top_up, stage)
                at_tracef.write(f'({stage}) {curr_calc}  (process-3 cmd, sharelist={shlist_name})\n')

                # # NOTE ONE DAY AT A TIME section
                # # in which various calculations are interleaved day by day
                # curr_calc = 'day_by_day_calcs'
                day_by_day_calcs(df, share_num, calc_dates_in_df, top_up, stage, at_tracef, shlist_name)

                # additional vector operations now that day_by_day calcs have been done
                curr_calc = '_2StPr_SlowBroadness'
                _2StPr_SlowBroadness().calculate(df, share_num, calc_dates_in_df, top_up, stage)
                at_tracef.write(f'({stage}) {curr_calc}  (process-3 cmd, sharelist={shlist_name})\n')
            else:
                at_tracef.write(f'_1St_DailyPrices,_2StPr_HundredDaysBroadness,_2StPr_PriceHighestSince,_2StPr_AvgOfDailyHighPriceGradient,day_by_day_calcs,_2StPr_SlowBroadness  (stage {stage}) ALL SKIPPED, sharelist={shlist_name}\n')

            curr_calc = 'BackwardsSlowDailyVol'
            D_BackwardsSlowDailyVol().calculate(df,share_num,calc_dates_in_df, top_up,stage)
            at_tracef.write(f'({stage}) {curr_calc}  (process-3 cmd, sharelist={shlist_name})\n')

    except Exception as exc:
        logging.error(
            f"{curr_calc} exception:\n {exc}\n (stage {stage})\nAbnormal termination \n {traceback.format_exc()}")
        exit()

    return
