from datetime import date
import logging
from numpy.core.numeric import NaN

import pandas as pd
from bsbetl import ov_helpers
from bsbetl.calc_helpers import busdays_offset, last_trading_row_index
from bsbetl.alltable_calcs import Calculation


class _2StPr_PriceHighestSince(Calculation.Calculation):

    def __init__(self):
        super().__init__('PriceHighestSince')
        self.description = 'Price Highest Since calculation'
        self.dependents = ['price', 'volume']
        self.at_computeds = ['DHPbig']
        self.ov_computeds = ['DHPlasthi', 'DHPlast20hi',
                             'DaysDHPlasthi', 'DaysDHPlast20hi' ]

    def calculate(self, df: pd.DataFrame, share_num: str, dates_in_df: list, top_up: bool, stage: int):
        ''' Implementation of section 'Price 2. Find price highest since ...'
            Refer Gunther's document 6 Calc Price 5.odt doc 
        '''

        # tip:
        # print(df.iloc[-1].name)  # gets actual timestamp oflast row
        # print(df.iloc[cur_date_start_row].name) # gets the row's ordinal number

        assert stage == 2, f'{self.name} calculation should only run at stage 2'
        # self.prepare_columns(df)

        DHPlasthi = NaN
        DHPlasthi_stack=[]

        DHPlast3hi = NaN

        DHPlast20hi = NaN
        DHPlast20hi_stack=[]
        DHPlast20hi3perc = NaN

        DHPlasthi3perc = NaN
        DHPlasthi3perc_stack=[]

        DaysDHPlasthi = NaN
        DaysDHPlast20hi = NaN
        DaysDHPlasthi3perc = NaN

        DDHPlasthi = NaN
        DDHPlasthi3perc = NaN
        DDHPlast20hi = NaN

        for cur_date in dates_in_df:
            # should be unecessary since its already been stripped of weekdays
            if cur_date.weekday() >= 5:
                continue
            # this need only be run for the last day in the df
            if len(dates_in_df) > 20:
                days_to_use = 20
            else:
                days_to_use = len(dates_in_df)
            
            if cur_date == dates_in_df[-1] and days_to_use > 1:

                cur_date_ts = df.iloc[-1].name
                # we need 3 and 20 bus days back from cur_date
                back_1_ts = busdays_offset(cur_date_ts, -1)
                back_3_ts = busdays_offset(cur_date_ts, -3)
                back_20_ts = busdays_offset(cur_date_ts, -days_to_use)
                back_100_ts = busdays_offset(cur_date_ts, -100)

                # use the between function to create filter conditions on the index
                last1_busdays_filter = df.index.to_series().between(back_1_ts, cur_date_ts)
                last3_busdays_filter = df.index.to_series().between(back_3_ts, cur_date_ts)
                last20_busdays_filter = df.index.to_series().between(back_20_ts, cur_date_ts)
                last100_busdays_filter = df.index.to_series().between(back_100_ts, cur_date_ts)

                # now we can compute the maxima we need
                DHPlasthi = df[last1_busdays_filter]['price'].max()
                # if share_num == 'A2ASUV.ETR':
                #     print(f'A2ASUV.ETR DHPlasthi={DHPlasthi}')
                DHPlasthi_stack.append(DHPlasthi)

                # compute DHPlast3high3perc
                DHPlasthi3perc = 1.03 * DHPlasthi
                DHPlasthi3perc_stack.append(DHPlasthi3perc)

                DHPlast3hi = df[last3_busdays_filter]['price'].max()


                DHPlast20hi = df[last20_busdays_filter]['price'].max()
                DHPlast20hi3perc = 1.03 * DHPlast20hi
                DHPlast20hi_stack.append(DHPlast20hi)

                # ASSIGN to AllTable these maxima in the day end row
                bot_row_idx = last_trading_row_index(df, cur_date, stage)
                # bot_row_idx is a DatetimeIndex with 0 (if empty) or 1 entry, the datetime of the YYYY-MM-DD 17:35 5-min slot
                #if bot_row_idx.size > 0:
                    # usually we get here, unless the df was truncated and dataframe does not go to the end of day slot 17:35
                    #df.at[bot_row_idx[0], 'DHPlasthi'] = DHPlasthi
                    #df.at[bot_row_idx[0], 'DHPlast20hi'] = DHPlast20hi

                # compute DaysDHPlasthi (number of days back any higher price than DHPlasthi occurred)
                # filter df for prices even higher than DHPlast3hi
                df_highs = df[df['price'] > DHPlasthi]
                if len(df_highs.index) > 0:
                    # get time stamp of the last of those that are 'higher than DHPlast3hi'
                    higher_than_hi1_ts = df_highs.iloc[-1].name
                    # compute
                    DaysDHPlasthi = len(pd.bdate_range(higher_than_hi1_ts, cur_date_ts))
                else:
                    DaysDHPlasthi = 97

                # compute DaysDHPlast20hi
                # filter df for prices even higher than DHPlast20hi
                df_highs = df[df['price'] > DHPlast20hi]
                if len(df_highs.index) > 0:
                    # get time stamp of the last of those that are 'higher than DHPlast3hi'
                    higher_than_hi20_ts = df_highs.iloc[-1].name
                    DaysDHPlast20hi = len(pd.bdate_range(higher_than_hi20_ts, cur_date_ts))
                else:
                    DaysDHPlast20hi = 80


                # filter df for prices even higher than DHPlast3hi3perc
                df_highs = df[df['price'] > DHPlasthi3perc]
                if len(df_highs.index) > 0:
                    # get time stamp of the last of those that are 'higher than DHPlast3high3perc'
                    higher_than_hi = df_highs.iloc[-1].name
                    DaysDHPlasthi3perc = len(pd.bdate_range(higher_than_hi, cur_date_ts))
                else:
                    DaysDHPlasthi3perc = 97

                # DDHPlasthi: Number of days since the DHPlasthigh D was higher than on the last day. 
                dhp_highs = df[df['DHP'] > DHPlasthi]
                if len(dhp_highs.index) > 0:
                    # get time stamp of the last of those that are 'higher than DHPlasthi'
                    higher_than_hi1_ts = dhp_highs.iloc[-1].name
                    # compute
                    DDHPlasthi = len(pd.bdate_range(higher_than_hi1_ts, cur_date_ts))
                else:
                    DDHPlasthi = 97                
                #for this simply add 3%
                DDHPlasthi3perc = 1.03*DDHPlasthi

                # DDHPlast20hi: Number of days since the DHPlast20high D was higher than on the last day. 
                dhp20_highs = df[df['price'] > DHPlast20hi]
                if len(dhp20_highs.index) > 0:
                    # get time stamp of the last of those that are 'higher than DHPlasthi'
                    higher_than_hi1_ts = dhp20_highs.iloc[-1].name
                    # compute
                    DDHPlast20hi = len(pd.bdate_range(higher_than_hi1_ts, cur_date_ts))
                else:
                    DDHPlast20hi = 97                


        # finally, the Overview
        # put these DHP numbers into the Overview for the share
        try:
            ov_helpers.global_ov_update(share_num, 'DHPlasthi', DHPlasthi_stack.pop())
        except IndexError: #pop from empty list we anticipate
            pass

        ov_helpers.global_ov_update(share_num, 'DHPlast3hi', DHPlast3hi)

        try:
            ov_helpers.global_ov_update(share_num, 'DHPlasthi.D-1', DHPlasthi_stack.pop())
        except IndexError: #pop from empty list we anticipate
            pass

        try:
            ov_helpers.global_ov_update(share_num, 'DHPlasthi3perc', DHPlasthi3perc_stack.pop())
        except IndexError: #pop from empty list we anticipate
            pass
        try:
            ov_helpers.global_ov_update(share_num, 'DHPlasthi3perc.D-1', DHPlasthi3perc_stack.pop())
        except IndexError: #pop from empty list we anticipate
            pass

        try:
            ov_helpers.global_ov_update(share_num, 'DHPlast20hi', DHPlast20hi_stack.pop())
        except IndexError: #pop from empty list we anticipate
            pass
        
        ov_helpers.global_ov_update(share_num, 'DHPlast20hi3perc', DHPlast20hi3perc)

        try:
            ov_helpers.global_ov_update(share_num, 'DHPlast20hi.D-1', DHPlast20hi_stack.pop())
        except IndexError: #pop from empty list we anticipate
            pass

        #ov_helpers.global_ov_update(share_num, 'DHPbig', DHPbig)
        ov_helpers.global_ov_update(share_num, 'DaysDHPlasthi', DaysDHPlasthi)
        ov_helpers.global_ov_update(share_num, 'DaysDHPlast20hi', DaysDHPlast20hi)
        ov_helpers.global_ov_update(share_num, 'DaysDHPlasthi3perc', DaysDHPlasthi3perc)

        ov_helpers.global_ov_update(share_num, 'DDHPlasthi', DDHPlasthi)
        ov_helpers.global_ov_update(share_num, 'DDHPlasthi3perc', DDHPlasthi3perc)
        ov_helpers.global_ov_update(share_num, 'DDHPlast20hi', DDHPlast20hi)

        logging.info(f'{self.name} done.')
