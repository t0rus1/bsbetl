import logging

from numpy.core.numeric import nan
from bsbetl.func_helpers import add_df_columns
import random
import pandas as pd
from bsbetl import g
#from bsbetl.func_helpers import add_df_columns, report_all_fail, report_row_shares_passing, report_results_so_far

''' Functions for ... '''


def compute_djp(ov: pd.DataFrame, results: pd.DataFrame):  # report_f
    ''' add a 'DjP' column to the results and compute its values using columns in the passed ov '''

    results['DjP'] = nan
    ov['DjP']= nan
    try:
        for cur_idx, row in ov.iterrows(): # ov at this stage has integer index - ShareNumber is a plain column
            RDPjP = (row['DHP']/row['DHP.D-1']) - 1 if row['DHP.D-1'] > 0 else nan
            # perform actual evaluation, x=1
            test = RDPjP is not nan and row['DHP.D-2'] > 0 and (row['DHP.D-1']/row['DHP.D-2'] - 1 < 0.4 * RDPjP)
            if test:
                # inequality fulfilled, x=2
                test = row['DHP.D-3'] and (row['DHP.D-2'] / row['DHP.D-3'] - 1 < 0.4 * RDPjP)
                if test:
                    # fulfilled, x=3
                    test = row['DHP.D-4'] > 0 and (row['DHP.D-3'] / row['DHP.D-4'] - 1 < 0.4 * RDPjP)
                    if test:
                        # fulfilled, x=4
                        test = row['DHP.D-5'] > 0 and (row['DHP.D-4'] / row['DHP.D-5'] - 1 < 0.4 * RDPjP)
                        if test:
                            # fulfilled, x=5
                            test = row['DHP.D-6'] > 0 and (row['DHP.D-5'] / row['DHP.D-6'] - 1 < 0.4 * RDPjP)
                            if test:
                                # fulfilled, x=6
                                test = row['DHP.D-7'] > 0 and (row['DHP.D-6'] / row['DHP.D-7'] - 1 < 0.4 * RDPjP)
                                if test:
                                    # fulfilled, x=7
                                    test = row['DHP.D-8'] > 0 and (row['DHP.D-7'] / row['DHP.D-8'] - 1 < 0.4 * RDPjP)
                                    if test:
                                        # fulfilled, x=8
                                        test = row['DHP.D-9'] > 0 and (row['DHP.D-8'] / row['DHP.D-9'] - 1 < 0.4 * RDPjP)
                                        if test:
                                            # 9 regardless
                                            results.loc[cur_idx,'DjP'] = 9
                                        else:
                                            # not fulfilled
                                            results.loc[cur_idx,'DjP'] = 8
                                    else:
                                        # not fulfilled
                                        results.loc[cur_idx,'DjP'] = 7
                                else:
                                    # not fulfilled
                                    results.loc[cur_idx,'DjP'] = 6
                            else:
                                # not fulfilled
                                results.loc[cur_idx,'DjP'] = 5
                        else:
                            # not fulfilled
                            results.loc[cur_idx,'DjP'] = 4
                    else:
                        # not fulfilled
                        results.loc[cur_idx,'DjP'] = 3
                else:
                    # not fulfilled
                    results.loc[cur_idx,'DjP'] = 2
            else:
                # inequality not fullfilled
                results.loc[cur_idx,'DjP'] = 1

    except ZeroDivisionError as zde:
        logging.warn('Zero Division Error in compute_djp')        

    #combine the Ov into the results
    #add_df_columns(results, ov, ov.columns)
    #carry 'DjP' into the Ov
    ov.loc[:,'DjP'] = results['DjP']

    return
