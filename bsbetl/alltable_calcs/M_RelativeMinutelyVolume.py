import logging
from math import inf
import pandas as pd
from bsbetl.alltable_calcs import Calculation
from bsbetl.alltable_calcs.at_params import at_calc_params
from bsbetl.calc_helpers import (n_days_back_filter, n_days_forward_filter, single_day_condition)
from bsbetl.ov_helpers import global_ov_update


class M_RelativeMinutelyVolume(Calculation.Calculation):

    def __init__(self):
        super().__init__('RelativeMinutelyVolume')
        self.description = 'Relative Minutely Volume'
        self.dependents = ['volume',]
        self.at_computeds = ['SMVms','RMVms','SMPGrmsbig', 'MSmp', 'MSmpv', 'MSmv', ]
        self.ov_computeds = ['MSmp','MSmpv', 'MSmv',]

    def calculate(self, df: pd.DataFrame, share_num: str, dates_in_df: list, top_up: bool, stage: int):
        ''' Module MS 3: Calc the Relative Minutely Volume RMVMS: 
        '''
        assert stage == 1, f'{self.name} calculation should only run at stage 1'

        #logging.debug(f"dates_in_df[-3]={dates_in_df[-3]}")

        d3_df = df[n_days_forward_filter(df, dates_in_df[-3], 3)]

        # 3 day period
        _3d_trades_df = d3_df[d3_df['volume'] > 0]
        num_trading_rows = len(_3d_trades_df)
        total_3_day_volume = _3d_trades_df['volume'].sum()

        # Calc the average vol (avMVMS) per (vol-not-zero-) minute:
        avMVms = total_3_day_volume/num_trading_rows

        # 3b) Now the Slow Minutely Vol, SMVMS M. (just last 3 days)
        for cur_dt in dates_in_df[-3:]: 
            # should be unecessary since its already been stripped of weekdays
            if cur_dt.weekday() >= 5:
                continue
            single_day_mask = single_day_condition(df, cur_dt)
            # work one day at a time
            day_df = df[single_day_mask]
            # by the minute
            prior_index=0
            for index,row in day_df.iterrows():
                MVm = row['volume']
                SMV_prior = MVm if prior_index == 0 else df.loc[prior_index,'SMVms']
                if MVm < SMV_prior:
                    SMVms = SMV_prior - 0.00064*num_trading_rows*(SMV_prior-MVm)
                else:
                    SMVms = SMV_prior + 0.3 * (MVm-SMV_prior)
                df.loc[index,'SMVms'] = SMVms

                # 3c) Finally to get the RMVMS: Only of Rows were the MV (so the actual Minutely Volume) is not zero (means where real trades took place), take the SMVMS M and calc the RMVMS M:
                # 	RMVMS M = SMVMS M / avMVMS M 
                if MVm > 0:
                    df.loc[index,'RMVms'] = SMVms / avMVms
                else:
                    df.loc[index,'RMVms'] = 0
                    
                prior_index = index

        # compute some totals we need for 4) below:
        SmpGr_Vol_df = d3_df[d3_df['SMPGrmsf'] >= 1] 
        SmpGr_Vol_df = SmpGr_Vol_df[SmpGr_Vol_df['volume'] > 0]
        num_trading_rows = len(SmpGr_Vol_df)

        if num_trading_rows >= at_calc_params['atp_RMV_TrRowsGr_threshold']['setting']: # 16
            # Take the SMPGrMS f of each such row, sum them up and divide them by their number: 
            # SMPGrMS cØ = ∑SMPGrMS f / TrRowsGrD-1 ... D-3                 
            SMPGrmsc0 = SmpGr_Vol_df['SMPGrmsf'].sum()/num_trading_rows
        else:
            SMPGrmsc0 = at_calc_params['atp_SMPGr_threshold']['setting'] # 1.01

        # vector assign first (SMPGrmsbig needed below)
        # refer M_SpecialSlowMinutePrices
        df['SMPGrmsbig'] = df[['SMPGrmsf','SMPGrmsm','SMPGrmssl','SMPGrmsb']].max(axis=1)

        # by the minute 
        mask=(_3d_trades_df['SMPGrmsf'] >= 1) | (_3d_trades_df['SMPGrmsm'] >= 1) | (_3d_trades_df['SMPGrmssl'] >= 1) | (_3d_trades_df['SMPGrmsb'] >= 1) 
        gr_df = _3d_trades_df[mask]
        MSmp=0
        MSmpv=0
        MSmv=0
        #logging.debug(f"Assigning MSmp,MSmpv,MSmv over {len(gr_df)} rows")

        for index,row in gr_df.iterrows():
            print(row.name)
            if SMPGrmsc0 > 0:
                RMVms = df.loc[index,'RMVms']
                RSMPGrms = df.loc[index,'SMPGrmsbig']/SMPGrmsc0
                if RSMPGrms >= 1:
                    #For MSM P: 	eMSP = 1   and 	eMSV = 0.5 
                    eMSP = at_calc_params['atp_eMSP_price']['setting'] # 1
                    eMSV = at_calc_params['atp_eMSV_price']['setting'] # 0.5
                    MSmp = (200*(RSMPGrms - 1))**eMSP * (RMVms**eMSV)
                    df.loc[index,'MSmp'] = MSmp

                    eMSP = at_calc_params['atp_eMSP_pr_vol']['setting'] # 0.8
                    eMSV = at_calc_params['atp_eMSV_pr_vol']['setting'] # 0.8
                    MSmpv = (200*(RSMPGrms - 1))**eMSP * (RMVms**eMSV)
                    df.loc[index,'MSmpv'] = MSmpv

                    eMSP = at_calc_params['atp_eMSP_vol']['setting'] # 0.5
                    eMSV = at_calc_params['atp_eMSV_vol']['setting'] # 1
                    MSmv = (200*(RSMPGrms - 1))**eMSP * (RMVms**eMSV) 
                    df.loc[index,'MSmv'] = MSmv
                    logging.debug(f"row {index}: RSMPGrms={RSMPGrms}, MSmp={MSmp}, MSmpv={MSmpv}, MSmv={MSmv}; rmvms={RMVms}; SMPGrmsc0 = {SMPGrmsc0}")
                else:
                    df.loc[index,'MSmp'] = 0
                    df.loc[index,'MSmpv'] = 0
                    df.loc[index,'MSmv'] = 0
                    logging.debug(f"row {index}: MSmp, MSmpv, MSmv all set 0 (RSMPGrms={RSMPGrms} = SMPGrmsbig/SMPGrmsc0 => {df.loc[index,'SMPGrmsbig']}/{SMPGrmsc0})")
            else:
                df.loc[index,'MSmp'] = 0
                df.loc[index,'MSmpv'] = 0
                df.loc[index,'MSmv'] = 0
                logging.debug(f"row {index}: MSmp=0, MSmpv=0, MSmv=0; rmvms=0; SMPGrmsc0 = {SMPGrmsc0}")

        # do ov 
        global_ov_update(share_num, 'MSmp', MSmp)
        global_ov_update(share_num, 'MSmpv', MSmpv)
        global_ov_update(share_num, 'MSmv', MSmv)

        logging.info(f'{self.name} done.')
