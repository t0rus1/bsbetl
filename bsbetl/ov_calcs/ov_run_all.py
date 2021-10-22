""" a single function which sequentially does all the overview calcs for a single share """

from bsbetl.ov_calcs import ov_DailyVolsFig
import logging
import inspect

from bsbetl.ov_calcs.ov_params import ov_calc_params
from bsbetl.ov_calcs.ov_Laziness import ov_Laziness


def run_all_final_ov_calcs(df, single_share_path: str, share_num: str, stage: int):
    """ call these additional calculations which can be computed post all alltable_calcs """

    func_name = inspect.stack()[0][3]
    logging.info(f'{func_name}...{share_num}')

    if stage == 1:
        ov_Laziness(
            df, share_num, ov_calc_params['ovp_lazy_turnover'], ov_calc_params['ovp_lazy_zerovol_rows'])

    if stage == 2:
        
        ov_DailyVolsFig.ov_DailyVolsFigure(df,share_num)



    #ov_dummy_above_sma(df, share_num, ov_calc_params['ovp_dummyAboveSMA'])

    logging.info(f'End {func_name} {share_num}.')
