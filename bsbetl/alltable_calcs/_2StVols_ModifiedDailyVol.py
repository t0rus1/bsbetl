import logging
import math
from datetime import date, datetime
from numpy.core.numeric import NaN

import pandas as pd
from bsbetl.alltable_calcs import Calculation
from bsbetl.alltable_calcs.at_params import at_calc_params
from bsbetl.calc_helpers import get_row_index_from_daily_df, last_trading_row_index, n_days_back_filter


class _2StVols_ModifiedDailyVol(Calculation.Calculation):

    def __init__(self):
        super().__init__('ModifiedDailyVol')
        self.description = 'Modified Daily Volume calculation'
        self.dependents = ['SDV']
        self.at_computeds = ['DV', 'DVv']
        self.ov_computeds = []

    def step_2(self, df, row_idx, prior_idx):

        if len(row_idx) > 0:
            # Reduce DVD virtual each day:
            df.at[row_idx[0], 'DVv'] = df.at[row_idx[0], 'DVv'] - at_calc_params['atp_ModDV_Z']['setting']
            if df.at[prior_idx[0], 'DVv'] < 0:
                # If DVD-1 virtual is negative, multiply the reduced DVD-1 virtual by 1.02:
                # DVD virtual new = DVD virtual before * 1.02
                # NOTE: I question the -1 and will treat it as wrong
                df.at[prior_idx[0], 'DVv'] = df.at[prior_idx[0], 'DVv'] * 1.02
            else:
                df.at[prior_idx[0], 'DVv'] = df.at[prior_idx[0], 'DVv'] / 1.02

    def step_3(self, df, row_idx, prior_idx):

        if len(row_idx) > 0:
            # Increase DVD virtual each day:
            df.at[row_idx[0], 'DVv'] = df.at[row_idx[0], 'DVv'] + at_calc_params['atp_ModDV_Z']['setting']
            if df.at[prior_idx[0], 'DVv'] < 0:
                # If DVD-1 virtual is negative, divide the increased DVD-1 virtual by 1.02:
                # DVD virtual new = DVD virtual before / 1.02
                # NOTE: I question the -1 and will treat it as wrong
                df.at[prior_idx[0], 'DVv'] = df.at[prior_idx[0], 'DVv'] / 1.02
            else:
                df.at[prior_idx[0], 'DVv'] = df.at[prior_idx[0], 'DVv'] * 1.02

    def day_calculate(self, df, share_num, row_idx, prior_idx, top_up, stage):
        ''' Implementation per Gunther's 210209 Calc Daily Vol Initial Stage.odt
        Daily Vol 2. Make the modified Daily Vol "DV". (To distinguish from the Original Daily Vol let´s name the Original Daily Vol "ODV"):        
        '''
        assert stage == 2, f'{self.name} calculation should only run at stage 2'
        # self.prepare_columns(df)

        if len(row_idx) > 0:
            # do each calculation one day at a time, in sequence
            if (prior_idx is None):
                return
            # If DVD-1 virtual is negative: Check if DVD-1 virtual > - 0,3 * ODVD
            if df.at[prior_idx[0], 'DVv'] < 0:
                if df.at[prior_idx[0], 'DVv'] > -0.3*df.at[prior_idx[0], 'ODV']:
                    self.step_2(df, row_idx, prior_idx)
                else:
                    self.step_3(df, row_idx, prior_idx)
            else:
                if df.at[prior_idx[0], 'DVv'] > df.at[prior_idx[0], 'ODV']:
                    self.step_2(df, row_idx, prior_idx)
                else:
                    self.step_3(df, row_idx, prior_idx)

            # 2c) The modified Daily Vol DVD was: DVD = ODVD + DVD virtual.
            # In case DVD is negative, set DVD = 0 instead, ...
            df.at[row_idx[0], 'DV'] = max(
                df.at[row_idx[0], 'ODV'] + df.at[row_idx[0], 'DVv'], 0)


