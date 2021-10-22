import logging
from bsbetl import ov_helpers
from numpy.core.numeric import NaN
from pandas.core.indexes.base import Index

import pandas as pd
from bsbetl.alltable_calcs import Calculation
from bsbetl.alltable_calcs.at_params import at_calc_params


class _2StPr_SlowBroadness(Calculation.Calculation):

    def __init__(self):
        super().__init__('SlowBroadness')
        self.description = 'Slow Broadness'
        self.dependents = []  # this column we assume exists
        self.at_computeds = ['SDLOCPBr','SDHP','SBr']
        self.ov_computeds = ['SBr']

    def calculate(self, df: pd.DataFrame, share_num: str, dates_in_df: list, top_up: bool, stage: int):
        ''' Implementation per Gunther's 210321 
        2. St. Pr. 6.: Calc Slow Broadness SBr:        
        Calculates the 'computeds' of single (daily) row of the df 
        '''

        assert stage == 2, f'{self.name} calculation should only run at stage 2'
        # df is assumed daily since stage 2 is asserted

        #Lets begin with the SDLOCP:
        df['SDLOCPBr'] = df['SDLOCPBr'].shift(1) + 0.4 * (df['DLOCP'] - df['SDLOCPBr'].shift(1))

        #SDHP
        prior_index = 0
        for row_index, row in df.iterrows():
            if prior_index != 0:
                # not on the first loop, so prior_row_index is good
                if df.at[prior_index, 'SDHP'] < df.at[row_index,'DHP']:
                    df.at[row_index,'SDHP'] = df.at[prior_index,'SDHP'] + 0.5* (df.at[row_index,'DHP']-df.at[prior_index,'SDHP'])
                if df.at[prior_index, 'SDHP'] > df.at[row_index,'DHP']:
                    df.at[row_index,'SDHP'] = df.at[prior_index,'SDHP'] - 0.2* (df.at[prior_index,'SDHP']-df.at[row_index,'DHP'])
            prior_index = row_index

        #SBr
        #So the SBr is:
        #SBrD = SDHPD / SDLOCPBr D 
        df['SBr'] = df['SDHP']/df['SDLOCPBr']

        # NOTE we now do the overview differently
        # now for the overview... use last assigned values
        sdhp = df.at[prior_index,'SDHP']
        sbr = df.at[prior_index,'SBr']
        ov_helpers.global_ov_update(share_num, 'SDHP', sdhp)
        
        # SBr
        ov_helpers.global_ov_update(share_num, 'SBr', sbr)
        # prior day values also needed in the Ov
        try:
            ov_helpers.global_ov_update(share_num, 'SBr.D-1', df.loc[df.index[-2],'SBr'])
            ov_helpers.global_ov_update(share_num, 'SBr.D-2', df.loc[df.index[-3],'SBr'])
            ov_helpers.global_ov_update(share_num, 'SBr.D-3', df.loc[df.index[-4],'SBr'])
            ov_helpers.global_ov_update(share_num, 'SBr.D-4', df.loc[df.index[-5],'SBr'])
            ov_helpers.global_ov_update(share_num, 'SBr.D-5', df.loc[df.index[-6],'SBr'])
        except IndexError as exc:
            pass

        logging.info(f'{self.name} done.')


        