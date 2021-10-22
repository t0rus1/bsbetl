import logging

import pandas as pd

from bsbetl.ov_helpers import global_ov_update
from bsbetl.alltable_calcs import at_columns



def ov_SlowDailyVols(df: pd.DataFrame, share_num: str):
    ''' per 210223 Calc Daily Vols Initial Stage.odt section 1a) thru 1g)
    '''

    # the last calculated values of the following columns must be copied from their At into the Ov
    #'SDVBsl', 'SDVBm', 'SDVBf', 'SDVCsl', 'SDVCm', 'SDVCf1', 'SDVCf2',

    #SDVBsl
    last_SDVBsl = df.iloc[:,at_columns.AT_COL2INDEX['SDVBsl']].iloc[-1]
    global_ov_update(share_num, 'SDVBsl', last_SDVBsl)

    #SDVBm
    last_SDVBm = df.iloc[:,at_columns.AT_COL2INDEX['SDVBm']].iloc[-1]
    global_ov_update(share_num, 'SDVBm', last_SDVBm)

    #SDVBf
    last_SDVBf = df.iloc[:,at_columns.AT_COL2INDEX['SDVBf']].iloc[-1]
    global_ov_update(share_num, 'SDVBf', last_SDVBf)

    #SDVCsl
    last_SDVCsl = df.iloc[:,at_columns.AT_COL2INDEX['SDVCsl']].iloc[-1]
    global_ov_update(share_num, 'SDVCsl', last_SDVCsl)

    #SDVCm
    last_SDVCm = df.iloc[:,at_columns.AT_COL2INDEX['SDVCm']].iloc[-1]
    global_ov_update(share_num, 'SDVCm', last_SDVCm)

    #SDVCf1
    last_SDVCf1 = df.iloc[:,at_columns.AT_COL2INDEX['SDVCf1']].iloc[-1]
    global_ov_update(share_num, 'SDVCf1', last_SDVCf1)

    #SDVCf2
    last_SDVCf2 = df.iloc[:,at_columns.AT_COL2INDEX['SDVCf2']].iloc[-1]
    global_ov_update(share_num, 'SDVCf2', last_SDVCf2)


