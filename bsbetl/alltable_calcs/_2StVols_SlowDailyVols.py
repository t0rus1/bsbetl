from bsbetl import ov_helpers
import logging
import math
from datetime import date, datetime
from numpy.core.numeric import NaN
from pandas.core.indexes.base import Index

import pandas as pd
from bsbetl.alltable_calcs import Calculation
from bsbetl.alltable_calcs.at_params import at_calc_params
from bsbetl.calc_helpers import between_dates_condition, get_row_index_from_daily_df, last_trading_row_index, single_day_condition


class _2StVols_SlowDailyVols(Calculation.Calculation):

    def __init__(self):
        super().__init__('SlowDailyVols')
        self.description = 'Modified Daily Volume calculation'
        self.dependents = ['DV']  # this column we assume exists
        self.at_computeds = ['DaysDVup', 'SDVBsl', 'SDVBm', 'SDVBf',
                             'SDVCsl', 'SDVCm', 'SDVCf1', 'SDVCf2',
                             'DVFDf', 'DVFf1', 'DVFf2', 'DVFm', 'DVFsl'
                             ]
        self.ov_computeds = []

    def day_calculate(self, df: pd.DataFrame, share_num: str, idx: Index, prior: Index, top_up: bool, stage: int):
        ''' Implementation per Gunther's 210209 Calc Daily Vol Initial Stage.odt
        Daily Vol 1. Make Slow Daily Vols:
        Calculates the 'computeds' of single (daily) row of the df 
        '''

        assert stage == 2, f'{self.name} calculation should only run at stage 2'
        # df is assumed daily since stage 2 is asserted
        # print(f'prior_idx={prior},idx={idx}')

        curday_ordinal = df.index.tolist().index(idx[0])
        #print(f'_2StVols_SlowDailyVols:day_calculate: curday_ordinal={curday_ordinal}')

        # 1a) Slow Daily Vol Basic slow "SDVBsl":
        #print(f"{idx[0]} DV= {df.at[idx[0], 'DV']}")
        if (prior is None):
            # first row
            df.at[idx[0], 'DaysDVup'] = 0
            # compute starting SlowVols figures by using average of 1st 5 days Volume
            DV_avg = df.iloc[:5]['ODV'].mean(0)
            df.at[idx[0],'SDVBsl'] = DV_avg
            df.at[idx[0],'SDVBm'] = DV_avg
            df.at[idx[0],'SDVBf'] = DV_avg

            df.at[idx[0],'SDVCsl'] = DV_avg
            df.at[idx[0],'SDVCm'] = DV_avg
            df.at[idx[0],'SDVCf1'] = DV_avg
            df.at[idx[0],'SDVCf2'] = DV_avg

        elif df.at[idx[0], 'DV'] > df.at[prior[0], 'SDVBsl']:
            # Case 1: DV D > SDVBsl D-1
            # we're not on the very first row
            # "DaysDVupD" is the number of days in a row the Slow Daily Vol Basic slow "SDVBsl D" increased.
            up_till = between_dates_condition(df, df.index[0], prior[0])
            up_tillDF = df[up_till]
            #print(f"up_tillDF rows={up_tillDF.shape[0]} {df.index[0]} -> {prior[0]}")
            if up_tillDF['SDVBsl'].is_monotonic_increasing:
                # been increasing till this row, write the count in DaysDVup
                #print(f'up_tilDF rows={up_tillDF.shape[0]}')
                daysDVup = min(up_tillDF.shape[0], 50)  # not more than 50
                daysDVup = max(1, daysDVup)  # not less than 1
                df.at[idx[0], 'DaysDVup'] = daysDVup
            else:
                daysDVup = 1
                df.at[idx[0], 'DaysDVup'] = daysDVup

            # SDVB sl D = SDVBsl D-1 + YDVBsl u / DaysDVupD * ( DVD - SDVB sl D-1)eSDVBsl u
            df.at[idx[0], 'SDVBsl'] = df.at[prior[0], 'SDVBsl'] + (at_calc_params['atp_YDVBslu']['setting']/daysDVup) * (
                df.at[idx[0], 'DV'] - df.at[prior[0], 'SDVBsl']) ** at_calc_params['atp_eSDVBslu']['setting']

        elif df.at[idx[0], 'DV'] <= df.at[prior[0], 'SDVBsl']:
            # Case 2: DVD < SDVBsl D-1
            # SDVBsl D = SDVBsl D-1 - YDVBsl d * (SDVB sl D-1 - DVD)eSDVBsl d
            df.at[idx[0], 'SDVBsl'] = df.at[prior[0], 'SDVBsl'] - at_calc_params['atp_YDVBsld']['setting'] * (
                df.at[prior[0], 'SDVBsl']-df.at[idx[0], 'DV']) ** at_calc_params['atp_eSDVBsld']['setting']

        # 1b) Slow Daily Vol Basic medium "SDVB m D":
        if (prior is None):
            # first row
            pass
        elif df.at[idx[0], 'DV'] > df.at[prior[0], 'SDVBm']:
            # Case 1: DVD > SDVBm D-1
            # SDVBm D = SDVBm D-1 + YDVBm u * ( DVD - SDVBm D-1)eSDVBm u
            df.at[idx[0], 'SDVBm'] = df.at[prior[0], 'SDVBm'] + at_calc_params['atp_YDVBmu']['setting'] * (
                df.at[idx[0], 'DV'] - df.at[prior[0], 'SDVBm']) ** at_calc_params['atp_eSDVBmu']['setting']

        elif df.at[idx[0], 'DV'] <= df.at[prior[0], 'SDVBm']:
            # Case 2: DVD < SDVBm D-1
            # SDVBm D = SDVBm D-1 - YDVB m d * (SDVBm D-1 - DVD)eSDVBm d
            df.at[idx[0], 'SDVBm'] = df.at[prior[0], 'SDVBm'] - at_calc_params['atp_YDVBmd']['setting'] * (
                df.at[prior[0], 'SDVBm']-df.at[idx[0], 'DV']) ** at_calc_params['atp_eSDVBmd']['setting']

        # 1c) Slow Daily Vol Basic fast "SDVB bf D":
        if (prior is None):
            # first row
            pass
        elif df.at[idx[0], 'DV'] > df.at[prior[0], 'SDVBf']:
            # Case 1: DVD > SDVBf D-1
            # SDVBf D = SDVBf D-1 + YDVBf u * ( DVD - SDVBf D-1)eSDVBf u
            df.at[idx[0], 'SDVBf'] = df.at[prior[0], 'SDVBf'] + at_calc_params['atp_YDVBfu']['setting'] * (
                df.at[idx[0], 'DV'] - df.at[prior[0], 'SDVBf']) ** at_calc_params['atp_eSDVBfu']['setting']

        elif df.at[idx[0], 'DV'] <= df.at[prior[0], 'SDVBf']:
            # Case 2: DVD < SDVBf D-1
            # SDVBf D = SDVBf D-1 - YDVB f d * (SDVBf D-1 - DVD)eSDVBf d
            df.at[idx[0], 'SDVBf'] = df.at[prior[0], 'SDVBf'] - at_calc_params['atp_YDVBfd']['setting'] * (
                df.at[prior[0], 'SDVBf']-df.at[idx[0], 'DV']) ** at_calc_params['atp_eSDVBfd']['setting']

        # 1d) Slow Daily Vol Compare slow "SDVCsl D":
        if (prior is None):
            # first row
            pass
        elif df.at[idx[0], 'DV'] > df.at[prior[0], 'SDVCsl']:
            # Case 1: DVD > SDVCsl D-1
            # SDVCsl D = SDVCsl D-1 + YDVCsl u * ( DVD - SDVCsl D-1)eSDVCsl u
            df.at[idx[0], 'SDVCsl'] = df.at[prior[0], 'SDVCsl'] + at_calc_params['atp_YDVCslu']['setting'] * (
                df.at[idx[0], 'DV'] - df.at[prior[0], 'SDVCsl']) ** at_calc_params['atp_eSDVCslu']['setting']

        elif df.at[idx[0], 'DV'] <= df.at[prior[0], 'SDVCsl']:
            # Case 2: DVD < SDVCsl D-1
            # SDVCsl D = SDVCsl D-1 - YDVC sl d * (SDVCsl D-1 - DVD)eSDVCsl d
            df.at[idx[0], 'SDVCsl'] = df.at[prior[0], 'SDVCsl'] - at_calc_params['atp_YDVCsld']['setting'] * (
                df.at[prior[0], 'SDVCsl']-df.at[idx[0], 'DV']) ** at_calc_params['atp_eSDVCsld']['setting']

        # 1e) Slow Daily Vol Compare medium "SDVCm D":
        if (prior is None):
            # first row
            pass
        elif df.at[idx[0], 'DV'] > df.at[prior[0], 'SDVCm']:
            # Case 1: DVD > SDVCm D-1
            # SDVCm D = SDVCm D-1 + YDVCm u * ( DVD - SDVCm D-1)eSDVCm u
            df.at[idx[0], 'SDVCm'] = df.at[prior[0], 'SDVCm'] + at_calc_params['atp_YDVCmu']['setting'] * (
                df.at[idx[0], 'DV'] - df.at[prior[0], 'SDVCm']) ** at_calc_params['atp_eSDVCmu']['setting']

        elif df.at[idx[0], 'DV'] <= df.at[prior[0], 'SDVCm']:
            # Case 2: DVD < SDVCm D-1
            # SDVCm D = SDVCm D-1 - YDVC m d * (SDVCm D-1 - DVD)eSDVCm d
            df.at[idx[0], 'SDVCm'] = df.at[prior[0], 'SDVCm'] - at_calc_params['atp_YDVCmd']['setting'] * (
                df.at[prior[0], 'SDVCm']-df.at[idx[0], 'DV']) ** at_calc_params['atp_eSDVCmd']['setting']

        # 1f) Slow Daily Vol Compare fast1 "SDVCf1 D":
        if (prior is None):
            # first row
            pass
        elif df.at[idx[0], 'DV'] > df.at[prior[0], 'SDVCf1']:
            # Case 1: DVD > SDVCf1 D-1
            # SDVCm D = SDVCf1 D-1 + YDVCf1 u * ( DVD - SDVCf1 D-1)eSDVCf1 u
            df.at[idx[0], 'SDVCf1'] = df.at[prior[0], 'SDVCf1'] + at_calc_params['atp_YDVCf1u']['setting'] * (
                df.at[idx[0], 'DV'] - df.at[prior[0], 'SDVCf1']) ** at_calc_params['atp_eSDVCf1u']['setting']

        elif df.at[idx[0], 'DV'] <= df.at[prior[0], 'SDVCf1']:
            # Case 2: DVD < SDVCf1 D-1
            # SDVCm D = SDVCf1 D-1 - YDVC f1 d * (SDVCf1 D-1 - DVD)eSDVCf1 d
            df.at[idx[0], 'SDVCf1'] = df.at[prior[0], 'SDVCf1'] - at_calc_params['atp_YDVCf1d']['setting'] * (
                df.at[prior[0], 'SDVCf1']-df.at[idx[0], 'DV']) ** at_calc_params['atp_eSDVCf1d']['setting']

        # 1g) Slow Daily Vol Compare fast1 "SDVCf2 D":
        if (prior is None):
            # first row
            pass
        elif df.at[idx[0], 'DV'] > df.at[prior[0], 'SDVCf2']:
            # Case 1: DVD > SDVCf2 D-1
            # SDVCf2 D = SDVCf2 D-1 + YDVCf2 u * ( DVD - SDVCf2 D-1)eSDVCf2 u
            df.at[idx[0], 'SDVCf2'] = df.at[prior[0], 'SDVCf2'] + at_calc_params['atp_YDVCf2u']['setting'] * (
                df.at[idx[0], 'DV'] - df.at[prior[0], 'SDVCf2']) ** at_calc_params['atp_eSDVCf2u']['setting']

        elif df.at[idx[0], 'DV'] <= df.at[prior[0], 'SDVCf2']:
            # Case 2: DVD < SDVCf2 D-1
            # SDVCf2 D = SDVCf2 D-1 - YDVC f2 d * (SDVCf2 D-1 - DVD)eSDVCf2 d
            df.at[idx[0], 'SDVCf2'] = df.at[prior[0], 'SDVCf2'] - at_calc_params['atp_YDVCf2d']['setting'] * (
                df.at[prior[0], 'SDVCf2']-df.at[idx[0], 'DV']) ** at_calc_params['atp_eSDVCf2d']['setting']

        # 1h) As in the old ShW, we need figures to show a volumes constellation, the Daily Vols Figure, "DVFxx"
        if not prior is None:
            # 'DVFDf' ???
            # df.at[idx[0], 'DVFDf'] = df.at[idx[0], 'DV'] / df.at[idx[0], 'SDVBf']

            # 'DVFf3'
            if curday_ordinal >= 1:
                _1_back=df.index[curday_ordinal-1]
                df.at[idx[0], 'DVFf3'] = df.at[idx[0], 'DV'] / df.at[_1_back, 'SDVBf']

            # 'DVFf2'
            if curday_ordinal >= 2:
                _2_back=df.index[curday_ordinal-2]
                df.at[idx[0], 'DVFf2'] = df.at[idx[0], 'SDVCf2'] / df.at[_2_back, 'SDVBf']

            # 'DVFf1'
            if curday_ordinal >= 3:
                _3_back=df.index[curday_ordinal-3]
                df.at[idx[0], 'DVFf1'] = df.at[idx[0], 'SDVCf1'] / df.at[_3_back, 'SDVBf']

            # 'DVFm'
            df.at[idx[0], 'DVFm'] = df.at[idx[0], 'SDVCm'] / df.at[idx[0], 'SDVBm']

            # 'DVFsl'
            df.at[idx[0], 'DVFsl'] = df.at[idx[0], 'SDVCsl'] / df.at[idx[0], 'SDVBsl']

    
    ''' additional calcs performed AFTER  day by day operations '''
    def wrap_up(self, df, share_num, calc_dates_in_df, top_up, stage):

        assert stage == 2, f'{self.name} wrap_up calculation should only run at stage 2'

        # assign into Ov SDVBf.D-1, and SDVBf.D-2
        try:
            ov_helpers.global_ov_update(share_num, 'SDVBf.D-1', df.loc[df.index[-2],'SDVBf'])
            ov_helpers.global_ov_update(share_num, 'SDVBf.D-2', df.loc[df.index[-3],'SDVBf'])
        except IndexError as exc:
            logging.error(f'_2StVols_SlowDailyVols wrap_up exception {exc}')


        return