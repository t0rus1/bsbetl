from bsbetl.helpers import copy_column_format_and_flag, format_and_flag, initialize_condition_column, update_column_format_and_flag
from io import FileIO
import random
import pandas as pd
from bsbetl import g
from bsbetl.func_helpers import add_df_columns, report_all_fail, report_ov_shares_passing
from bsbetl.results._2StVols_conditions import _2StVols_conditions

''' Functions for applying various 1st Stage Conditions to the Ov table '''

def _2StVols_Condition_a1(ov: pd.DataFrame, results: pd.DataFrame, report_f) -> dict:
    ''' Apply Condition 2. St. Vls. In. : Conditions to meet to enter the 3. Stage 
    '''

    report_f.write("  \n*_2StVols_Condition_a1:*  \n")

    con = _2StVols_conditions['Con_a1']
    audit_dict = {}
    audit_dict['Con_a1'] = con
    con_key='Con_a1'

    #add Con_a1 col to results filled with NaN
    num_nodata_shares = initialize_condition_column(con_key, results, ov)
    #overlay Con_a1 col with DVFf3 from ov, flagged as FAIL initially
    update_column_format_and_flag(results,con_key,ov,'DVFf3',g.FAIL)

    #adj = _2StVols_conditions['Con_a1']['adjustors']
    mask1_str = f"DVFf3 > {con['C2Vca1']}"
    mask2_str = f"DHPGrDiF.D-1 < {con['C2Vca1D']}"
    mask3_str = f"DHPGrAvSh > {con['C2Vca1A']}"
    # note the backticks (MarkDown)
    full_condition_str = f"`{mask1_str}  AND {mask2_str} AND {mask3_str}`  \n"

    report_f.write(full_condition_str)

    mask = ov['DVFf3'] > con['C2Vca1']
    masked_ov = ov[mask]
    if len(masked_ov.index) > 0:
        #report_f.write(f"{len(masked_ov.index)} shares pass {mask_str}  \n")
        mask = masked_ov['DHPGrDiF.D-1'] < con['C2Vca1D']
        masked_ov = masked_ov[mask]
        if len(masked_ov.index) > 0:
            #report_f.write(f"{len(masked_ov.index)} shares pass {mask1_str} AND {mask2_str}  \n")
            mask = masked_ov['DHPGrAvSh'] > con['C2Vca1A']
            masked_ov = masked_ov[mask].copy()
            if len(masked_ov.index) > 0:
                report_f.write(f"{len(masked_ov.index)} shares pass this condition  \n")
                update_column_format_and_flag(masked_ov,con_key,ov,'DVFf3',g.PASS)
                results.update(masked_ov[con_key])
            else:
                report_all_fail(report_f,f'this condition')
        else:
            report_all_fail(report_f,f'{mask1_str} AND {mask2_str} - no further sub-conditions tested' )
    else:
        report_all_fail(report_f,f'{mask1_str} - no further sub-conditions tested' )

    return audit_dict

def _2StVols_Condition_a2(ov: pd.DataFrame, results: pd.DataFrame, report_f) -> dict:
    ''' Apply Condition 2. St. Vls. In. : Conditions to meet to enter the 3. Stage 
    '''

    report_f.write("  \n*_2StVols_Condition_a2:*  \n")
    con_key = 'Con_a2'
    con = _2StVols_conditions[con_key]
    audit_dict = {}
    audit_dict['Con_a2'] = con

    #add Con_a2 col to results filled with NaN
    num_nodata_shares = initialize_condition_column(con_key, results, ov)
    #overlay Con_a2 col with DV/SDVBf.D-2 from ov, flagged as FAIL initially
    results[con_key] = ov['DV']/ov['SDVBf.D-2']
    format_and_flag(results,con_key,g.FAIL)


    mask1_str = f"DV/SDVBf.D-2 > {con['C2Vca2']}"
    mask2_str = f"DHPGrDiF.D-1 < {con['C2Vca1D']}"
    mask3_str = f"DHPGrAvSh > {con['C2Vca1A']}"
    # note the backticks (MarkDown)
    full_condition_str = f"`{mask1_str}  AND {mask2_str} AND {mask3_str}`  \n"
    report_f.write(full_condition_str)


    mask = ov['DV']/ov['SDVBf.D-2'] > con['C2Vca2']
    masked_ov = ov[mask]
    if len(masked_ov.index) > 0:
        mask = masked_ov['DHPGrDiF.D-1'] < con['C2Vca1D']
        masked_ov = masked_ov[mask]
        if len(masked_ov.index) > 0:
            mask = masked_ov['DHPGrAvSh'] > con['C2Vca1A']
            masked_ov = masked_ov[mask].copy()
            if len(masked_ov.index) > 0:
                report_f.write(f"{len(masked_ov.index)} shares pass this condition  \n")
                masked_ov[con_key] = ov['DV']/ov['SDVBf.D-2']
                format_and_flag(masked_ov,con_key,g.PASS)
                results.update(masked_ov[con_key])
            else:
                report_all_fail(report_f,f'this condition')
        else:
            report_all_fail(report_f,f'{mask1_str} AND {mask2_str} - no further sub-conditions tested' )
    else:
        report_all_fail(report_f,f'{mask1_str} - no further sub-conditions tested' )

    return audit_dict


def _2StVols_Condition_b(ov: pd.DataFrame, results: pd.DataFrame, report_f) -> dict:
    ''' Apply Condition 2. St. Vls. In. : Conditions to meet to enter the 3. Stage 
    '''

    report_f.write(f"  \n*_2StVols_Condition_b:*  \n")
    audit_dict = {}
    con_key='Con_b'
    con = _2StVols_conditions[con_key]
    audit_dict[con_key] = con

    #add Con_b col to results filled with NaN
    num_nodata_shares = initialize_condition_column(con_key, results, ov)
    #overlay Con_b col with DVFf1/C2Vcb flagged as FAIL initially
    results[con_key] = ov['DVFf1']/con['C2Vcb']
    format_and_flag(results,con_key,g.FAIL)

    mask1_str = f"DVFf1 > {con['C2Vcb']}"
    mask2_str = f"DHPGrDiF.D-1 < {con['C2Vca1D']}"
    mask3_str = f"DHPGrAvSh > {con['C2Vca1A']}"

    # note the backticks (MarkDown)
    full_condition_str = f"`{mask1_str}  AND {mask2_str} AND {mask3_str}`  \n"
    report_f.write(full_condition_str)

    mask = ov['DVFf1'] > con['C2Vcb']
    masked_ov = ov[mask]
    if len(masked_ov.index) > 0:
        mask = masked_ov['DHPGrDiF.D-1'] < con['C2Vca1D']
        masked_ov = masked_ov[mask]
        if len(masked_ov.index) > 0:
            mask = masked_ov['DHPGrAvSh'] > con['C2Vca1A']
            masked_ov = masked_ov[mask].copy()
            if len(masked_ov.index) > 0:
                report_f.write(f"{len(masked_ov.index)} shares pass this condition  \n")
                masked_ov[con_key] = ov['DVFf1']  #/con['C2Vcb']
                format_and_flag(masked_ov,con_key,g.PASS)
                results.update(masked_ov[con_key])
            else:
                report_all_fail(report_f,f'this condition' )
        else:
            report_all_fail(report_f,f'{mask1_str} AND {mask2_str} - no further sub-conditions tested' )
    else:
        report_all_fail(report_f,f'{mask1_str} - no further sub-conditions tested' )

    return audit_dict


def _2StVols_Condition_c(ov: pd.DataFrame, results: pd.DataFrame, report_f) -> dict:
    ''' Apply Condition 2. St. Vls. In. : Conditions to meet to enter the 3. Stage 
    '''

    report_f.write(f"  \n*_2StVols_Condition_c:*  \n")
    con_key = 'Con_c'
    con = _2StVols_conditions[con_key]
    audit_dict = {}
    audit_dict[con_key] = con

    #add Con_c col to results filled with NaN
    num_nodata_shares = initialize_condition_column(con_key, results, ov)
    #overlay Con_c col with DVFm from ov, flagged as FAIL initially
    results[con_key] = ov['DVFm']
    format_and_flag(results,con_key,g.FAIL)

    mask1_str=f"DVFm > {con['C2Vcc']}"
    mask2_str = f"DHPGrDiSl.D-1 < {con['C2VccD']}"
    mask3_str = f"'DHPGrAvMi' > {con['C2VccA']}"
    # note the backticks (MarkDown)
    full_condition_str = f"`{mask1_str}  AND {mask2_str} AND {mask3_str}`  \n"
    report_f.write(full_condition_str)

    mask = ov['DVFm'] > con['C2Vcc']
    masked_ov = ov[mask]
    if len(masked_ov.index) > 0:
        mask = masked_ov['DHPGrDiSl.D-1'] < con['C2VccD']
        masked_ov = masked_ov[mask]
        if len(masked_ov.index) > 0:
            mask = masked_ov['DHPGrAvMi'] > con['C2VccA']
            masked_ov = masked_ov[mask].copy()
            if len(masked_ov.index) > 0:
                report_f.write(f"{len(masked_ov.index)} shares pass this condition  \n")
                masked_ov[con_key] = ov['DVFm']
                copy_column_format_and_flag(masked_ov,con_key,con_key,g.PASS)
                results.update(masked_ov[con_key])
            else:
                report_all_fail(report_f,'this condition')
        else:
            #this condition completely failed,
            report_all_fail(report_f,f'{mask1_str} AND {mask2_str} - no further sub-conditions tested' )
    else:
        #this condition completely failed
        report_all_fail(report_f,f'{mask1_str} - no further sub-conditions tested' )

    return audit_dict


def _2StVols_Condition_d(ov: pd.DataFrame, results: pd.DataFrame, report_f) -> dict:
    ''' Apply Condition 2. St. Vls. In. : Conditions to meet to enter the 3. Stage 
    '''

    report_f.write("  \n*_2StVols_Condition_d:*  \n")
    con_key='Con_d'
    con = _2StVols_conditions[con_key]
    audit_dict = {}
    audit_dict[con_key] = con

    #add Con_d col to results filled with NaN
    num_nodata_shares = initialize_condition_column(con_key, results, ov)
    #overlay Con_d col with 'DVFsl' from ov, flagged as FAIL initially
    results[con_key] = ov['DVFsl']
    format_and_flag(results,con_key,g.FAIL)

    mask1_str = f"DVFsl > {con['C2Vcd']}"
    mask2_str = f"DHPGrDiSl.D-1 < {con['C2VcdD']}"
    mask3_str = f"DHPGrAvLo > {con['C2VcdA']}"
    # note the backticks (MarkDown)
    full_condition_str = f"`{mask1_str}  AND {mask2_str} AND {mask3_str}`  \n"
    report_f.write(full_condition_str)

    mask = ov['DVFsl'] > con['C2Vcd']
    masked_ov = ov[mask]
    if len(masked_ov.index) > 0:
        mask = masked_ov['DHPGrDiSl.D-1'] < con['C2VcdD']
        masked_ov = masked_ov[mask]
        if len(masked_ov.index) > 0:
            mask = masked_ov['DHPGrAvLo'] > con['C2VcdA']
            masked_ov = masked_ov[mask].copy()
            if len(masked_ov.index) > 0:
                report_f.write(f"{len(masked_ov.index)} shares pass this condition  \n")
                masked_ov[con_key] = ov['DVFsl']
                copy_column_format_and_flag(masked_ov,con_key,con_key,g.PASS)
                results.update(masked_ov[con_key])
            else:
                #this condition completely failed
                report_all_fail(report_f,'this condition')
        else:
            report_all_fail(report_f,f"{mask1_str} for {mask2_str}")
    else:
        #this condition completely failed
        report_all_fail(report_f,f'{mask1_str} - no further sub-conditions tested' )

    return audit_dict


def _2StVols_Condition_e(ov: pd.DataFrame, results: pd.DataFrame, report_f) -> dict:
    ''' Apply Condition 2. St. Vls. In. : Conditions to meet to enter the 3. Stage 
    '''

    #print(f'_2StVols_Condition_e len(results)={len(results)}')
    # 'description': '{100} * DVFf2 D *  [(DHPD + DHPD-1) / (DHPD-2 + DHPD-3) -1 ] > {3}',
    # 'notes': 'NO PARAMETERS',

    report_f.write(f"  \n*_2StVols_Condition_e*  \n")
    con_key='Con_e'
    con = _2StVols_conditions[con_key]
    audit_dict = {}
    audit_dict[con_key] = con
    adj = con['adjustors']

    #add Con_d col to results filled with NaN
    num_nodata_shares = initialize_condition_column(con_key, results, ov)
    #overlay Con_d col with calc from ov, flagged as FAIL initially
    results[con_key] = ov['DVFf2'] #adj[0]*ov['DVFf2'] *((ov['DHP'] + ov['DHP.D-1'])/(ov['DHP.D-2']+ov['DHP.D-3'])-1)
    format_and_flag(results,con_key,g.FAIL)

    mask1_str=f"{adj[0]}*DVFf2 * ((DHP + DHP.D-1)/(DHP.D-2 + DHP.D-3)-1) > {adj[1]}"
    # note the backticks (MarkDown)
    full_condition_str = f"`{mask1_str}`  \n"
    report_f.write(full_condition_str)

    mask = adj[0]*ov['DVFf2'] * ((ov['DHP'] + ov['DHP.D-1'])/(ov['DHP.D-2'] + ov['DHP.D-3'])-1) > adj[1]
    masked_ov = ov[mask].copy()
    if len(masked_ov.index) > 0:
        report_f.write(f"{len(masked_ov.index)} shares pass this condition  \n")
        masked_ov[con_key] = adj[0]*ov['DVFf2'] * ((ov['DHP'] + ov['DHP.D-1'])/(ov['DHP.D-2'] + ov['DHP.D-3'])-1)
        copy_column_format_and_flag(masked_ov,con_key,con_key,g.PASS)
        results.update(masked_ov[con_key])
    else:
        report_all_fail(report_f,'this condition')

    return audit_dict

def _2StVols_Condition_f(ov: pd.DataFrame, results: pd.DataFrame, report_f) -> dict:
    ''' Apply Condition 2. St. Vls. In. : Conditions to meet to enter the 3. Stage 
    '''

    report_f.write(f"  \n*_2StVols_Condition_f*  \n")
    con_key = 'Con_f'
    con = _2StVols_conditions[con_key]
    audit_dict = {}
    audit_dict[con_key] = con
    adj = con['adjustors']

    #add Con_f col to results filled with NaN
    num_nodata_shares = initialize_condition_column(con_key, results, ov)
    #overlay Con_f col with calc from ov, flagged as FAIL initially
    results[con_key] = ov['DV'] #adj[0] * (ov['DV']/ov['SDVCf2.D-1']) * ((ov['DHP']/ov['DHP.D-1'])-1)
    format_and_flag(results,con_key,g.FAIL)

    mask1_str = f"{adj[0]} * (ov['DV']/ov['SDVCf2.D-1']) * ((ov['DHP']/ov['DHP.D-1'])-1) > {adj[1]}"    
    # note the backticks (MarkDown)
    full_condition_str = f"`{mask1_str}`  \n"
    report_f.write(full_condition_str)

    mask = adj[0] * (ov['DV']/ov['SDVCf2.D-1']) * ((ov['DHP']/ov['DHP.D-1'])-1) > adj[1]
    masked_ov = ov[mask].copy()
    if len(masked_ov.index) > 0:
        report_f.write(f"{len(masked_ov.index)} shares pass this condition  \n")
        masked_ov[con_key] = adj[0] * (ov['DV']/ov['SDVCf2.D-1']) * ((ov['DHP']/ov['DHP.D-1'])-1)
        copy_column_format_and_flag(masked_ov,con_key,con_key,g.PASS)
        results.update(masked_ov[con_key])
    else:
        report_all_fail(report_f,'this condition')

    return audit_dict
