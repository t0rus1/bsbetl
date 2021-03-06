from bsbetl import g, ov_helpers
import logging
import math
from datetime import date
from numpy.core.numeric import NaN

import pandas as pd
from bsbetl.alltable_calcs import Calculation
from bsbetl.alltable_calcs.at_params import at_calc_params
from bsbetl.calc_helpers import first_trading_row_index, last_days_filter, last_trading_row_index, single_day_condition


class M_DailyHighPrice(Calculation.Calculation):

    def __init__(self):
        super().__init__('DailyHighPrice')
        self.description = 'Daily High Prices calculation'
        self.dependents = ['price', 'volume']
        self.at_computeds = [
            'TO', 'AvMV','ODV','SDT','DT','DT1','DHP', 'DLP', 'DMP', 'DCP', 'DHOCP', 'DLOCP', 'DOP', 'DHPbig', 'DLPsmall', 
        ]
        self.ov_computeds = [
            'DT','DT1','SDT','ODV','AvMV',
            'DHP','DHP.D-1','DHP.D-2','DHP.D-3','DHP.D-4','DHP.D-5','DHP.D-6','DHP.D-7','DHP.D-8','DHP.D-9',
            'DLP','DLOCP',
            'DLOCP.D-1','DLOCP.D-2','DLOCP.D-3',  'DLOCP.D-4','DLOCP.D-5','DLOCP.D-6','DLOCP.D-7','DLOCP.D-8','DLOCP.D-9',
            'DHOCP','DMP',
            'DMP.D-1','DMP.D-2','DMP.D-3',
            'DCP','DOP','DHPbig','DLPsmall',
            'DOP.D-1'
        ]

    def calculate(self, df: pd.DataFrame, share_num: str, dates_in_df: list, top_up: bool, stage: int):
        ''' Implementation of Gunther's DHP calculations (replacing DAP calculations)
        '''

        assert stage == 1, f'{self.name} calculation should only run at stage 1'
        # self.prepare_columns(df) now done at instantiation time

        # can compute this now
        df['TO'] = df['price'] * df['volume']

        # but do these DAP calcs day by day
        last_nz_dap = 0
        dv = dt = dt1 = sdt = odv = dhp = dlp = dmp = dap = 0.00
        dcp = dhocp = dlocp = dop = amv = 0.00
        first_idx = bot = bot_idx = None

        dhp_stack = []
        dlocp_stack = []  # holds prior day columns for the Ov
        dmp_stack = []
        dop_stack = []

        for cur_dt in dates_in_df:
            # should be unecessary since its already been stripped of weekdays
            if cur_dt.weekday() >= 5:
                continue
            single_day = single_day_condition(df, cur_dt)

            # work one day at a time
            day_DF = df[single_day]
            
            dv = day_DF['volume'].sum()
            amv = dv/g.MINUTES_PER_TRADING_DAY 
            
            # place average minute volume in each minute row of the day           
            # this is needed by M_ParticularSumOfMV
            day_DF['AvMV'] = amv
            df.update(day_DF['AvMV'])
            
            #dhp = day_DF[day_DF['volume']>0]['price'].max()
            dhp = day_DF['price'].max()
            dhp_stack.append(dhp)

            dt1 = dhp * dv

            dlp = day_DF['price'].min()

            # sort by volume descending
            day_by_vol_DF = day_DF.sort_values(by='volume', ascending=False)

            day_rows = day_by_vol_DF.shape[0]
            day_zerovol_rows = day_by_vol_DF[day_by_vol_DF['volume'] < 1].shape[0]
            day_withvol_rows = day_rows - day_zerovol_rows
            dap = 0
            # eg 60
            if day_withvol_rows > at_calc_params['atp_dap_min_rows_avg_price']['setting']:
                # there are sufficient non zero volume rows to perform a straight averaging of price
                rows_to_avg = (at_calc_params['atp_dap_perc_rows_avg_price']['setting'] * day_rows) / 100
                rows_to_avg = math.ceil(rows_to_avg)
                dap = day_by_vol_DF.head(rows_to_avg)['price'].mean()
            else:
                # not enough trades - perform a volume weighted average price calc
                day_by_vol_DF['TO'] = day_by_vol_DF['price'] * day_by_vol_DF['volume']
                # eg 15
                rows_to_avg = at_calc_params['atp_dap_rows_vol_wt_price']['setting']
                rows_to_avg = math.ceil(rows_to_avg)
                vol_sum = day_by_vol_DF.head(rows_to_avg)['volume'].sum()

                if vol_sum != 0:
                    dap = day_by_vol_DF.head(rows_to_avg)['TO'].sum()/vol_sum

            if dap > 0:
                last_nz_dap = dap
            # finally update the passed in df's DAP column in the end of day row
            try:
                # DOP... find index of 
                df_dop = day_DF[day_DF['price']>0]
                dop = df_dop.iat[0,0]
                dop_stack.append(dop)
                # DCP
                dcp = df_dop.loc[df_dop.index[-1],'price']
                # DHOCP
                dhocp = max(dop, dcp)
                # DLOCP
                dlocp = min(dop, dcp)
                dlocp_stack.append(dlocp) # push value onto stack
                # SDT
                sdt = dv * dcp
                # DT
                dt = dv * dap

                # DMP
                dmp = (dop+dcp)/2.00
                dmp_stack.append(dmp) # push value onto stack

                bot = last_trading_row_index(df, cur_dt, stage)
                if len(bot) > 0:
                    bot_idx=bot
                    # the rest
                    df.at[bot_idx[0], 'ODV'] = dv
                    df.at[bot_idx[0], 'SDT'] = sdt
                    df.at[bot_idx[0], 'DT'] = dt
                    df.at[bot_idx[0], 'DT1'] = dt1
                    df.at[bot_idx[0], 'DHP'] = dhp
                    df.at[bot_idx[0], 'AvMV'] = amv
                    df.at[bot_idx[0], 'DLP'] = dlp
                    df.at[bot_idx[0], 'DMP'] = dmp
                    df.at[bot_idx[0], 'DCP'] = dcp
                    df.at[bot_idx[0], 'DHOCP'] = dhocp
                    df.at[bot_idx[0], 'DLOCP'] = dlocp
                    df.at[bot_idx[0], 'DOP'] = dop
                else:
                    logging.debug(
                        f"M_DAP(1): Share {share_num}: couldn't locate 17:35 band for date {cur_dt.strftime('%Y-%m-%d')}")

            except IndexError:
                logging.debug(
                    f"M_DAP(2): Share {share_num}: couldn't locate 17:35 band for date {cur_dt.strftime('%Y-%m-%d')}")

        # now in a position to compute DHPbig
        last_100_days = last_days_filter(df, 100)
        dhp_big = df[last_100_days]['DHP'].max()
        dlp_small = df[last_100_days]['DHP'].min()
        if isinstance(bot,pd.DatetimeIndex) and len(bot)==0:
            # NOTE the last day of the data was not the 17:35 slot     
            df.loc[df.index[-1],'DHPbig'] = dhp_big
            df.loc[df.index[-1],'DLPsmall'] = dlp_small
            # plus put the last computed other values into the last 
            # row as well, even though its not a 17:35 slot
            logging.debug(f'Not a full day, assigning slot {df.index[-1]} DAP,ODV,SDT,DT,DHP,DLP,DMP,DCP,DHOCP,DLOCP & DOP...')  
            df.loc[df.index[-1],'ODV'] = dv
            df.loc[df.index[-1],'SDT'] = sdt
            df.loc[df.index[-1],'DT'] = dt
            df.loc[df.index[-1],'DT1'] = dt1
            df.loc[df.index[-1],'DHP'] = dhp
            df.loc[df.index[-1],'AvMV'] = amv
            df.loc[df.index[-1],'DLP'] = dlp
            df.loc[df.index[-1],'DMP'] = dmp
            df.loc[df.index[-1],'DCP'] = dcp
            df.loc[df.index[-1],'DHOCP'] = dhocp
            df.loc[df.index[-1],'DLOCP'] = dlocp
            df.loc[df.index[-1],'DOP'] = dop

        # now for the overview... use last assigned values
        ov_helpers.global_ov_update(share_num, 'DT', dt)
        ov_helpers.global_ov_update(share_num, 'DT1', dt1)
        ov_helpers.global_ov_update(share_num, 'SDT', sdt)
        ov_helpers.global_ov_update(share_num, 'ODV', dv)
        ov_helpers.global_ov_update(share_num, 'AvMV', amv)
        ov_helpers.global_ov_update(share_num, 'DHP', dhp)

        try:
            dhp_stack.pop() # throw away last value (its that which is stored in DHP above)

            ov_helpers.global_ov_update(share_num, 'DHP.D-1', dhp_stack.pop())            
            ov_helpers.global_ov_update(share_num, 'DHP.D-2', dhp_stack.pop())            
            ov_helpers.global_ov_update(share_num, 'DHP.D-3', dhp_stack.pop())            

            ov_helpers.global_ov_update(share_num, 'DHP.D-4', dhp_stack.pop())            
            ov_helpers.global_ov_update(share_num, 'DHP.D-5', dhp_stack.pop())            
            ov_helpers.global_ov_update(share_num, 'DHP.D-6', dhp_stack.pop())            
            ov_helpers.global_ov_update(share_num, 'DHP.D-7', dhp_stack.pop())            
            ov_helpers.global_ov_update(share_num, 'DHP.D-8', dhp_stack.pop())            
            ov_helpers.global_ov_update(share_num, 'DHP.D-9', dhp_stack.pop())            

        except IndexError: #pop from empty list we anticipate
            pass

        ov_helpers.global_ov_update(share_num, 'DLP', dlp)
        
        # DLOCP has additional assoc columns
        ov_helpers.global_ov_update(share_num, 'DLOCP', dlocp)
        try:
            dlocp_stack.pop() # throw away last value (its that which is stored in DLOCP above)
            ov_helpers.global_ov_update(share_num, 'DLOCP.D-1', dlocp_stack.pop())            
            ov_helpers.global_ov_update(share_num, 'DLOCP.D-2', dlocp_stack.pop())            
            ov_helpers.global_ov_update(share_num, 'DLOCP.D-3', dlocp_stack.pop())            
            ov_helpers.global_ov_update(share_num, 'DLOCP.D-4', dmp_stack.pop())            
            ov_helpers.global_ov_update(share_num, 'DLOCP.D-5', dmp_stack.pop())            
            ov_helpers.global_ov_update(share_num, 'DLOCP.D-6', dmp_stack.pop())            
            ov_helpers.global_ov_update(share_num, 'DLOCP.D-7', dmp_stack.pop())            
            ov_helpers.global_ov_update(share_num, 'DLOCP.D-8', dmp_stack.pop())            
            ov_helpers.global_ov_update(share_num, 'DLOCP.D-9', dmp_stack.pop())            
        except IndexError: #pop from empty list we anticipate
            pass

        ov_helpers.global_ov_update(share_num, 'DHOCP', dhocp)
        
        # DMP has additional assoc columns
        ov_helpers.global_ov_update(share_num, 'DMP', dmp)
        try:
            dlocp_stack.pop() # throw away last value (its that which is stored in DLOCP above)
            ov_helpers.global_ov_update(share_num, 'DMP.D-1', dmp_stack.pop())            
            ov_helpers.global_ov_update(share_num, 'DMP.D-2', dmp_stack.pop())            
            ov_helpers.global_ov_update(share_num, 'DMP.D-3', dmp_stack.pop())            
        except IndexError: #pop from empty list we anticipate
            pass


        ov_helpers.global_ov_update(share_num, 'DCP', dcp)
        ov_helpers.global_ov_update(share_num, 'DOP', dop)

        ov_helpers.global_ov_update(share_num, 'DHPbig', dhp_big)
        ov_helpers.global_ov_update(share_num, 'DLPsmall', dlp_small)

        try:
            dop_stack.pop() # throw away last value (its that which is stored in DOP above)
            ov_helpers.global_ov_update(share_num, 'DOP.D-1', dop_stack.pop())
        except IndexError: #pop from empty list we anticipate
            pass
        
        logging.info(f'{self.name} done.')
        