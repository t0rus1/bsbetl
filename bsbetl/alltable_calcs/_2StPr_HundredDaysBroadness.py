from datetime import date, datetime, timedelta
import logging

import numpy as np
from numpy.core.numeric import NaN
import pandas as pd

from bsbetl import ov_helpers
from bsbetl.alltable_calcs import Calculation
from bsbetl.calc_helpers import last_trading_row_index


class _2StPr_HundredDaysBroadness(Calculation.Calculation):

    def __init__(self):
        super().__init__('HundredDaysBroadness')
        self.description = 'Hundred Days Broadness calculation'
        self.dependents = ['price']
        self.at_computeds = ['HBF']
        self.ov_computeds = ['HBF']

    def calculate(self, df: pd.DataFrame, share_num: str, dates_in_df: list, top_up: bool, stage: int):
        ''' Implementation of section 'Price 1. Make Hundred days Broadness Figure HBF:'
            Refer Gunther's document 6 Calc Price 6b.odt doc
        '''
        assert stage == 2, f'{self.name} calculation should only run at stage 2'
        # self.prepare_columns(df)

        broadness_for_ov = -1.0
        index_series = df.index.to_series()
        for cur_date in reversed(dates_in_df):
            # cur_dt_str = cur_dt.strftime('%Y-%m-%d')
            # left = cur_dt_str+' 09:00:00'
            # right = cur_dt_str+' 17:35:00'
            # single_day_condition = df.index.to_series().between(left, right)
            cur_date_dt = datetime.strptime(cur_date.strftime(
                '%Y-%m-%d 17:35:00'), '%Y-%m-%d 17:35:00')

            # compute broadness over last 100 days
            hundred_back_dt = cur_date_dt - timedelta(days=100)
            hundred_day_condition = index_series.between(
                hundred_back_dt, cur_date_dt)

            price_max = df[hundred_day_condition]['price'].max()
            price_min = df[hundred_day_condition]['price'].min()
            broadness = price_max/price_min if price_min > 0 else 0.00

            # assign the broadness to the cur_dt row
            try:
                botrow_idx = last_trading_row_index(df, cur_date, stage)
                # <-- here we change df
                df.at[botrow_idx[0], 'HBF'] = broadness
                # capture the first broadness (the latest day since we're iterating in reverse)
                if broadness_for_ov < 0:
                    broadness_for_ov = broadness
            except IndexError:
                logging.debug(
                    f"at_HBF: Share {share_num}: couldn't locate 17:35 band on {cur_date.strftime('%Y-%m-%d')}. Was the download done too early on that day?")

        # now for the overview
        if broadness_for_ov > 0:
            ov_helpers.global_ov_update(share_num, 'HBF', broadness_for_ov)

        logging.info(f'{self.name} done.')
