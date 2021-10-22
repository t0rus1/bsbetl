import logging
import math
from datetime import date
import numpy as np
from numpy.core.numeric import NaN

import pandas as pd
from bsbetl.ov_helpers import global_ov_update
from bsbetl.alltable_calcs import Calculation
from bsbetl.alltable_calcs.at_params import at_calc_params
from bsbetl.calc_helpers import first_non_zero, last_trading_row_index


class _2StPr_AvgOfDailyHighPriceGradient(Calculation.Calculation):

    def __init__(self):
        super().__init__('AvgOfDailyHighPriceGradient')
        self.description = 'Average of Daily High Price Gradient calculation'
        self.dependents = ['price', 'DHP', ]
        self.at_computeds = ['DHPGr', 'DHPGrAvSh',
                             'DHPGrAvMi', 'DHPGrAvLo', 'DHPGrDiSl', 'DHPGrDiF']
        self.ov_computeds = ['DHPGr', 'DHPGrAvSh',
                             'DHPGrAvMi', 'DHPGrAvLo', 'DHPGrDiSl', 'DHPGrDiF', 'DHPGrDiF.D-1', 'pnt1_DHPGrDiF', 'pnt3_DHPGrDiF']

    def calculate(self, df: pd.DataFrame, share_num: str, dates_in_df: list, top_up: bool, stage: int):
        ''' 
        2. St. Pr. 4.: 
        Find the Average of the Daily Average Price Gradient,  
        "DHPGrAv" and the Distances from it, "DHPGrDi":        
        '''

        assert stage == 2, f'{self.name} calculation should only run at stage 2'
        # self.prepare_columns(df)

        # vector way of calculating DHPgr for entire column
        df['DHPGr'] = df['DHP'] / df['DHP'].shift(1)
        df.loc[~np.isfinite(df['DHPGr']), 'DHPGr'] = 1.
        # patch up NaN values which may arise
        df['DHPGr'].interpolate(method='linear', limit_direction='forward')

        prior_idx = None
        cur_idx = None
        DHPGrAvSh = 1.00
        DHPGrAvSh_stack = []
        DHPGrAvMi = 1.00
        DHPGrAvLo = 1.00

        DHPGrDiSl = 0.00
        DHPGrDiSl_stack = []

        DHPGrDiF = 0.00

        # compute the rows which follow
        for cur_idx, row in df.iterrows():
            # print(cur_idx)
            if cur_idx == df.index[0]:
                # 4a) The initial DHPGrAvD is  1.
                df.at[cur_idx, 'DHPGrAvSh'] = 1.00
                df.at[cur_idx, 'DHPGrAvMi'] = 1.00
                df.at[cur_idx, 'DHPGrAvLo'] = 1.00
                # distances
                df.at[cur_idx, 'DHPGrDiSl'] = 0.00
                df.at[cur_idx, 'DHPGrDiF'] = 0.00
                prior_idx = cur_idx
                continue
            # DHPGrAvx D = DHPGrAvx D-1 + Yx DHPGrAv * (DHPGrD - DHPGrAvx D-1)
            # short term
            DHPGrAvSh = df.at[prior_idx, 'DHPGrAvSh'] + \
                at_calc_params['atp_YshDHPGrAv']['setting'] * \
                (df.at[cur_idx, 'DHPGr'] - df.at[prior_idx, 'DHPGrAvSh'])

            DHPGrAvSh_stack.append(DHPGrAvSh) # need to be able to access D-1 and D-2 values

            # middle term
            DHPGrAvMi = df.at[prior_idx, 'DHPGrAvMi'] + \
                at_calc_params['atp_YmiDHPGrAv']['setting'] * \
                (df.at[cur_idx, 'DHPGr'] - df.at[prior_idx, 'DHPGrAvMi'])
            # long term
            DHPGrAvLo = df.at[prior_idx, 'DHPGrAvLo'] + \
                at_calc_params['atp_YloDHPGrAv']['setting'] * \
                (df.at[cur_idx, 'DHPGr'] - df.at[prior_idx, 'DHPGrAvLo'])

            # 4b) limit maximum values
            df.at[cur_idx, 'DHPGrAvSh'] = min(DHPGrAvSh, 1.03)
            df.at[cur_idx, 'DHPGrAvMi'] = min(DHPGrAvMi, 1.03)
            df.at[cur_idx, 'DHPGrAvLo'] = min(DHPGrAvLo, 1.03)
            # limit minimum values
            df.at[cur_idx, 'DHPGrAvSh'] = max(DHPGrAvSh, 0.97)
            df.at[cur_idx, 'DHPGrAvMi'] = max(DHPGrAvMi, 0.97)
            df.at[cur_idx, 'DHPGrAvLo'] = max(DHPGrAvLo, 0.97)

            # 4c) DAPGrDi
            # The slow one:
            DHPGrDiSl = 0.9 * df.at[prior_idx, 'DHPGrDiSl'] + \
                math.fabs(df.at[cur_idx, 'DHPGr'] -
                          df.at[cur_idx, 'DHPGrAvLo'])

            DHPGrDiSl_stack.append(DHPGrDiSl) # we need to be able to access D-1

            df.at[cur_idx, 'DHPGrDiSl'] = DHPGrDiSl
            # The fast
            DHPGrDiF = 0.7 * df.at[prior_idx, 'DHPGrDiF'] + \
                math.fabs(df.at[cur_idx, 'DHPGr'] -
                          df.at[cur_idx, 'DHPGrAvSh'])
            df.at[cur_idx, 'DHPGrDiF'] = DHPGrDiF

            prior_idx = cur_idx


        try:
            global_ov_update(share_num, 'DHPGrAvSh', DHPGrAvSh)
            DHPGrAvSh_stack.pop() # discard last one
            global_ov_update(share_num, 'DHPGrAvSh.D-1', DHPGrAvSh_stack.pop())
            global_ov_update(share_num, 'DHPGrAvSh.D-2', DHPGrAvSh_stack.pop())


            global_ov_update(share_num, 'DHPGrAvMi', DHPGrAvMi)
            global_ov_update(share_num, 'DHPGrAvLo', DHPGrAvLo)

            global_ov_update(share_num, 'DHPGrDiSl', DHPGrDiSl)
            DHPGrDiSl_stack.pop()
            global_ov_update(share_num, 'DHPGrDiSl.D-1', DHPGrDiSl_stack.pop())
            
            # we need DAPGrDiF.D-1 also in the Ov
            global_ov_update(share_num, 'DHPGrDiF', DHPGrDiF)
            global_ov_update(share_num, 'DHPGrDiF.D-1',df.loc[df.index[-2],'DHPGrDiF'])

            global_ov_update(share_num, 'DHPGr',df.loc[df.index[-1],'DHPGr'])

            global_ov_update(share_num, 'pnt1_DHPGrDiF', 0.1*DHPGrDiF)
            global_ov_update(share_num, 'pnt3_DHPGrDiF', 0.3*DHPGrDiF)
        except IndexError as exc:
            logging.error(f'_2StPr_AvgOfDailyHighPriceGradient exception {exc}')

        logging.info(f'{self.name} done.')
