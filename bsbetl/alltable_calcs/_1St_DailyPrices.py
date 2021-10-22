import logging
import math
from datetime import date
import numpy as np
from numpy.core.numeric import NaN

import pandas as pd
from bsbetl import ov_helpers
from bsbetl.ov_helpers import global_ov_update
from bsbetl.alltable_calcs import Calculation
from bsbetl.alltable_calcs.at_params import at_calc_params
from bsbetl.calc_helpers import first_non_zero, last_trading_row_index


class _1St_DailyPrices(Calculation.Calculation):

    def __init__(self):
        super().__init__('DailyPrices1_St')
        self.description = 'Make Slow Daily High Prices'
        self.dependents = ['price', 'DHP', ]
        self.at_computeds = ['SDHP1sh','SDHP1m','SDHP1lo',
                             'SDHPGr1sh','SDHPGr1m','SDHPGr1lo',
                             'SDT1f', 'SDT1sl', 'DTF']
        self.ov_computeds = ['SDHPGr1sh','SDHPGr1m','SDHPGr1lo','SDT1f','DTF']

    def calculate(self, df: pd.DataFrame, share_num: str, dates_in_df: list, top_up: bool, stage: int):
        ''' Implementation of Gunther's 1 210315.odt document
            Daily Prices 1. St.: 1. Make Slow Daily High Prices, SDHP:
        '''

        assert stage == 2, f'{self.name} calculation should only run at stage 2'
        # self.prepare_columns(df)

        prior_idx = None
        cur_idx = None
        DHPD = NaN
        SDHP1sh_prior=NaN

        # Daily Prices 1. St.: 1. Make Slow Daily High Prices, SDHP:

        # compute the rows which follow
        for cur_idx, row in df.iterrows():
            # print(cur_idx)
            if cur_idx == df.index[0]:
                DHPD = df.at[cur_idx,'DHP']
                df.at[cur_idx, 'SDHP1sh',] = DHPD
                df.at[cur_idx, 'SDHP1m',] = DHPD
                df.at[cur_idx, 'SDHP1lo',] = DHPD
                prior_idx = cur_idx
                continue
            #can assume we're not in the first row
            DHPD = df.at[cur_idx,'DHP']
            SDHP1sh_prior = df.at[prior_idx,'SDHP1sh']
            SDHP1m_prior = df.at[prior_idx,'SDHP1m']
            SDHP1lo_prior = df.at[prior_idx,'SDHP1lo']
            # 1a) The one for short term view:
            # Case 1:
            if DHPD >= SDHP1sh_prior:
                df.at[cur_idx,'SDHP1sh'] = SDHP1sh_prior + 0.1 * (DHPD-SDHP1sh_prior)
            # Case 2:
            if DHPD < SDHP1sh_prior:
                df.at[cur_idx,'SDHP1sh'] = SDHP1sh_prior - 0.2 * (SDHP1sh_prior-DHPD)

            # 1b) The one for middle term view (no cases)            
            df.at[cur_idx,'SDHP1m'] = SDHP1m_prior + 0.01 * (DHPD-SDHP1m_prior)

            # 1c) The one for long term view (also no cases)
            df.at[cur_idx,'SDHP1lo'] = SDHP1lo_prior + 0.001 * (DHPD-SDHP1lo_prior)
            prior_idx = cur_idx


        #Daily Prices 1. St.: 2. Make Slow Daily High Prices Gradients, SDHPGr:

        # vector approach to gradient computation
        # 'SDHPGr1sh'
        df['SDHPGr1sh'] = df['SDHP1sh'] / df['SDHP1sh'].shift(1)
        df.loc[~np.isfinite(df['SDHPGr1sh']), 'SDHPGr1sh'] = np.nan
        # patch up NaN values which may arise
        df['SDHPGr1sh'].interpolate(method='pad', limit_direction='forward')

        # 'SDHPGr1m'
        df['SDHPGr1m'] = df['SDHP1m'] / df['SDHP1m'].shift(1)
        df.loc[~np.isfinite(df['SDHPGr1m']), 'SDHPGr1m'] = np.nan
        # patch up NaN values which may arise
        df['SDHPGr1m'].interpolate(method='pad', limit_direction='forward')

        # 'SDHPGr1lo'
        df['SDHPGr1lo'] = df['SDHP1lo'] / df['SDHP1lo'].shift(1)
        df.loc[~np.isfinite(df['SDHPGr1lo']), 'SDHPGr1lo'] = np.nan
        # patch up NaN values which may arise
        df['SDHPGr1lo'].interpolate(method='pad', limit_direction='forward')

        # Daily Prices 1. St.: 3. Make Daily Turnover Figure, DTF:
        # 3a) For an easy approach, take the DHP and the DV to calc the DT1. D: 
        # DT1.D = ODVD * DAPD 
        # 3b) So the Slow Daily Turnovers here are: 
        #     The fast one:
        #     SDT1. f D = SDT1. D-1 + 0.3 * (DT1. D - SDT1. D-1)  
        #     The slow one:	
        #     SDT1. sl D = SDT1. D-1 + 0.03 * (DT1. D - SDT1. D-1)         
        df['SDT1f'] = df['SDT1f'].shift(1) + 0.3 *(df['DT']-df['SDT1f'].shift(1))
        df['SDT1sl'] = df['SDT1f'].shift(1) + 0.03 *(df['DT']-df['SDT1f'].shift(1))

        # 3c) And the DTF:        
        df['DTF'] = df['SDT1f']/df['SDT1sl'].shift(1)


        #carry to the overview (so that 1 St Conditions may be tested)
        # cur_idx assumed to be on the last row
        ov_helpers.global_ov_update(share_num, 'SDHPGr1sh', df.at[cur_idx,'SDHPGr1sh'])
        ov_helpers.global_ov_update(share_num, 'SDHPGr1m', df.at[cur_idx,'SDHPGr1m'])
        ov_helpers.global_ov_update(share_num, 'SDHPGr1lo', df.at[cur_idx,'SDHPGr1lo'])
        ov_helpers.global_ov_update(share_num, 'SDT1f', df.at[cur_idx,'SDT1f'])
        ov_helpers.global_ov_update(share_num, 'SDT1sl', df.at[cur_idx,'SDT1sl'])
        ov_helpers.global_ov_update(share_num, 'DTF', df.at[cur_idx,'DTF'])


        logging.info(f'{self.name} done.')
