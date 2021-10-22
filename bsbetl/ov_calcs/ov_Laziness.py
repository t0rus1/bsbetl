from types import SimpleNamespace
from bsbetl.simple_param import SimpleParam
import logging

import pandas as pd

from bsbetl.ov_helpers import global_ov_update
from bsbetl.alltable_calcs import at_columns

from bsbetl.ov_calcs import ov_params


def ov_Laziness(df: pd.DataFrame, share_num: str, parm_turnover: SimpleParam, parm_zerovol_rows: SimpleParam):
    """ Uses price & volume of the share to determine and store 'Lazy' & 'VP' & 'LastPrice' in the overview """

    #assert params.ov_laziness_turnover >= params.ov_laziness_turnover_min and params.ov_laziness_turnover <= params.ov_laziness_turnover_max
    #assert params.ov_laziness_zerovol_rows >= params.ov_laziness_zerovol_rows_min and params.ov_laziness_zerovol_rows <= params.ov_laziness_zerovol_rows_max

    mean_vol = df['volume'].mean()  # .iloc[-1]  # grabs last item from Series
    last_price = df.iloc[:, at_columns.AT_COL2INDEX['price']].iloc[-1]  # ditto
    # we use the LastPrice's date for the date entry in the Ov
    last_price_date = df.iloc[:, at_columns.AT_COL2INDEX['price']].index[-1]

    turnover = mean_vol * last_price

    # init default return tuple
    lazi_turnover = (True, turnover)

    if turnover >= parm_turnover['setting']:
        # got sufficient turnover, but what about zero volume days?
        # filter on zero volume rows and count
        zv_df = df['volume'] <= 0

        if len(zv_df.index) > parm_zerovol_rows['setting']:
            lazi_turnover = (False, turnover)

    global_ov_update(share_num, 'Lazy', lazi_turnover[0])
    global_ov_update(share_num, 'VP', lazi_turnover[1])
    #ov_column_update(share_num, 'DCP', last_price)
    global_ov_update(share_num, 'Date', last_price_date)

    logging.debug(f'calc_laziness DONE')
