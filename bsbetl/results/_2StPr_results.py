from bsbetl.helpers import copy_column_format_and_flag, initialize_condition_column, update_column_format_and_flag
import random
import numpy as np
from numpy.core.numeric import NaN
import pandas as pd
from bsbetl import g
from bsbetl.func_helpers import add_df_columns, report_all_fail, report_ov_shares_passing, report_ov_shares_simply_displayed, report_results_so_far
from bsbetl.results._2StPr_conditions import _2StPr_conditions

''' Functions for applying various 1st Stage Conditions to the Ov table '''

def _2StPr_Condition_a1(ov: pd.DataFrame, results: pd.DataFrame, report_f) -> dict:
    ''' Apply Condition a1) 2. St. Pr. Conditions to meet to enter the 3. Stage 
    '''

    report_f.write(f"  \n*_2StPr_Condition_a1:*  \n")
    con = _2StPr_conditions['Con_a1']
    audit_dict = {}
    audit_dict['Con_a1'] = con
    sub_conditions = []

    adj = con['adjustors']

    report_f.write(f"{con['description']}  \n")

    results['Con_a1'] = ov['DaysDHPlasthi']
    report_ov_shares_simply_displayed(report_f,ov.index)

    return audit_dict

def _2StPr_Condition_a2(ov: pd.DataFrame, results: pd.DataFrame, report_f) -> dict:
    ''' Apply Condition a2) 2. St. Pr. Conditions to meet to enter the 3. Stage 
    '''

    report_f.write(f"  \n*_2StPr_Condition_a2:*  \n")
    con = _2StPr_conditions['Con_a2']
    audit_dict = {}
    audit_dict['Con_a2'] = con
    sub_conditions = []

    adj = con['adjustors']

    report_f.write(f"{con['description']}  \n")

    results['Con_a2'] = ov['DaysDHPlasthi3perc']
    report_ov_shares_simply_displayed(report_f,ov.index)

    return audit_dict

def _2StPr_Condition_a3(ov: pd.DataFrame, results: pd.DataFrame, report_f) -> dict:
    ''' Apply Condition a3) 2. St. Pr. Conditions to meet to enter the 3. Stage 
    '''

    report_f.write(f"  \n*_2StPr_Condition_a3:*  \n")
    con = _2StPr_conditions['Con_a3']
    audit_dict = {}
    audit_dict['Con_a3'] = con
    sub_conditions = []

    adj = con['adjustors']

    report_f.write(f"{con['description']}  \n")

    results['Con_a3'] = ov['DaysDHPlast20hi']
    report_ov_shares_simply_displayed(report_f,ov.index)

    return audit_dict

def _2StPr_Condition_b(ov: pd.DataFrame, results: pd.DataFrame, report_f) ->dict:
    ''' Apply Con_b1 thru Con_b5 to the ov & gather results 
    '''
    report_f.write(f"  \n*_2StPr_Condition_b:*  \n")
    audit_dict = {}
    con_keys = ['Con_b1','Con_b2','Con_b3','Con_b4','Con_b5']
    for con_key in con_keys:
        report_f.write(f"{con_key}:  \n")
        con = _2StPr_conditions[con_key]  

        audit_dict[con_key] = con
        dhp_from = con['DHPd_from']
        dhp_to = con['DHPd_to']
        e = con['exponent']

        num_nodata_shares = initialize_condition_column(con_key, results, ov)

        # create a DHP range restricted dataframe
        dhp_range_mask = (ov['DHP'] >= dhp_from) & (ov['DHP'] <= dhp_to) & (ov['Status'] != 'no data')
        dhp_range_df = ov[dhp_range_mask]
        # filter in those passing the threshold
        over_threshold_mask = (dhp_range_df['DHP']/dhp_range_df['DHOCP'])**e > con['C2Pcb']        
        over_threshold_df = dhp_range_df[over_threshold_mask]
        #assign passing values into the condition column of the results
        over_threshold_df[con_key] = (over_threshold_df['DHP']/over_threshold_df['DHOCP'])**e
        copy_column_format_and_flag(over_threshold_df,con_key,con_key,g.PASS)
        
        if len(over_threshold_df)>0:
            results.update(over_threshold_df[con_key]) # updates only those results rows in the masked_df               

        #assign those that are in dhp range but under threshold
        under_threshold_mask = (dhp_range_df['DHP']/dhp_range_df['DHOCP'])**e <= con['C2Pcb']        
        under_threshold_df = dhp_range_df[under_threshold_mask]

        under_threshold_df[con_key] = (dhp_range_df['DHP']/dhp_range_df['DHOCP'])**e
        copy_column_format_and_flag(under_threshold_df,con_key,con_key,g.FAIL)
        if len(under_threshold_df)>0:
            results.update(under_threshold_df[con_key])
        
        #complete range failures            
        dhp_range_fail_mask = (ov['DHP'] < dhp_from) | (ov['DHP'] > dhp_to) & (ov['Status'] != 'no data')
        dhp_range_fail_df = ov[dhp_range_fail_mask]
        # dhp_range_fail_df[con_key] = '-'
        # results.update(dhp_range_fail_df[con_key])

        report_f.write(f"{num_nodata_shares} shares with no data, {len(dhp_range_df)} shares in DHP range of {dhp_from} to {dhp_to} ({len(dhp_range_fail_df)} outside), {len(over_threshold_df)} shares over threshold ({len(under_threshold_df)} under) out of a total of {len(ov)} shares  \n")

    return audit_dict

def _2StPr_Condition_c(ov: pd.DataFrame, results: pd.DataFrame, report_f) ->dict:
    ''' Apply Con_c1 thru Con_c5 to the ov & gather results 
    '''

    #print(f'_2St_Condition_c len(results)={len(results)}')
    report_f.write(f"  \n*_2StPr_Condition_c:*  \n")
    #adj = _2StPr_conditions['Con_c']['adjustors']

    audit_dict = {}
    con_keys = ['Con_c1','Con_c2','Con_c3','Con_c4','Con_c5']
    for con_key in con_keys:
        report_f.write(f"{con_key}:  \n")
        con = _2StPr_conditions[con_key]  

        audit_dict[con_key] = con
        dhp_from = con['DHPd_from']
        dhp_to = con['DHPd_to']
        e = con['exponent']

        num_nodata_shares = initialize_condition_column(con_key, results, ov)

        # create a DHP range restricted dataframe
        dhp_range_mask = (ov['DHP'] >= dhp_from) & (ov['DHP'] <= dhp_to) & (ov['Status'] != 'no data')
        dhp_range_df = ov[dhp_range_mask]
        # filter in those passing the threshold
        over_threshold_mask = (dhp_range_df['DHP']/dhp_range_df['DHP.D-1'])**e > con['C2Pcc']
        over_threshold_df = dhp_range_df[over_threshold_mask]

        # assign PASSing values into the condition column of the results
        over_threshold_df[con_key] = (over_threshold_df['DHP']/over_threshold_df['DHP.D-1'])**e
        copy_column_format_and_flag(over_threshold_df,con_key,con_key,g.PASS)
        if len(over_threshold_df)>0:
            results.update(over_threshold_df[con_key])

        #assign those that are in dhp range but under threshold as FAILS
        under_threshold_mask = (dhp_range_df['DHP']/dhp_range_df['DHP.D-1'])**e <= con['C2Pcc']
        under_threshold_df = dhp_range_df[under_threshold_mask]
        under_threshold_df[con_key] = (under_threshold_df['DHP']/under_threshold_df['DHP.D-1'])**e

        # under_threshold_df[con_key] = under_threshold_df[con_key].map('{0:.3f}'.format)
        # under_threshold_df[con_key] = under_threshold_df[con_key]  + f' {g.FAIL}'
        copy_column_format_and_flag(under_threshold_df,con_key,con_key,g.FAIL)
        if len(under_threshold_df)>0:
            results.update(under_threshold_df[con_key])

        #complete range failures
        dhp_range_fail_mask = (ov['DHP'] < dhp_from) | (ov['DHP'] > dhp_to) & (ov['Status'] != 'no data')
        dhp_range_fail_df = ov[dhp_range_fail_mask]
        #dhp_range_fail_df[con_key] = '-'
        #results.update(dhp_range_fail_df[con_key])

        report_f.write(f"{num_nodata_shares} shares with no data, {len(dhp_range_df)} shares in DHP range of {dhp_from} to {dhp_to} ({len(dhp_range_fail_df)} outside), {len(over_threshold_df)} shares over threshold ({len(under_threshold_df)} under) out of a total of {len(ov)} shares  \n")

    return audit_dict

def _2StPr_Condition_d(ov: pd.DataFrame, results: pd.DataFrame, report_f) -> dict:
    ''' Apply Con_d1 thru Con_d5 to the ov & gather results 
    '''

    report_f.write(f"  \n*_2StPr_Condition_d:*  \n")

    audit_dict = {}
    con_keys = ['Con_d1','Con_d2','Con_d3','Con_d4','Con_d5']
    for con_key in con_keys:
        report_f.write(f"{con_key}:  \n")
        con = _2StPr_conditions[con_key]

        audit_dict[con_key] = con
        dhp_from = con['DHPd_from']
        dhp_to = con['DHPd_to']
        e = con['exponent']

        num_nodata_shares = initialize_condition_column(con_key, results, ov)

        # create a DHP range restricted dataframe
        dhp_range_mask = (ov['DHP'] >= dhp_from) & (ov['DHP'] <= dhp_to) & (ov['Status'] != 'no data')
        dhp_range_df = ov[dhp_range_mask]
        # filter in those passing the threshold
        over_threshold_mask = (dhp_range_df['DHP']/dhp_range_df['DHP.D-2'])**e > con['C2Pcd']
        over_threshold_df = dhp_range_df[over_threshold_mask]
        # assign passing values into the condition column
        over_threshold_df[con_key] = (over_threshold_df['DHP']/over_threshold_df['DHP.D-2'])**e

        copy_column_format_and_flag(over_threshold_df,con_key,con_key,g.PASS)
        if len(over_threshold_df)>0:
            results.update(over_threshold_df[con_key])

        #assign those that are in dhp range but under threshold as FAILS
        under_threshold_mask = (dhp_range_df['DHP']/dhp_range_df['DHP.D-2'])**e <= con['C2Pcd']
        under_threshold_df = dhp_range_df[under_threshold_mask]

        under_threshold_df[con_key] = (under_threshold_df['DHP']/under_threshold_df['DHP.D-2'])**e
        copy_column_format_and_flag(under_threshold_df,con_key,con_key,g.FAIL)
        if len(under_threshold_df)>0:
            results.update(under_threshold_df[con_key])

        #complete range failures
        dhp_range_fail_mask = (ov['DHP'] < dhp_from) | (ov['DHP'] > dhp_to) & (ov['Status'] != 'no data')
        dhp_range_fail_df = ov[dhp_range_fail_mask]
        #dhp_range_fail_df[con_key] = '-'
        #results.update(dhp_range_fail_df[con_key])

        report_f.write(f"{num_nodata_shares} shares with no data, {len(dhp_range_df)} shares in DHP range of {dhp_from} to {dhp_to} ({len(dhp_range_fail_df)} outside), {len(over_threshold_df)} shares over threshold ({len(under_threshold_df)} under) out of a total of {len(ov)} shares  \n")

    return audit_dict

def _2StPr_Condition_e(ov: pd.DataFrame, results: pd.DataFrame, report_f) -> dict:
    ''' Apply Con_d1 thru Con_d5 to the ov & gather results 
    '''

    report_f.write(f"  \n*_2StPr_Condition_e:*  \n")

    audit_dict = {}
    con_keys = ['Con_e1','Con_e2','Con_e3','Con_e4','Con_e5']
    for con_key in con_keys:
        report_f.write(f"{con_key}:  \n")
        con = _2StPr_conditions[con_key]
        audit_dict[con_key] = con
        dhp_from = _2StPr_conditions[con_key]['DHPd_from']
        dhp_to = _2StPr_conditions[con_key]['DHPd_to']
        e = _2StPr_conditions[con_key]['exponent']

        num_nodata_shares = initialize_condition_column(con_key, results, ov)

        # create a dhp range restricted dataframe
        dhp_range_mask = (ov['DHP'] >= dhp_from) & (ov['DHP'] <= dhp_to) & (ov['Status'] != 'no data')
        dhp_range_df = ov[dhp_range_mask]
        # filter in those shares passing threshold
        over_threshold_mask = (dhp_range_df['DHP']/dhp_range_df['DHP.D-3'])**e > con['C2Pce']
        over_threshold_df = dhp_range_df[over_threshold_mask]
        # assign passing values into the condition column
        over_threshold_df[con_key] = (over_threshold_df['DHP']/over_threshold_df['DHP.D-3'])**e
        copy_column_format_and_flag(over_threshold_df,con_key,con_key,g.PASS)
        if len(over_threshold_df)>0:
            results.update(over_threshold_df[con_key])

        #assign those that are in dhp range but under threshold as FAILS
        under_threshold_mask = (dhp_range_df['DHP']/dhp_range_df['DHP.D-3'])**e <= con['C2Pce']
        under_threshold_df = dhp_range_df[under_threshold_mask]

        under_threshold_df[con_key] = (under_threshold_df['DHP']/under_threshold_df['DHP.D-3'])**e

        copy_column_format_and_flag(under_threshold_df,con_key,con_key,g.FAIL)
        if len(under_threshold_df)>0:
            results.update(under_threshold_df[con_key])

        #complete range failures
        dhp_range_fail_mask = (ov['DHP'] < dhp_from) | (ov['DHP'] > dhp_to) & (ov['Status'] != 'no data')
        dhp_range_fail_df = ov[dhp_range_fail_mask]
        #dhp_range_fail_df[con_key] = '-'
        #results.update(dhp_range_fail_df[con_key])

        report_f.write(f"{num_nodata_shares} shares with no data, {len(dhp_range_df)} shares in DHP range of {dhp_from} to {dhp_to} ({len(dhp_range_fail_df)} outside), {len(over_threshold_df)} shares over threshold ({len(under_threshold_df)} under) out of a total of {len(ov)} shares  \n")

    return audit_dict

def _2StPr_Condition_f(ov: pd.DataFrame, results: pd.DataFrame, report_f) -> dict:
    ''' Apply Condition f) 2. St. Pr. Conditions to meet to enter the 3. Stage 
    '''

    report_f.write(f"  \n*_2StPr_Condition_f:*  \n")
    con = _2StPr_conditions['Con_f']
    adj = con['adjustors']
    audit_dict = {}
    audit_dict['Con_f'] = con
    sub_conditions = []

    # add 'Con_f' column to results
    num_nodata_shares = initialize_condition_column('Con_f', results, ov)
    # copy DHPGrAvLo values to it,flagging all initially as FAILing
    update_column_format_and_flag(results,'Con_f',ov,'DHPGrAvLo',g.FAIL)

    sub_conditions.append(f"'DHPGrAvLo' > {_2StPr_conditions['Con_f']['C2Pcf']}")
    sub_conditions.append(f"'DCP' < {adj[0]} * 'DOP.D-1'") # 1.03
    full_condition_str = f"`{' AND '.join(sub_conditions)}`  \n" 
    report_f.write(full_condition_str)

    over_threshold_mask1 = (ov['DHPGrAvLo'] > _2StPr_conditions['Con_f']['C2Pcf']) & (ov['Status'] != 'no data')
    over_threshold_df = ov[over_threshold_mask1]

    over_threshold_mask2 = over_threshold_df['DCP'] < adj[0] * over_threshold_df['DOP.D-1'] # 1.03
    fully_passing_df = over_threshold_df[over_threshold_mask2]

    # assign passing values into the results
    fully_passing_df['Con_f'] = ov['DHPGrAvLo']
    copy_column_format_and_flag(fully_passing_df,'Con_f','Con_f',g.PASS)
    if len(fully_passing_df)>0:
        results.update(fully_passing_df['Con_f'])

    report_f.write(f"{num_nodata_shares} shares with no data, {len(fully_passing_df)} shares pass out of a total of {len(ov)} shares  \n")

    return audit_dict


def _2StPr_Condition_g(ov: pd.DataFrame, results: pd.DataFrame, report_f) -> dict:
    ''' Apply Condition g) 2. St. Pr. Conditions to meet to enter the 3. Stage 
    '''

    report_f.write(f"  \n*_2StPr_Condition_g:*  \n")
    con = _2StPr_conditions['Con_g']

    audit_dict = {}
    audit_dict['Con_g'] = con
    sub_cond = []

    con_key='Con_g'
    # add con_key column to results
    num_nodata_shares = initialize_condition_column(con_key, results, ov)
    # copy DHPGr values to it,flagging all initially as FAILing
    update_column_format_and_flag(results, con_key, ov,'DHPGr',g.FAIL)

    sub_cond.append(f"'DHPGr' > {con['C2Pcgs']}")
    sub_cond.append(f"'DHPGrAvSh'.D-1 < {con['C2Pcgb']}")
    sub_cond.append(f"('DHPGrAvSh' / 'DHPGrAvSh'.D-1) > {con['C2PcgA']}")
    sub_cond.append(f"('DHPGrAvSh' / 'DHPGrAvSh'.D-2) > {con['C2PcgA']}")
    sub_cond.append(f"'DHPGrDiF'.D-1 < {con['C2PcgD']}")

    full_condition_str = f"`{' AND '.join(sub_cond)}`  \n" 
    report_f.write(full_condition_str)

    #apply a series of filters
    mask1 = ov['DHPGr'] > con['C2Pcgs']
    masked_ov = ov[mask1]
    report_f.write(f"{len(masked_ov)} shares pass sub condition: {sub_cond[0]}  \n")

    mask2 = masked_ov['DHPGrAvSh.D-1'] < con['C2Pcgb']
    masked_ov = masked_ov[mask2]
    report_f.write(f"{len(masked_ov)} shares remaining after also passing sub condition: {sub_cond[1]}  \n")

    mask3 = (masked_ov['DHPGrAvSh'] / masked_ov['DHPGrAvSh.D-1']) > con['C2PcgA']
    masked_ov = masked_ov[mask3]
    report_f.write(f"{len(masked_ov)} shares remaining after also passing sub condition: {sub_cond[2]}  \n")

    mask4 = (masked_ov['DHPGrAvSh'] / masked_ov['DHPGrAvSh.D-2']) > con['C2PcgA']
    masked_ov = masked_ov[mask4]
    report_f.write(f"{len(masked_ov)} shares remaining after also passing sub condition: {sub_cond[3]}  \n")

    mask5 = masked_ov['DHPGrDiF.D-1'] < con['C2PcgD']
    masked_ov = masked_ov[mask5]
    report_f.write(f"{len(masked_ov)} shares remaining after also passing sub condition: {sub_cond[4]}  \n")

    update_column_format_and_flag(masked_ov,con_key,ov,'DHPGr',g.PASS)
    if len(masked_ov)>0:
        results.update(masked_ov[con_key])

    return audit_dict

def _2StPr_Condition_h(ov: pd.DataFrame, results: pd.DataFrame, report_f) -> dict:
    ''' Apply Condition h) 2. St. Pr. Conditions to meet to enter the 3. Stage 
    '''

    report_f.write(f"  \n*_2StPr_Condition_h:*  \n")
    con = _2StPr_conditions['Con_h']
    adj = con['adjustors']
    sub_cond = []
    audit_dict = {}
    audit_dict['Con_h'] = con

    con_key = 'Con_h'

    # add con_key column to results
    num_nodata_shares = initialize_condition_column(con_key, results, ov)
    # copy DHPGrAvLo values to it,flagging all initially as FAILing
    update_column_format_and_flag(results, con_key, ov,'DHPGrAvLo',g.FAIL)

    sub_cond.append(f"'DHPGrAvLo' > {adj[0]}") #0.9995"
    sub_cond.append(f"'DHPGrDiSl'.D-1 < {con['C2Pch']}")

    full_condition_str = f"`{' AND '.join(sub_cond)}`  \n" 
    report_f.write(full_condition_str)

    mask1 = ov['DHPGrAvLo'] > adj[0] #0.9995
    masked_ov = ov[mask1]
    report_f.write(f"{len(masked_ov)} shares pass sub condition: {sub_cond[0]}  \n")

    mask2 = masked_ov['DHPGrDiSl.D-1'] < con['C2Pch']
    masked_ov = masked_ov[mask2]
    report_f.write(f"{len(masked_ov)} shares remaining after also passing sub condition: {sub_cond[1]}  \n")

    update_column_format_and_flag(masked_ov,con_key,ov,'DHPGrAvLo',g.PASS)
    if len(masked_ov)>0:
        results.update(masked_ov[con_key])

    return audit_dict

def _2StPr_Condition_i(ov: pd.DataFrame, results: pd.DataFrame, report_f) -> dict:
    ''' Apply Condition i) 2. St. Pr. Conditions to meet to enter the 3. Stage 
    '''

    report_f.write(f"  \n*_2StPr_Condition_i:*  \n")
    con = _2StPr_conditions['Con_i']
    adj = con['adjustors']
    audit_dict = {}
    audit_dict['Con_i'] = con
    sub_cond = []

    #establish an initial con_key column in the results
    #with 'no data' alongside all shares which have no data
    #else with 'initial' in the column
    con_key='Con_i'

    num_nodata_shares = initialize_condition_column(con_key, results, ov)
    # copy DHPGrAvSh values to it,flagging all initially as FAILing
    update_column_format_and_flag(results, con_key, ov,'DHPGrAvSh',g.FAIL)

    sub_cond.append(f"'DHPGrAvSh' < {adj[0]}")
    sub_cond.append(f"'DHPGrAvLo' > {adj[1]}")
    sub_cond.append("'DMP' > 'DMP'.D-1")
    sub_cond.append("'DMP'.D-3 > 'DMP'.D-2")
    sub_cond.append("'DCP' > 'DOP'")
    full_condition_str = f"`{' AND '.join(sub_cond)}`  \n" 
    report_f.write(full_condition_str)

    mask1 = ov['DHPGrAvSh'] < adj[0] #1
    masked_ov = ov[mask1]
    report_f.write(f"{len(masked_ov)} shares pass sub condition: {sub_cond[0]}  \n")

    mask2 = masked_ov['DHPGrAvLo'] > adj[1] #1
    masked_ov = masked_ov[mask2]
    report_f.write(f"{len(masked_ov)} shares remaining after also passing sub condition: {sub_cond[1]}  \n")

    mask3 = masked_ov['DMP'] > masked_ov['DMP.D-1']
    masked_ov = masked_ov[mask3]
    report_f.write(f"{len(masked_ov)} shares remaining after also passing sub condition: {sub_cond[2]}  \n")

    mask4 = masked_ov['DMP.D-3'] > masked_ov['DMP.D-2']
    masked_ov = masked_ov[mask4]
    report_f.write(f"{len(masked_ov)} shares remaining after also passing sub condition: {sub_cond[3]}  \n")

    mask5 = masked_ov['DCP'] > masked_ov['DOP']
    masked_ov = masked_ov[mask5]
    report_f.write(f"{len(masked_ov)} shares remaining after also passing sub condition: {sub_cond[4]}  \n")

    update_column_format_and_flag(masked_ov,con_key,ov,'DHPGrAvSh',g.PASS)
    if len(masked_ov)>0:
        results.update(masked_ov[con_key])

    return audit_dict

def _2StPr_Condition_j(ov: pd.DataFrame, results: pd.DataFrame, report_f) -> dict:
    ''' Apply Condition j) 2. St. Pr. Conditions to meet to enter the 3. Stage 
    '''

    #print(f'_2St_Condition_j len(results)={len(results)}')
    # 'description': '3 * SBrD / (SBrD-2 + SBrD-3 + SBrD-4 ) > 1.3 OR 1.5 * (SBrD + SBrD-1) / (SBrD-3 + SBrD-4 + SBrD-5) > 1.4',
    # 'notes': 'NO PARAMETERS', 

    report_f.write(f"  \n*_2StPr_Condition_j:*  \n")
    con = _2StPr_conditions['Con_j']
    adj = con['adjustors']
    audit_dict = {}
    audit_dict['Con_j'] = con
    sub_cond = []

    con_key='Con_j'
    #results[con_key] = g.FAIL
    update_column_format_and_flag(results, con_key, ov,'SBr',g.FAIL)
    #num_nodata_shares = initialize_condition_column(con_key, results, ov)

    sub_cond.append(f"({adj[0]}'SBr'/('SBr'.D-2+'SBr'.D-3+'SBr'.D-4))") #1.3"
    sub_cond.append(f"({adj[1]}('SBr'+'SBr'.D-1)/('SBr'.D-3+'SBr'.D-3+'SBr'.D-5))") #1.4"
    full_condition_str = f"`{' OR '.join(sub_cond)}`  \n" 
    report_f.write(full_condition_str)
    report_f.write(f"The greater of the two expressions is shown in the {con_key} column: its flagged PASS or FAIL vs threshold value {adj[2]}  \n")

    # 1) RBrsh D = 3 * SBrD / (SBrD-2 + SBrD-3 + SBrD-4 )
    masked_ov =ov.copy()
    masked_ov['expr1'] = (adj[0]*ov['SBr']/(ov['SBr.D-2']+ov['SBr.D-3']+ov['SBr.D-4']))
    #place 1st expression results entirely in con_key col
    results['expr1'] = 0
    results.update(masked_ov['expr1']) # skips NaN values resulting from the above calc for the 'no data' rows

    # create another column with 2nd expression values
    # 2) RBrsh D = 1.5 * (SBrD + SBrD-1) / (SBrD-3 + SBrD-4 + SBrD-5)
    masked_ov =ov.copy()
    masked_ov['expr2'] = (adj[1]*(ov['SBr']+ov['SBr.D-1'])/(ov['SBr.D-3']+ov['SBr.D-3']+ov['SBr.D-5'])) 
    # slap it onto results df
    results['expr2'] = 0
    results.update(masked_ov['expr2'])

    #now results contains con_key (as yet not correct) plus expr1 and expr2
    #con_key must be updated with the higher of expr1 or expr2

    #first set con_key to the max of expr1, expr2    
    #only want those shares with data 
    # NOTE con_key will still have 'initial' in the col
    shares_with_data = results[results[con_key] != 'no data']
    #print(has_data[[con_key,'expr1','expr2']].head(600))


    #want results con_key column to include where expr2 > expr1
    #step 1 
    # plonk expr2 into con_key if for the share expr2 is greater than expr1
    mask_2g1 = shares_with_data['expr2'] > shares_with_data['expr1']
    data_2gt1 = shares_with_data[mask_2g1]
    data_2gt1[con_key] = data_2gt1['expr2']
    if len(data_2gt1)>0:
        results.update(data_2gt1[con_key])
    #print(results[[con_key,'expr1','expr2']].head(600))
    
    #step 2 
    # plonk expr1 into con_key if for the share expr1 is greater than expr2
    mask_1g2 = shares_with_data['expr2'] <= shares_with_data['expr1']
    data_1gt2 = shares_with_data[mask_1g2]
    data_1gt2[con_key] = data_1gt2['expr1']
    if len(data_1gt2)>0:
        results.update(data_1gt2[con_key])
    #print(results[[con_key,'expr1','expr2']].head(600))

    #con_key now correctly populated with selected higher number

    #PASS or FAIL to end of con_key values based on comparison with adj[2]
    #single out failers 
    failers = results[results[con_key] != 'no data']
    failers = failers[failers[con_key] < adj[2]]

    #single out passers
    passers = results[results[con_key] != 'no data']
    passers = passers[passers[con_key] >= adj[2]]

    #format and append FAIL symbol to the con_key value of the failers
    failers[con_key] = failers[con_key].map('{0:.5f}'.format)
    failers[con_key] = failers[con_key].astype(str) + f' { g.FAIL}'
    results.update(failers[con_key])

    #format and append PASS symbol to the con_key value of the passers
    passers[con_key] = passers[con_key].map('{0:.5f}'.format)
    passers[con_key] = passers[con_key].astype(str) + f' { g.PASS}'
    results.update(passers[con_key])

    #print(results[[con_key,'expr1','expr2']].head(600))

    #remove now unneeded columns
    del(results['expr1'])
    del(results['expr2'])

    return audit_dict

