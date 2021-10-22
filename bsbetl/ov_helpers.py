from datetime import timedelta
import logging
from typing import Any
import pandas as pd
from pandas._libs.tslibs import Timestamp
from bsbetl import g


def global_ov_update(share_num: str, column: str, value):

    #print(f'updating Ov for share_num: {share_num} col {column} value {value}')
    g.df_ov.at[share_num, column] = value


def ov_last_day(df: pd.DataFrame, share_num: str, df_column: str, ov_column: str):
    """ grabs last day's last df_column value in the df and stores it in the ov_column of the ov """

    try:
        global_ov_update(
            share_num, ov_column, df.loc[df.index[-1]][df_column])
    except KeyError as ke:
        logging.error(f'KeyError: {ke}')


def ov_2ndlast_day(df: pd.DataFrame, share_num: str, df_column: str, ov_column: str):
    """ grabs 2nd last day's last df_column value in the df and stores it in the ov_column of the ov """

    last_stamp = df.index[-1]
    day_b4_last = last_stamp - timedelta(days=1)
    target_idx = Timestamp(year=day_b4_last.year, month=day_b4_last.month,
                           day=day_b4_last.day, hour=g.LAST_BUS_HOUR_SLOT, minute=g.LAST_BUS_MIN_SLOT)
    try:
        global_ov_update(
            share_num, ov_column, df.loc[target_idx][df_column])
    except KeyError as ke:
        logging.error(f'KeyError: {ke}')


def ov_biggest(df: pd.DataFrame, share_num: str, df_column: str, ov_column: str, days_back: int):
    """ computes maximum value over daysback days in the df column df_column and stores it in the ov_column of the ov"""

    last_day = df.index[-1]
    twenty_days_back = last_day - timedelta(days=20)

    try:
        biggest = df.loc[twenty_days_back:last_day, df_column].max()
        global_ov_update(share_num, ov_column, biggest)
    except KeyError as ke:
        logging.error(f'KeyError: {ke}')


def ov_smallest(df: pd.DataFrame, share_num: str, df_column: str, ov_column: str, days_back: int):
    """ computes minimum value over daysback days in the df column df_column and stores it in the ov_column of the ov"""

    last_day = df.index[-1]
    twenty_days_back = last_day - timedelta(days=20)

    try:
        smallest = df.loc[twenty_days_back:last_day, df_column].min()
        global_ov_update(share_num, ov_column, smallest)
    except KeyError as ke:
        logging.error(f'KeyError: {ke}')


def ov_price_factor(df: pd.DataFrame, share_num: str, df_column: str, ov_column: str):

    last_day = df.index[-1]
    two_days_back = last_day - timedelta(days=1)

    try:
        last_day_price = df.loc[last_day][g.AT_COL2INDEX[df_column]]
        two_day_back_price = df.loc[two_days_back][g.AT_COL2INDEX[df_column]]

        price_factor = last_day_price / two_day_back_price if two_day_back_price != 0 else 0
        global_ov_update(share_num, ov_column, price_factor)
    except KeyError as ke:
        logging.error(f'KeyError: {ke}')


def bulk_ov_update_stage_1():

    #
    #M_DailyHighPrice
    # =========================
    #
    # ov_helpers.global_ov_update(share_num, 'DT', dt)
    # ov_helpers.global_ov_update(share_num, 'DT1', dt1)
    # ov_helpers.global_ov_update(share_num, 'SDT', sdt)
    # ov_helpers.global_ov_update(share_num, 'ODV', dv)
    # ov_helpers.global_ov_update(share_num, 'AvMV', amv)
    # ov_helpers.global_ov_update(share_num, 'DHP', dhp)
    # ov_helpers.global_ov_update(share_num, 'DHP.D-1', dhp_stack.pop())            
    # ov_helpers.global_ov_update(share_num, 'DHP.D-2', dhp_stack.pop())            
    # ov_helpers.global_ov_update(share_num, 'DHP.D-3', dhp_stack.pop())            
    # ov_helpers.global_ov_update(share_num, 'DHP.D-4', dhp_stack.pop())            
    # ov_helpers.global_ov_update(share_num, 'DHP.D-5', dhp_stack.pop())            
    # ov_helpers.global_ov_update(share_num, 'DHP.D-6', dhp_stack.pop())            
    # ov_helpers.global_ov_update(share_num, 'DHP.D-7', dhp_stack.pop())            
    # ov_helpers.global_ov_update(share_num, 'DHP.D-8', dhp_stack.pop())            
    # ov_helpers.global_ov_update(share_num, 'DHP.D-9', dhp_stack.pop())            
    #ov_helpers.global_ov_update(share_num, 'DLP', dlp)
    # DLOCP has additional assoc columns
    #ov_helpers.global_ov_update(share_num, 'DLOCP', dlocp)
    # ov_helpers.global_ov_update(share_num, 'DLOCP.D-1', dlocp_stack.pop())            
    # ov_helpers.global_ov_update(share_num, 'DLOCP.D-2', dlocp_stack.pop())            
    # ov_helpers.global_ov_update(share_num, 'DLOCP.D-3', dlocp_stack.pop())            
    # ov_helpers.global_ov_update(share_num, 'DLOCP.D-4', dmp_stack.pop())            
    # ov_helpers.global_ov_update(share_num, 'DLOCP.D-5', dmp_stack.pop())            
    # ov_helpers.global_ov_update(share_num, 'DLOCP.D-6', dmp_stack.pop())            
    # ov_helpers.global_ov_update(share_num, 'DLOCP.D-7', dmp_stack.pop())            
    # ov_helpers.global_ov_update(share_num, 'DLOCP.D-8', dmp_stack.pop())            
    # ov_helpers.global_ov_update(share_num, 'DLOCP.D-9', dmp_stack.pop())            
    #ov_helpers.global_ov_update(share_num, 'DHOCP', dhocp)
    # DMP has additional assoc columns
    #ov_helpers.global_ov_update(share_num, 'DMP', dmp)
    #ov_helpers.global_ov_update(share_num, 'DMP.D-1', dmp_stack.pop())            
    #ov_helpers.global_ov_update(share_num, 'DMP.D-2', dmp_stack.pop())            
    #ov_helpers.global_ov_update(share_num, 'DMP.D-3', dmp_stack.pop())            
    #ov_helpers.global_ov_update(share_num, 'DCP', dcp)
    #ov_helpers.global_ov_update(share_num, 'DOP', dop)
    #ov_helpers.global_ov_update(share_num, 'DHPbig', dhp_big)
    #ov_helpers.global_ov_update(share_num, 'DLPsmall', dlp_small)
    #ov_helpers.global_ov_update(share_num, 'DOP.D-1', dop_stack.pop())

    #
    #M_ParticularSumOfMV
    #==========================================

    # ov_helpers.global_ov_update(share_num, 'PSMV', psmv_last)
    # ov_helpers.global_ov_update(share_num, 'CV1', cv1)
    # ov_helpers.global_ov_update(share_num, 'RCV1', rcv1)

    # CV1s = ['CV1.D-1','CV1.D-2','CV1.D-3','CV1.D-4','CV1.D-5',]
    # for entry in CV1s:
    #     cv1=cv1_stack.pop()
    #     ov_helpers.global_ov_update(share_num, entry, cv1)

    # RCV1s = ['RCV1.D-1','RCV1.D-2','RCV1.D-3','RCV1.D-4','RCV1.D-5',]
    # smallest_rcv1 = math.inf
    # for entry in RCV1s:
    #     rcv1=rcv1_stack.pop()
    #     ov_helpers.global_ov_update(share_num, entry, rcv1)
    #     # also grab the smallest rcv1 while assigning
    #     if rcv1 < smallest_rcv1:
    #         smallest_rcv1 = rcv1

    # assign smallest
    #ov_helpers.global_ov_update(share_num, 'RCV1small', smallest_rcv1)

    #M_RelativeMinutelyVolume
    #==========================================
    #

    # global_ov_update(share_num, 'MSmp', MSmp)
    # global_ov_update(share_num, 'MSmpv', MSmpv)
    # global_ov_update(share_num, 'MSmv', MSmv)

    return

def bulk_ov_update_stage_2():

    # _1St_DailyPrices
    # =====================================
    #

    # ov_helpers.global_ov_update(share_num, 'SDHPGr1sh', df.at[cur_idx,'SDHPGr1sh'])
    # ov_helpers.global_ov_update(share_num, 'SDHPGr1m', df.at[cur_idx,'SDHPGr1m'])
    # ov_helpers.global_ov_update(share_num, 'SDHPGr1lo', df.at[cur_idx,'SDHPGr1lo'])
    # ov_helpers.global_ov_update(share_num, 'SDT1f', df.at[cur_idx,'SDT1f'])
    # ov_helpers.global_ov_update(share_num, 'SDT1sl', df.at[cur_idx,'SDT1sl'])
    # ov_helpers.global_ov_update(share_num, 'DTF', df.at[cur_idx,'DTF'])

    # _2StPr_HundredDaysBroadness
    # ===================================
    #
    #     ov_helpers.global_ov_update(share_num, 'HBF', broadness_for_ov)

    # _2StPr_PriceHighestSince
    # ====================================
    #
    # put these DHP numbers into the Overview for the share
    # try:
    #     ov_helpers.global_ov_update(share_num, 'DHPlasthi', DHPlasthi_stack.pop())
    # except IndexError: #pop from empty list we anticipate
    #     pass

    # ov_helpers.global_ov_update(share_num, 'DHPlast3hi', DHPlast3hi)

    # try:
    #     ov_helpers.global_ov_update(share_num, 'DHPlasthi.D-1', DHPlasthi_stack.pop())
    # except IndexError: #pop from empty list we anticipate
    #     pass

    # try:
    #     ov_helpers.global_ov_update(share_num, 'DHPlasthi3perc', DHPlasthi3perc_stack.pop())
    # except IndexError: #pop from empty list we anticipate
    #     pass
    # try:
    #     ov_helpers.global_ov_update(share_num, 'DHPlasthi3perc.D-1', DHPlasthi3perc_stack.pop())
    # except IndexError: #pop from empty list we anticipate
    #     pass

    # try:
    #     ov_helpers.global_ov_update(share_num, 'DHPlast20hi', DHPlast20hi_stack.pop())
    # except IndexError: #pop from empty list we anticipate
    #     pass
    
    # ov_helpers.global_ov_update(share_num, 'DHPlast20hi3perc', DHPlast20hi3perc)

    # try:
    #     ov_helpers.global_ov_update(share_num, 'DHPlast20hi.D-1', DHPlast20hi_stack.pop())
    # except IndexError: #pop from empty list we anticipate
    #     pass

    # #ov_helpers.global_ov_update(share_num, 'DHPbig', DHPbig)
    # ov_helpers.global_ov_update(share_num, 'DaysDHPlasthi', DaysDHPlasthi)
    # ov_helpers.global_ov_update(share_num, 'DaysDHPlast20hi', DaysDHPlast20hi)
    # ov_helpers.global_ov_update(share_num, 'DaysDHPlasthi3perc', DaysDHPlasthi3perc)

    # ov_helpers.global_ov_update(share_num, 'DDHPlasthi', DDHPlasthi)
    # ov_helpers.global_ov_update(share_num, 'DDHPlasthi3perc', DDHPlasthi3perc)
    # ov_helpers.global_ov_update(share_num, 'DDHPlast20hi', DDHPlast20hi)


    #
    # _2StPr_AvgOfDailyHighPriceGradient
    # =======================================
    #
    # try:
    #     global_ov_update(share_num, 'DHPGrAvSh', DHPGrAvSh)
    #     DHPGrAvSh_stack.pop() # discard last one
    #     global_ov_update(share_num, 'DHPGrAvSh.D-1', DHPGrAvSh_stack.pop())
    #     global_ov_update(share_num, 'DHPGrAvSh.D-2', DHPGrAvSh_stack.pop())


    #     global_ov_update(share_num, 'DHPGrAvMi', DHPGrAvMi)
    #     global_ov_update(share_num, 'DHPGrAvLo', DHPGrAvLo)

    #     global_ov_update(share_num, 'DHPGrDiSl', DHPGrDiSl)
    #     DHPGrDiSl_stack.pop()
    #     global_ov_update(share_num, 'DHPGrDiSl.D-1', DHPGrDiSl_stack.pop())
        
    #     # we need DAPGrDiF.D-1 also in the Ov
    #     global_ov_update(share_num, 'DHPGrDiF', DHPGrDiF)
    #     global_ov_update(share_num, 'DHPGrDiF.D-1',df.loc[df.index[-2],'DHPGrDiF'])

    #     global_ov_update(share_num, 'DHPGr',df.loc[df.index[-1],'DHPGr'])

    #     global_ov_update(share_num, 'pnt1_DHPGrDiF', 0.1*DHPGrDiF)
    #     global_ov_update(share_num, 'pnt3_DHPGrDiF', 0.3*DHPGrDiF)
    # except IndexError as exc:
    #     logging.error(f'_2StPr_AvgOfDailyHighPriceGradient exception {exc}')

#remember day_by_day_calcs

    #
    #_2StPr_SlowBroadness
    #===================
    #
    # # now for the overview... use last assigned values
    # sdhp = df.at[prior_index,'SDHP']
    # sbr = df.at[prior_index,'SBr']
    # ov_helpers.global_ov_update(share_num, 'SDHP', sdhp)
    
    # # SBr
    # ov_helpers.global_ov_update(share_num, 'SBr', sbr)
    # # prior day values also needed in the Ov
    # try:
    #     ov_helpers.global_ov_update(share_num, 'SBr.D-1', df.loc[df.index[-2],'SBr'])
    #     ov_helpers.global_ov_update(share_num, 'SBr.D-2', df.loc[df.index[-3],'SBr'])
    #     ov_helpers.global_ov_update(share_num, 'SBr.D-3', df.loc[df.index[-4],'SBr'])
    #     ov_helpers.global_ov_update(share_num, 'SBr.D-4', df.loc[df.index[-5],'SBr'])
    #     ov_helpers.global_ov_update(share_num, 'SBr.D-5', df.loc[df.index[-6],'SBr'])
    # except IndexError as exc:
    #     pass

    #
    #D_BackwardsSlowDailyVol
    #====================================
    #
    # ov_helpers.global_ov_update(share_num, 'bSDV', df.iat[max_row_idx, bSDV_col_idx])
    # ov_helpers.global_ov_update(share_num, 'RbSDV', df.iat[max_row_idx, RbSDV_col_idx])

    # try:
    #     ov_helpers.global_ov_update(share_num, 'RbSDV.D-4', df.iat[max_row_idx-4, RbSDV_col_idx])
    #     ov_helpers.global_ov_update(share_num, 'RbSDV.D-7', df.iat[max_row_idx-7, RbSDV_col_idx])
    # except IndexError as exc:
    #     logging.warn(f'BackwardsSlowDailyVol exception {exc} when updating RbSDV.D-4 and/or RbSDV.D-7')


    return