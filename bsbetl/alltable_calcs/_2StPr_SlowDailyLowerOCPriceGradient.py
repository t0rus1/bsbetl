from bsbetl import ov_helpers
from numpy.core.numeric import NaN
from pandas.core.indexes.base import Index

import pandas as pd
from bsbetl.alltable_calcs import Calculation
from bsbetl.alltable_calcs.at_params import at_calc_params


class _2StPr_SlowDailyLowerOCPriceGradient(Calculation.Calculation):

    def __init__(self):
        super().__init__('SlowDailyLowerOpenClosePriceGradient')
        self.description = 'Make Slow Daily Lower Open Close Price Gradient'
        self.dependents = ['DLOCP']  # this column we assume exists
        self.at_computeds = ['SDLOCPsl','SDLOCPGrsl','DLOCup']
        self.ov_computeds = ['SDLOCPGrsl','DLOCup']

    def day_calculate(self, df: pd.DataFrame, share_num: str, idx: Index, prior: Index, top_up: bool, stage: int):
        ''' Implementation per Gunther's 210318 
        2. St. Pr. 5.: 
        Make Slow Daily Lower Open Close Price Gradient, SLOCPGr
        Calculates the 'computeds' of single (daily) row of the df 
        '''

        assert stage == 2, f'{self.name} calculation should only run at stage 2'
        # df is assumed daily since stage 2 is asserted

        if prior is None:
            # first row
            df.at[idx[0], 'SDLOCPsl'] = df.at[idx[0], 'DLOCP']
        elif df.at[idx[0], 'DLOCP'] > df.at[prior[0], 'SDLOCPsl']:
            df.at[idx[0], 'SDLOCPsl'] = df.at[prior[0], 'SDLOCPsl'] + 0.01 * (df.at[idx[0], 'DLOCP'] - df.at[prior[0], 'SDLOCPsl'])
        elif df.at[idx[0], 'DLOCP'] <= df.at[prior[0], 'SDLOCPsl']:
            df.at[idx[0], 'SDLOCPsl'] = df.at[prior[0], 'SDLOCPsl'] - 0.1 * (df.at[prior[0], 'SDLOCPsl'] - df.at[idx[0], 'DLOCP'])

    def wrap_up(self, df: pd.DataFrame, share_num: str, dates_in_df: list, top_up: bool, stage: int):
        ''' final, additional (vector) calculations '''

        # Have the Price Gradient of SDLOCPsl D ("SDLOCPGrsl D") in the Ov of the 2. Stage
        df['SDLOCPGrsl'] = df['SDLOCPsl'] / df['SDLOCPsl'].shift(1)
        last_SDLOCPGrsl = df.loc[df.index[-1],'SDLOCPGrsl']

        # and the number of days since when it was < 1 last time ("DLOCup"), 
        # so 2 columns for that.
        # mask_lowgr = df['SDLOCPGrsl'] < 1
        # df_lowgr = df[mask_lowgr]

        dlocup=0
        for idx in reversed(df.index):
            #print(idx, data.loc[idx, 'Even'], data.loc[idx, 'Odd'])
            if df.loc[idx,'SDLOCPGrsl'] < 1:
                dlocup = dlocup + 1
            else:
                break

        # assign DLOCup in the at
        df.loc[df.index[-1],'DLOCup'] = dlocup

        ov_helpers.global_ov_update(share_num, 'DLOCup', dlocup)
        ov_helpers.global_ov_update(share_num, 'SDLOCPGrsl', last_SDLOCPGrsl)


        return        