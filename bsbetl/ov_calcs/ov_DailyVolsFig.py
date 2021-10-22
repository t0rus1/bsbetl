import logging

import pandas as pd

from bsbetl.ov_helpers import global_ov_update
from bsbetl.alltable_calcs import at_columns



def ov_DailyVolsFigure(df: pd.DataFrame, share_num: str):
    ''' per 210223 Calc Daily Vols Initial Stage.odt section 1h)
    compute a volumes constellation, the Daily Vols Figure, 'DVFxx' 
    '''

    #NOTE df is an All-Table dataframe!
    #last_price = df.iloc[:, at_columns.AT_COL2INDEX['price']].iloc[-1]  # ditto

    # below an extract from the instructions... DV means Daily Volume 
    # we shall use ODV (same thing)
    # 
    # DVFDf D = DVD / SDVBf D 
	# DVFf1 D = SDVCf1 D / SDVBf D 
	# DVFf2 D = SDVCf2 D / SDVBf D 
	# DVFm D = SDVCm D / SDVBm D 
	# DVFsl D = SDVCsl D / SDVBsl D 


    #last_dvd = df.iloc[:,at_columns.AT_COL2INDEX['DV']].iloc[-1]

    try:
        sdvbf = df.iloc[:,at_columns.AT_COL2INDEX['SDVBf']].iloc[-1]
        sdvbf1 = df.iloc[:,at_columns.AT_COL2INDEX['SDVBf']].iloc[-2]
        sdvbf2 = df.iloc[:,at_columns.AT_COL2INDEX['SDVBf']].iloc[-3]
        sdvbf3 = df.iloc[:,at_columns.AT_COL2INDEX['SDVBf']].iloc[-4]

        sdvcf1 = df.iloc[:,at_columns.AT_COL2INDEX['SDVCf1']].iloc[-1]
        sdvcf2 = df.iloc[:,at_columns.AT_COL2INDEX['SDVCf2']].iloc[-1]

        sdvcm = df.iloc[:,at_columns.AT_COL2INDEX['SDVCm']].iloc[-1]
        sdvbm4 = df.iloc[:,at_columns.AT_COL2INDEX['SDVBm']].iloc[-5]

        sdvcsl = df.iloc[:,at_columns.AT_COL2INDEX['SDVCsl']].iloc[-1]
        sdvbsl = df.iloc[:,at_columns.AT_COL2INDEX['SDVBsl']].iloc[-1]

        last_dv = df.iloc[:,at_columns.AT_COL2INDEX['DV']].iloc[-1]

        # DVFdf = last_dvd/last_sdvbf3
        # global_ov_update(share_num, 'DVFdf', DVFdf)

        DVFf3 = last_dv/sdvbf1
        df.iloc[-1,df.columns.get_loc('DVFf3')] = DVFf3
        global_ov_update(share_num, 'DVFf3', DVFf3)

        DVFf2 = sdvcf2/sdvbf2
        df.iloc[-1,df.columns.get_loc('DVFf2')] = DVFf2
        global_ov_update(share_num, 'DVFf2', DVFf2)

        DVFf1 = sdvcf1/sdvbf3
        df.iloc[-1,df.columns.get_loc('DVFf1')] = DVFf1
        global_ov_update(share_num, 'DVFf1', DVFf1)

        DVFm = sdvcm/sdvbm4
        df.iloc[-1,df.columns.get_loc('DVFm')] = DVFm
        global_ov_update(share_num, 'DVFm', DVFm)

        DVFsl = sdvcsl/sdvbsl
        df.iloc[-1,df.columns.get_loc('DVFsl')] = DVFsl
        global_ov_update(share_num, 'DVFsl', DVFsl)

        #while we're about it, grab the last DV  (modified Daily Vol) from the at
        global_ov_update(share_num, 'DV', last_dv)

    except IndexError as exc:
        logging.error(f'ov_DailyVolsFig exception {exc}')






