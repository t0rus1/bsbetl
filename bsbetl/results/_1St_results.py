import random
import pandas as pd
from bsbetl import g
from bsbetl.helpers import copy_column_format_and_flag, update_column_format_and_flag
from bsbetl.func_helpers import add_df_columns, report_all_fail, report_ov_shares_passing, report_results_so_far
from bsbetl.results._1St_conditions import _1St_conditions

''' Functions for applying various 1st Stage Conditions to the Ov table '''


def _1St_Condition_a(ov: pd.DataFrame, results: pd.DataFrame, report_f) -> tuple:
    ''' Apply Pr 1. Con. a):  '''

    report_f.write(f"*_1St_Condition_a:*  \n")

    con = _1St_conditions['Con_a']
    audit_dict = {}
    audit_dict['Con_a'] = con
    #sub_conditions = []

    adj = con['adjustors']

    full_condition_str = f'SDHPGr1.shoD > {adj[0]} AND ((SDT1.fD > {adj[1]}) OR (SDT1.slD > {adj[2]}))  \n'
    report_f.write(full_condition_str)

    # initialize Con_a result column as first value term in the above condition and as a FAIL
    update_column_format_and_flag(results,'Con_a', ov,'SDHPGr1sh',g.FAIL)

    mask = ov['SDHPGr1sh'] > adj[0] # 1.005
    masked_ov = ov[mask]
    if len(masked_ov.index) > 0:
        mask1 = masked_ov['SDT1f'] > adj[1] #  10_000
        mask2 = masked_ov['SDT1sl'] > adj[2] # 5_000 

        masked_ov = masked_ov[mask1 | mask2].copy()
        if len(masked_ov.index) > 0:
            # we have some passing results in masked_ov 
            # so place a Con_a column in it taken from the ov 'SDHPGr1sh' suitably flagged as passing
            copy_column_format_and_flag(masked_ov, 'Con_a', 'SDHPGr1sh', g.PASS)
            # overwrite corresponding cells in results
            results.update(masked_ov['Con_a'])

        report_ov_shares_passing(report_f,masked_ov.index)

    else:
        report_all_fail(report_f)

    #report_results_so_far(report_f,results)
    return audit_dict

def _1St_Condition_b(ov: pd.DataFrame, results: pd.DataFrame, report_f) -> dict:
    ''' Apply Pr 1. Con. b):  '''

    report_f.write("*_1St_Condition_b:*  \n")
    con = _1St_conditions['Con_b']
    audit_dict = {}
    audit_dict['Con_b'] = con
    #sub_conditions = []

    adj = con['adjustors']

    full_condition_str = f'SDHPGr1.mD > {adj[0]} AND ((SDT1.fD > {adj[1]}) OR (SDT1.slD > {adj[2]}))  \n'
    report_f.write(full_condition_str)

    # initialize Con_b result column as first value term in the above condition and as a FAIL
    update_column_format_and_flag(results, 'Con_b', ov, 'SDHPGr1m', g.FAIL)

    mask = ov['SDHPGr1m'] > adj[0]  # 1   
    masked_ov = ov[mask]
    if len(masked_ov.index) > 0:
        mask1 = masked_ov['SDT1f'] > adj[1] # 10_000
        mask2 = masked_ov['SDT1sl'] > adj[2] # 5_000 
        
        mask = mask1 | mask2
        masked_ov = masked_ov[mask].copy()
        if len(masked_ov.index) > 0:
            # passing results
            # hold a new Con_b column in masked_ov containing a copy of 'SDHPGr1m' suitably formatted and flagged
            copy_column_format_and_flag(masked_ov, 'Con_b', 'SDHPGr1m', g.PASS)
            results.update(masked_ov['Con_b'])

        report_ov_shares_passing(report_f,masked_ov.index)
    else:
        report_all_fail(report_f)

    #report_results_so_far(report_f,results)
    return audit_dict

def _1St_Condition_c(ov: pd.DataFrame, results: pd.DataFrame, report_f) -> dict:
    ''' Apply Pr 1. Con. d):  '''

    report_f.write("*_1St_Condition_c:*  \n")
    con = _1St_conditions['Con_c']
    audit_dict = {}
    audit_dict['Con_c'] = con


    adj = con['adjustors']

    full_condition_str = f'SDHPGr1.lo D > {adj[0]} AND ((SDT1.fD > {adj[1]}) OR (SDT1.slD > {adj[0]}))  \n'
    report_f.write(full_condition_str)

    # initialize Con_c result column as first value term in the above condition and as a FAIL
    update_column_format_and_flag(results, 'Con_c', ov, 'SDHPGr1lo', g.FAIL)
    mask = ov['SDHPGr1lo'] > adj[0] # 1
    masked_ov = ov[mask]
    if len(masked_ov.index) > 0:
        #report_f.write(f"{len(masked_ov.index)} shares pass {mask_str}  \n")
        mask1 = masked_ov['SDT1f'] > adj[1] #10_000
        mask2 = masked_ov['SDT1sl'] > adj[2] # 5_000

        mask = mask1 | mask2
        masked_ov = masked_ov[mask].copy()
        if len(masked_ov.index) > 0:
            copy_column_format_and_flag(masked_ov, 'Con_c', 'SDHPGr1lo', g.PASS)
            results.update(masked_ov['Con_c'])

        report_ov_shares_passing(report_f,masked_ov.index)
    else:
        report_all_fail(report_f)

    #report_results_so_far(report_f,results)
    return audit_dict

def _1St_Condition_d(ov: pd.DataFrame, results: pd.DataFrame, report_f) -> dict:
    ''' Apply Pr 1. Con. d):  '''

    report_f.write("*_1St_Condition_d:*  \n")
    con = _1St_conditions['Con_d']
    audit_dict = {}
    audit_dict['Con_d'] = con

    adj = con['adjustors']
    full_condition_str = f'SDHPGr1.sh D > {adj[0]} AND ((SDT1.fD > {adj[1]}) OR (SDT1.slD > {adj[2]})) AND DTF1. D > {adj[3]}  \n'
    report_f.write(full_condition_str)

    # initialize Con_d result column as first value term in the above condition and as a FAIL
    update_column_format_and_flag(results, 'Con_d', ov, 'DTF', g.FAIL)
    mask = ov['SDHPGr1sh'] > adj[0] # 0.995
    masked_ov = ov[mask]
    if len(masked_ov.index) > 0:
        mask1 = masked_ov['SDT1f'] > adj[1] # 10_000
        mask2 = masked_ov['SDT1sl'] > adj[2] #5_000 

        mask = mask1 | mask2
        masked_ov = masked_ov[mask]
        if len(masked_ov.index) > 0:
            mask = masked_ov['DTF'] > adj[3] #3

            masked_ov = masked_ov[mask].copy()
            if len(masked_ov.index) > 0:
                # we have some passing results
                copy_column_format_and_flag(masked_ov, 'Con_d', 'DTF', g.PASS)
                results.update(masked_ov['Con_d'])

            report_ov_shares_passing(report_f,masked_ov.index)
    else:
        report_all_fail(report_f)

    #report_results_so_far(report_f,results)
    return audit_dict

