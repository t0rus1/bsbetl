import logging
import pandas as pd
from bsbetl.alltable_calcs import Calculation
from bsbetl.alltable_calcs.at_params import at_calc_params
from bsbetl.calc_helpers import (single_day_condition)


class M_SpecialSlowMinutePrices(Calculation.Calculation):

    def __init__(self):
        super().__init__('SpecialSlowMinutePrices')
        self.description = 'Special Slow Minute Prices'
        self.dependents = ['price',]
        self.at_computeds = ['SMPmsf','SMPmsm','SMPmssl','SMPmsb', 'SMPGrmsf', 'SMPGrmsm', 'SMPGrmssl', 'SMPGrmsb',]
        self.ov_computeds = []

    def calculate(self, df: pd.DataFrame, share_num: str, dates_in_df: list, top_up: bool, stage: int):
        ''' Module MS 1: Calc special Slow Minute Prices, SMPMS: 
        '''

        assert stage == 1, f'{self.name} calculation should only run at stage 1'

        #1a) Beginning from day 3 (D-3) before the last day.
        day_num=0
        for cur_dt in dates_in_df[-4:]: # gunther seems to want 4 days
            # should be unecessary since its already been stripped of weekdays
            if cur_dt.weekday() >= 5:
                continue
            single_day = single_day_condition(df, cur_dt)
            # work one day at a time
            day_DF = df[single_day]
            # by the minute
            prior_index=0
            for index,row in day_DF.iterrows():
                # same approach for each of the 3 slow minute prices
                MPm = row['price']
                for SMP in [('SMPmsf',at_calc_params['atp_SMP_Ymsf']['setting']),('SMPmsm',at_calc_params['atp_SMP_Ymsm']['setting']),('SMPmssl',at_calc_params['atp_SMP_Ymssl']['setting'])]:
                    SMP_prior = MPm if prior_index == 0 else df.loc[prior_index,SMP[0]]
                    #Case 1:
                    if MPm < SMP_prior:
                        eMSP = 0.01 / (1-(MPm/SMP_prior))
                        df.loc[index,SMP[0]] = SMP_prior - (0.05**eMSP)*(SMP_prior-MPm)
                    #Case 2:
                    if MPm >= SMP_prior:
                        df.loc[index,SMP[0]] = SMP_prior + SMP[1] * (SMP_prior-MPm)

                # if day_num==0:
                #     print(f"row.name={row.name}, index={index}, row['price']={row['price']}, SMP_prior={SMP_prior}")

                prior_index=index
            day_num = day_num+1
        
        # 1c) Now we calc a fourth SMP, a backwards one, SMPMS b M. 
        # This SMP is using the same (fast) YMS f as before and is starting from 
        # the last minute (so on day D at minute M (= Mlast)), but calced only 
        # until minute M-600 (that´s on day D-1).

        SMPmsb_loc = df.columns.get_loc('SMPmsb')
        max_row_idx = len(df) - 1 # for using integer positioning
        # go in reverse order from max to 0
        for i in range(max_row_idx, -1, -1):
            if i >= 1:
                MPm = df.iloc[i]['price']
                MPm_prior = df.iloc[i-1]['price']
                if MPm_prior <= MPm:
                    df.iat[i-1,SMPmsb_loc] = MPm - at_calc_params['atp_SMP_Ymsf']['setting'] * (MPm - MPm_prior)
                if MPm_prior > MPm:
                    eMSP = 0.01 / (1-(MPm/MPm_prior))
                    df.iat[i-1,SMPmsb_loc] = MPm + (0.05**eMSP)*(MPm_prior-MPm)


        # use vector operation to compute 4 gradients
        df['SMPGrmsf'] = df['SMPmsf']/df['SMPmsf'].shift(1)
        df['SMPGrmsm'] = df['SMPmsm']/df['SMPmsm'].shift(1)
        df['SMPGrmssl'] = df['SMPmssl']/df['SMPmssl'].shift(1)
        df['SMPGrmsb'] = df['SMPmsb']/df['SMPmsb'].shift(1)

        # do ov 
        # ov_helpers.global_ov_update(share_num, 'bSDV', df.iat[max_row_idx, bSDV_col_idx])

        logging.info(f'{self.name} done.')
