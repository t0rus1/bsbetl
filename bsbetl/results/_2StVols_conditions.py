""" 
2 St. Vols conditions
"""
from bsbetl import g
from bsbetl.g_helpers import load_prepare_2StVols_conditions, sync_2stVols_conditions_audit_structure


''' DEFAULT CONDITIONS HERE '''
# NOTE all the dict objects below MUST have a 'cond['name']' key!!!!

# region Condition a
_2StVols_cond_a1 = {
    "name": "Con_a1",
    "group": "Con_a",
    "description": "DVFf3D > C2Vca1 AND DHPGrDifD-1 < C2Vca1D AND DHPGrAvshD > C2Vca1A",
    "notes": "C2Vca1 = 1.0 ... 20; C2Vca1Di = 0.000 ... 0.050; C2Vca1A = 0.9500 ... 1.0500",
    "C2Vca1": 2.0,
    "C2Vca1_min": 1.0,
    "C2Vca1_max": 20.0,
    "C2Vca1D": 0.01,
    "C2Vca1D_min": 0.0,
    "C2Vca1D_max": 0.05,
    "C2Vca1A": 1.0,
    "C2Vca1A_min": 0.95,
    "C2Vca1A_max": 1.05,
    "audit_list": [
        "DVFf3",
        "DHPGrDiF.D-1",
        "DHPGrAvSh"
    ],
    "document_ref": "2 Vols 210524.odt: 2. St. Vls. Con a1)"
}
_2StVols_cond_a2 = {
    "name": "Con_a2",
    "group": "Con_a",
    "description": "DVD / SDVBfD-2 > C2Vca2 AND  DHPGrDifD-1 < C2Vca1D AND DHPGrAvshD > C2Vca1A",
    "notes": "C2Vca2 = 1.0 ... 20; C2Vca1Di = 0.000 ... 0.050; C2Vca1A = 0.9500 ... 1.0500",
    "C2Vca2": 2.0,
    "C2Vca2_min": 1.0,
    "C2Vca2_max": 20.0,
    "C2Vca1D": 0.001,
    "C2Vca1D_min": 0.0,
    "C2Vca1D_max": 0.05,
    "C2Vca1A": 0.96,
    "C2Vca1A_min": 0.95,
    "C2Vca1A_max": 1.05,
    "audit_list": [
        "DV",
        "SDVBf.D-2",
        "DHPGrDiF.D-1",
        "DHPGrAvSh"
    ],
    "document_ref": "2 Vols 210524.odt: 2. St. Vls. Con a2)"
}
#endregion

# region Condition b
_2StVols_cond_b = {
    "name": "Con_b",
    "group": "Con_b",
    "description": "DVFf1D > C2Vcb AND DHPGrDifD-1 < C2Vca1D  AND DHPGrAvshD > C2Vca1A",
    "notes": "C2Vcb = 1.0 ... 10; C2Vca1Di = 0.000 ... 0.050; C2Vca1A = 0.9500 ... 1.0500",
    "C2Vcb": 2.0,
    "C2Vcb_min": 1.0,
    "C2Vcb_max": 10.0,
    "C2Vca1D": 0.01,
    "C2Vca1D_min": 0.0,
    "C2Vca1D_max": 0.05,
    "C2Vca1A": 0.96,
    "C2Vca1A_min": 0.95,
    "C2Vca1A_max": 1.05,
    "audit_list": [
        "DVFf1",
        "DHPGrDiF.D-1",
        "DHPGrAvSh"
    ],
    "document_ref": "2 Vols 210524.odt: 2. St. Vls. Con b)"
}
# endregion

#region Condition c
_2StVols_cond_c = {
    "name": "Con_c",
    "group": "Con_c",
    "description": "DVFmD > C2Vcc AND DHPGrDislD-1 < C2VccD AND DHPGrAvmiD > C2VccA",
    "notes": "C2Vcc = 1.00 ... 3.00; C2VccD = 0.0000 ...  0.0500; C2Vcc = 0.9500 ... 1.0500;",
    "C2Vcc": 1.1,
    "C2Vcc_min": 1.0,
    "C2Vcc_max": 3.0,
    "C2VccD": 0.01,
    "C2VccD_min": 0.0,
    "C2VccD_max": 0.05,
    "C2VccA": 0.96,
    "C2VccA_min": 0.95,
    "C2VccA_max": 1.05,
    "audit_list": [
        "DVFm",
        "DHPGrDiSl.D-1",
        "DHPGrAvMi"
    ],
    "document_ref": "2 Vols 210524.odt: 2. St. Vls. Con c)"
}
#endregion

#region Condition d
_2StVols_cond_d = {
    "name": "Con_d",
    "group": "Con_d",
    "description": "DVFsl D > C2Vcd  AND DHPGrDislD-1 < C2VcdD AND DHPGrAvloD > C2VcdA",
    "notes": "C2Vcd = 1.00 ...1.50; C2VcdD = 0.0000 ...  0.0500; C2VcdA = 0.9500 ... 1.0500",
    "C2Vcd": 1.1,
    "C2Vcd_min": 1.0,
    "C2Vcd_max": 1.5,
    "C2VcdD": 0.001,
    "C2VcdD_min": 0.0,
    "C2VcdD_max": 0.05,
    "C2VcdA": 0.96,
    "C2VcdA_min": 0.95,
    "C2VcdA_max": 1.05,
    "audit_list": [
        "DVFsl",
        "DHPGrDiSl.D-1",
        "DHPGrAvLo"
    ],
    "document_ref": "2 Vols 210524.odt: 2. St. Vls. Con d)"
}
#endregion

#region Condition e
_2StVols_cond_e = {
    "name": "Con_e",
    "group": "Con_e",
    "description": "{100} * DVFf2D *  [(DHPD + DHPD-1) / (DHPD-2 + DHPD-3) -1 ] > {3}",
    "notes": "NO PARAMETERS",
    "audit_list": [
        "DVFf2",
        "DHP",
        "DHP.D-1",
        "DHP.D-2",
        "DHP.D-3"
    ],
    "adjustors": [
        100,
        3
    ],
    "document_ref": "2 Vols 210524.odt: 2. St. Vls. Con e)"
}
#endregion

#region Condition f
_2StVols_cond_f = {
    "name": "Con_f",
    "group": "Con_f",
    "description": "{100} * DVD / SDVCf2 D-1 * (DHPD / DHPD-1 - 1)  > {3}",
    "notes": "NO PARAMETERS",
    "audit_list": [
        "DV",
        "SDVCf2.D-1",
        "DHP",
        "DHP.D-1"
    ],
    "adjustors": [
        100,
        3
    ],
    "document_ref": "2 Vols 210524.odt: 2. St. Vls. Con f)"
}
#endregion

# place all the above individual conditions here
default_2StVols_conditions = [
    _2StVols_cond_a1,
    _2StVols_cond_a2,
    _2StVols_cond_b,
    _2StVols_cond_c,
    _2StVols_cond_d,
    _2StVols_cond_e,
    _2StVols_cond_f,
]

def _2StVols_min_max_value_condition(cond :dict) ->list:
    ''' retrieve the min,max,current value and setting_name as a tuple from the dp_init_conditions '''

    # giant case statement
    # temp clipboard:
    #(cond['_min'],cond['_max'],cond[''],'')

    if cond['name'] == 'Con_a1':
        return [(cond['C2Vca1_min'],cond['C2Vca1_max'],cond['C2Vca1'],'C2Vca1'),
                (cond['C2Vca1D_min'],cond['C2Vca1D_max'],cond['C2Vca1D'],'C2Vca1D'),
                (cond['C2Vca1A_min'],cond['C2Vca1A_max'],cond['C2Vca1A'],'C2Vca1A')
                ]
    if cond['name'] == 'Con_a2':
        return [(cond['C2Vca2_min'],cond['C2Vca2_max'],cond['C2Vca2'],'C2Vca2'),
                (cond['C2Vca1D_min'],cond['C2Vca1D_max'],cond['C2Vca1D'],'C2Vca1D'),
                (cond['C2Vca1A_min'],cond['C2Vca1A_max'],cond['C2Vca1A'],'C2Vca1A')
                ]
    if cond['name'] == 'Con_b':
        return [(cond['C2Vcb_min'],cond['C2Vcb_max'],cond['C2Vcb'],'C2Vcb'),
                (cond['C2Vca1D_min'],cond['C2Vca1D_max'],cond['C2Vca1D'],'C2Vca1D'),
                (cond['C2Vca1A_min'],cond['C2Vca1A_max'],cond['C2Vca1A'],'C2Vca1A')
                ]
    if cond['name'] == 'Con_c':
        return [(cond['C2Vcc_min'],cond['C2Vcc_max'],cond['C2Vcc'],'C2Vcc'),
                (cond['C2VccD_min'],cond['C2VccD_max'],cond['C2VccD'],'C2VccD'),
                (cond['C2VccA_min'],cond['C2VccA_max'],cond['C2VccA'],'C2VccA')
                ]
    if cond['name'] == 'Con_d':
        return [(cond['C2Vcd_min'],cond['C2Vcd_max'],cond['C2Vcd'],'C2Vcd'),
                (cond['C2VcdD_min'],cond['C2VcdD_max'],cond['C2VcdD'],'C2VcdD'),
                (cond['C2VcdA_min'],cond['C2VcdA_max'],cond['C2VcdA'],'C2VcdA')
                ]
    # the rest
    return [(0,0,0,'?')]


_2StVols_conditions = load_prepare_2StVols_conditions(g._2STVOLS_CONDITIONS_FQ, default_2StVols_conditions)

# force sync the assoc audit structure
sync_2stVols_conditions_audit_structure(_2StVols_conditions)