from bsbetl import ov_helpers
import logging
import math
from datetime import date
from numpy.core.numeric import NaN

import pandas as pd
from bsbetl.alltable_calcs import Calculation
from bsbetl.alltable_calcs.at_params import at_calc_params
from bsbetl.calc_helpers import first_non_zero, last_trading_row_index


class D_BackwardsSlowDailyVol(Calculation.Calculation):

    def __init__(self):
        super().__init__('BackwardsSlowDailyVol')
        self.description = 'Backwards Slow Daily Volume'
        self.dependents = ['DV']
        self.at_computeds = ['bSDV','RbSDV',]
        self.ov_computeds = ['bSDV','RbSDV.D-4','RbSDV.D-7']  

    def calculate(self, df: pd.DataFrame, share_num: str, dates_in_df: list, top_up: bool, stage: int):
        ''' Implementation of Gunther's Make backwards Slow Daily Vol, bSDV: 
            See 3 Vol up few days 210315.odt
        '''
        assert stage == 2, f'{self.name} calculation should only run at stage 2'

        # Loop through rows of dataframe by index 
        # in REVERSE i.e. from last row to row at 0th index.
        DV_col_index = df.columns.get_loc('DV')
        bSDV_col_idx = df.columns.get_loc('bSDV')
        RbSDV_col_idx = df.columns.get_loc('RbSDV')

        max_row_idx = df.shape[0] - 1
        for i in range(max_row_idx, -1, -1):
            if i >= 1:
                if df.iloc[i]['DV'] < df.iloc[i-1]['DV']:
                    df.iat[i-1,bSDV_col_idx] = df.iloc[i]['DV'] + 0.3 * (df.iloc[i-1]['DV'] - df.iloc[i]['DV'])
                else:
                    df.iat[i-1,bSDV_col_idx] = df.iloc[i]['DV'] - 0.2 * (df.iloc[i]['DV'] - df.iloc[i-1]['DV'])

            if i == max_row_idx-4:
                df.iat[i,RbSDV_col_idx] = 1.5 * (df.iloc[i+4]['DV'] + df.iloc[i+3]['DV'])/(df.iloc[i+2]['bSDV'] + df.iloc[i+1]['bSDV'] + df.iloc[i]['bSDV'])

            if i == max_row_idx-7:
                df.iat[i,RbSDV_col_idx] = 1.5 * (df.iloc[i+3]['DV'] + df.iloc[i+2]['DV'])/(df.iloc[i+1]['bSDV'] + df.iloc[i]['bSDV'])

        # also populate max_row_index (which got skipped above)
        # The chain starts with the last day, so it´s day D. As starting bSDVD we take DVD. 
        df.iat[max_row_idx,bSDV_col_idx] = df.iloc[max_row_idx]['DV']

        # do ov 
        ov_helpers.global_ov_update(share_num, 'bSDV', df.iat[max_row_idx, bSDV_col_idx])
        ov_helpers.global_ov_update(share_num, 'RbSDV', df.iat[max_row_idx, RbSDV_col_idx])

        try:
            ov_helpers.global_ov_update(share_num, 'RbSDV.D-4', df.iat[max_row_idx-4, RbSDV_col_idx])
            ov_helpers.global_ov_update(share_num, 'RbSDV.D-7', df.iat[max_row_idx-7, RbSDV_col_idx])
        except IndexError as exc:
            logging.warn(f'BackwardsSlowDailyVol exception {exc} when updating RbSDV.D-4 and/or RbSDV.D-7')

        logging.info(f'{self.name} done.')
