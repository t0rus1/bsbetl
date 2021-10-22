import logging
import math
from time import process_time
from datetime import date
from numpy.core.numeric import Infinity, NaN

import pandas as pd
from bsbetl.alltable_calcs import Calculation
from bsbetl.alltable_calcs.at_params import at_calc_params
from bsbetl.calc_helpers import first_trading_row_index, last_days_filter, last_trading_row_index, single_day_condition
from bsbetl import ov_helpers


class M_ParticularSumOfMV(Calculation.Calculation):

    def __init__(self):
        super().__init__('ParticularSumOfMV')
        self.description = 'Particular Sum of Minute Volume'
        self.dependents = ['volume','AvMV']
        self.at_computeds = ['PSMV','CV1','RCV1','MVm','AvMVdec']
        self.ov_computeds = ['PSMV','CV1','CV1.D-1','CV1.D-2','CV1.D-3','CV1.D-4','CV1.D-5','RCV1','RCV1.D-1','RCV1.D-2','RCV1.D-3','RCV1.D-4','RCV1.D-5','AvMVdec']

    # def decline_PSMV(self, row, **kwargs):
    #     ''' gets called for every row by an apply function'''

    #     df = kwargs['df']
    #     psmv_colnum = kwargs['psmv_colnum'] 
    #     volume_colnum = kwargs['volume_colnum'] 
    #     df_index_list=kwargs['df_index_list']

    #     try:
    #         row_ordinal = df_index_list.index(row.name)
    #         prior_ordinal = row_ordinal-1

    #         if prior_ordinal >= 0:
    #             # Step 1: Decline the PSMVCV1 M by 0.97:
    #             # PSMVCV1 M = 0.97 * PSMVCV1 M-1 
    #             df.iat[row_ordinal,psmv_colnum] = 0.97*df.iat[prior_ordinal,volume_colnum]
    #             # Step 2: Add the vol of the next minute (MVM after):
    #             # PSMVCV1 M = PSMVCV1 M-1 + MVM after
    #             df.iat[row_ordinal,psmv_colnum] = df.iat[prior_ordinal,psmv_colnum] + row['MVm']
    #     except ValueError as exc:
    #         logging.warn(f"{exc}\n row name='{row.name}'")

    #     return row

    def calculate(self, df: pd.DataFrame, share_num: str, dates_in_df: list, top_up: bool, stage: int):
        ''' Module CV1 2: Calc the Particular Sum of MV, PSMVCV1 M:
            Module CV1 3: Calc the Cluster Vol of the day D, CV1D :
        '''

        assert stage == 1, f'{self.name} calculation should only run at stage 1'

        # 'AvMV' assumed already computed in M_DailyHighPrice.py

        cv1=0
        cv1_stack=[]
        rcv1=0
        rcv1_stack=[]
        bot_idx=None
        MVm_colnum =  df.columns.get_loc('MVm')
        PSMV_colnum = df.columns.get_loc('PSMV')
        #VOL_colnum = df.columns.get_loc('volume')
        #df_index_list=df.index.tolist()

        # 2a1) Decline every MV which is not zero by AvMVD:
        # MVM before -  AvMVD = MVM after 
        df['MVm'] = df['volume']-df['AvMV']
        # zero the negative ones
        df['MVm'][df['MVm'] < 0]=0

        # compute PSMV NOTE takes 40 seconds per share !!!
        # df.apply(lambda row: self.decline_PSMV(row,df=df, psmv_colnum=PSMV_colnum, volume_colnum=VOL_colnum, df_index_list=df_index_list), axis=1)

        # Step 1: Decline the PSMVCV1 M by 0.97:
        # PSMVCV1 M = 0.97 * PSMVCV1 M-1 
        df['PSMV'] = 0.97*df['PSMV'].shift(1,fill_value=df.iat[0,PSMV_colnum])
        # Step 2: Add the vol of the next minute (MVM after):
        # PSMVCV1 M = PSMVCV1 M-1 + MVM after
        df['PSMV'] = df['PSMV'].shift(1,fill_value=df.iat[0,PSMV_colnum]) + df['MVm'].shift(-1,fill_value=0)

        for cur_dt in dates_in_df:

            # should be unecessary since its already been stripped of weekdays
            if cur_dt.weekday() >= 5:
                continue
            single_day = single_day_condition(df, cur_dt)
            # work one day at a time
            day_DF = df[single_day]

            # at this point every MVm and PSMV has been computed (above)
            # Module CV1 3: Calc the Cluster Vol of the day D, CV1D :
            # CV1 = PSMVWb1 biggest  / AvMV 

            # Now again calc an Average Minute Vol, AvMVdec on day D (AvMVdec D): 
            AvMVdecD = day_DF['MVm'].mean()
            # this value needs to be in every row
            df['AvMVdec'][single_day] = AvMVdecD
            
            psmv_biggest = day_DF['PSMV'].max(axis=0)
            psmv_last = day_DF.iloc[-1,PSMV_colnum]

            # end of day assignments of CV1 and RCV1
            # CV1 = PSMVWb1 biggest  / AvMV 
            cv1 = psmv_biggest/AvMVdecD

            # convoluted way to safely obtain sensible prior_cv1
            try:
                prior_cv1=cv1 # init
                if len(cv1_stack)>0:
                    # prior_cv1=cv1_stack.pop()
                    # cv1_stack.append(prior_cv1)
                    prior_cv1=cv1_stack[-1]

            except IndexError as exc:
                logging.error(f'M_ParticularSumOfMV exception {exc}')

            cv1_stack.append(cv1) # save this cv1 for recall below
            rcv1=0
            if prior_cv1 != 0:
                rcv1 = cv1/prior_cv1
            rcv1_stack.append(rcv1) # save this rcv1 for recall below

            bot_idx = last_trading_row_index(df, cur_dt, stage)
            if len(bot_idx) > 0:
                # this ought to be the 17:35 slot
                #print(f"assigning cv1 {cv1} and rcv1 {rcv1} to row {bot_idx}")
                df.loc[bot_idx,'CV1'] = cv1
                df.loc[bot_idx,'RCV1'] = rcv1
                #df.loc[bot_idx,'AvMVdec'] = AvMVdecD
            else:
                logging.debug(f"M_PSMV: Share {share_num}: couldn't locate 17:35 band for date {cur_dt.strftime('%Y-%m-%d')}")

        # NOTE check if the very last day of the data was not the 17:35 slot     
        if isinstance(bot_idx,pd.DatetimeIndex) and len(bot_idx)==0:
            # put the last computed values into the last 
            # row, even though its not a 17:35 slot
            df.loc[df.index[-1],'CV1'] = cv1
            df.loc[df.index[-1],'RCV1'] = rcv1
            #df.loc[df.index[-1],'AvMVdec'] = rcv1

        # now for the overview... use last assigned values
        ov_helpers.global_ov_update(share_num, 'PSMV', psmv_last)
        ov_helpers.global_ov_update(share_num, 'CV1', cv1)
        ov_helpers.global_ov_update(share_num, 'RCV1', rcv1)


        # now assign CV1.D-1 thru D-5
        try:
            _ = cv1_stack.pop() # discard last one since its already stored as 'CV1'
            CV1s = ['CV1.D-1','CV1.D-2','CV1.D-3','CV1.D-4','CV1.D-5',]
            for entry in CV1s:
                cv1=cv1_stack.pop()
                ov_helpers.global_ov_update(share_num, entry, cv1)

            _ = rcv1_stack.pop() # discard "    "    "    "
            # assign RCV1.D-1 ..etc
            RCV1s = ['RCV1.D-1','RCV1.D-2','RCV1.D-3','RCV1.D-4','RCV1.D-5',]

            smallest_rcv1 = math.inf
            for entry in RCV1s:
                rcv1=rcv1_stack.pop()
                ov_helpers.global_ov_update(share_num, entry, rcv1)
                # also grab the smallest rcv1 while assigning
                if rcv1 < smallest_rcv1:
                    smallest_rcv1 = rcv1
        except IndexError as exc:
            logging.error(f'M_ParticularSumOfMV exception {exc}')
        #assign smallest
        ov_helpers.global_ov_update(share_num, 'RCV1small', smallest_rcv1)
        
        logging.info(f'{self.name} done.')
