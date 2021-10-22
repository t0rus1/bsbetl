''' 2. St. Pr. Conditions to meet to enter the 3. Stage '''

from bsbetl.g_helpers import load_prepare_2StPr_conditions, sync_2StPr_audit_structure
from bsbetl import g

#region cond_a
_2StPr_cond_a1 = {
    "name": "Con_a1",
    "group": "Con_a",
    "description": "DaysDHPlasthi simply displayed",
    "notes": "NO PARAMETERS",
    "audit_list": [
        "DaysDHPlasthi"
    ],
    "adjustors": [],
    "document_ref": "2 Prices 210701.odt: 2. Pr In. Con. a2)"
}

_2StPr_cond_a2 = {
    "name": "Con_a2",
    "group": "Con_a",
    "description": "DaysDHPlasthi3perc simply displayed",
    "notes": "NO PARAMETERS",
    "audit_list": [
        "DaysDHPlasthi3perc"
    ],
    "adjustors": [],
    "document_ref": "2 Prices 210701.odt: 2. Pr In. Con. a2)"
}

_2StPr_cond_a3 = {
    "name": "Con_a3",
    "group": "Con_a",
    "description": "DaysDHPlast20hi simply displayed",
    "notes": "NO PARAMETERS",
    "audit_list": [
        "DaysDHPlast20hi"
    ],
    "adjustors": [],
    "document_ref": "2 Prices 210701.odt: 2. Pr In. Con. a3)"
}
#endregion

#region cond_b
_2StPr_cond_b1 = {
    "name": "Con_b1",
    "group": "Con_b",
    "description": "(DHPD / DHOCPD)e2Pcb > C2Pcb",
    "notes": "C2Pcb  = 1.00 ... 1.20; e2Pcb=0.3; applies when DHP between 0 and 0.1999",
    "exponent": 0.3,
    "DHPd_from": 0.0,
    "DHPd_to": 0.1999,
    "C2Pcb": 1.03,
    "C2Pcb_min": 0.0,
    "C2Pcb_max": 1.2,
    "audit_list": [
        "DHP",
        "DHOCP"
    ],
    "document_ref": "2 Prices 210701.odt: 2. Pr In. Con. b1)"
}

_2StPr_cond_b2 = {
    "name": "Con_b2",
    "group": "Con_b",
    "description": "(DHPD / DHOCPD)**e2Pcb > C2Pcb",
    "notes": "C2Pcb  = 1.00 ... 1.20; e2Pcb=0.4; applies when DHP between 0.2 and 0.3999",
    "exponent": 0.4,
    "DHPd_from": 0.2,
    "DHPd_to": 0.3999,
    "C2Pcb": 1.03,
    "C2Pcb_min": 0.0,
    "C2Pcb_max": 1.2,
    "audit_list": [
        "DHP",
        "DHOCP"
    ],
    "document_ref": "2 Prices 210701.odt: 2. Pr In. Con. b2)"
}

_2StPr_cond_b3 = {
    "name": "Con_b3",
    "group": "Con_b",
    "description": "(DHPD / DHOCPD)**e2Pcb > C2Pcb",
    "notes": "C2Pcb  = 1.00 ... 1.20; e2Pcb=0.6; applies when DHP between 0.4 and 0.6999",
    "exponent": 0.6,
    "DHPd_from": 0.4,
    "DHPd_to": 0.6999,
    "C2Pcb": 1.03,
    "C2Pcb_min": 0.0,
    "C2Pcb_max": 1.2,
    "audit_list": [
        "DHP",
        "DHOCP"
    ],
    "document_ref": "2 Prices 210701.odt: 2. Pr In. Con. b3)"
}

_2StPr_cond_b4 = {
    "name": "Con_b4",
    "group": "Con_b",
    "description": "(DHPD / DHOCPD)**e2Pcb > C2Pcb",
    "notes": "C2Pcb  = 1.00 ... 1.20; e2Pcb=0.85; applies when DHP between 0.7 and 1.1999",
    "exponent": 0.85,
    "DHPd_from": 0.7,
    "DHPd_to": 1.1999,
    "C2Pcb": 1.03,
    "C2Pcb_min": 0.0,
    "C2Pcb_max": 1.2,
    "audit_list": [
        "DHP",
        "DHOCP"
    ],
    "document_ref": "2 Prices 210701.odt: 2. Pr In. Con. b4)"
}

_2StPr_cond_b5 = {
    "name": "Con_b5",
    "group": "Con_b",
    "description": "(DHPD / DHOCPD)**e2Pcb > C2Pcb",
    "notes": "C2Pcb  = 1.00 ... 1.20; e2Pcb=1; applies when DHP between 1.2 and higher",
    "exponent": 1.0,
    "DHPd_from": 1.2,
    "DHPd_to": 1000000,
    "C2Pcb": 1.03,
    "C2Pcb_min": 0.0,
    "C2Pcb_max": 1.2,
    "audit_list": [
        "DHP",
        "DHOCP"
    ],
    "document_ref": "2 Prices 210701.odt: 2. Pr In. Con. b5)"
}
#endregion cond_b

#region cond_c
_2StPr_cond_c1 = {
    "name": "Con_c1",
    "group": "Con_c",
    "description": "(DHPD / DHPD-1)**e2Pcb > C2Pcc",
    "notes": "C2Pcc  = 1.00 ... 1.20; e2Pcb=0.3; applies when DHP between 0 and 0.1999",
    "exponent": 0.3,
    "DHPd_from": 0.0,
    "DHPd_to": 0.1999,
    "C2Pcc": 1.03,
    "C2Pcc_min": 0.0,
    "C2Pcc_max": 1.2,
    "audit_list": [
        "DHP",
        "DHP.D-1"
    ],
    "document_ref": "2 Prices 210701.odt: 2. Pr In. Con. c1)"
}

_2StPr_cond_c2 = {
    "name": "Con_c2",
    "group": "Con_c",
    "description": "(DHPD / DHPD-1)**e2Pcb > C2Pcc",
    "notes": "C2Pcc  = 1.00 ... 1.20; e2Pcb=0.4; applies when DHP between 0.2 and 0.3999",
    "exponent": 0.4,
    "DHPd_from": 0.2,
    "DHPd_to": 0.3999,
    "C2Pcc": 1.03,
    "C2Pcc_min": 0.0,
    "C2Pcc_max": 1.2,
    "audit_list": [
        "DHP",
        "DHP.D-1"
    ],
    "document_ref": "2 Prices 210701.odt: 2. Pr In. Con. c2)"
}

_2StPr_cond_c3 = {
    "name": "Con_c3",
    "group": "Con_c",
    "description": "(DHPD / DHPD-1)**e2Pcb > C2Pcc",
    "notes": "C2Pcc  = 1.00 ... 1.20; e2Pcb=0.6; applies when DHP between 0.6 and 0.6999",
    "exponent": 0.6,
    "DHPd_from": 0.4,
    "DHPd_to": 0.6999,
    "C2Pcc": 1.03,
    "C2Pcc_min": 0.0,
    "C2Pcc_max": 1.2,
    "audit_list": [
        "DHP",
        "DHP.D-1"
    ],
    "document_ref": "2 Prices 210701.odt: 2. Pr In. Con. c3)"
}

_2StPr_cond_c4 = {
    "name": "Con_c4",
    "group": "Con_c",
    "description": "(DHPD / DHPD-1)**e2Pcb > C2Pcc",
    "notes": "C2Pcc  = 1.00 ... 1.20; e2Pcb=0.85; applies when DHP between 0.7 and 1.1999",
    "exponent": 0.85,
    "DHPd_from": 0.7,
    "DHPd_to": 1.1999,
    "C2Pcc": 1.03,
    "C2Pcc_min": 0.0,
    "C2Pcc_max": 1.2,
    "audit_list": [
        "DHP",
        "DHP.D-1"
    ],
    "document_ref": "2 Prices 210701.odt: 2. Pr In. Con. c4)"
}

_2StPr_cond_c5 = {
    "name": "Con_c5",
    "group": "Con_c",
    "description": "(DHPD / DHPD-1)**e2Pcb > C2Pcc",
    "notes": "C2Pcc  = 1.00 ... 1.20; e2Pcb=1; applies when DHP between 1.2 and higher",
    "exponent": 1.0,
    "DHPd_from": 1.2,
    "DHPd_to": 1000000,
    "C2Pcc": 1.03,
    "C2Pcc_min": 0.0,
    "C2Pcc_max": 1.2,
    "audit_list": [
        "DHP",
        "DHP.D-1"
    ],
    "document_ref": "2 Prices 210701.odt: 2. Pr In. Con. c5)"
}
#endregion

#region cond_d
_2StPr_cond_d1 = {
    "name": "Con_d1",
    "group": "Con_d",
    "description": "(DHPD / DHPD-2)**e2Pcb > C2Pcd",
    "notes": "C2Pcd  = 1.00 ... 1.20; e2Pcb=0.3; applies when DHP between 0 and 0.1999",
    "exponent": 0.3,
    "DHPd_from": 0.0,
    "DHPd_to": 0.1999,
    "C2Pcd": 1.05,
    "C2Pcd_min": 0.0,
    "C2Pcd_max": 1.2,
    "audit_list": [
        "DHP",
        "DHP.D-2"
    ],
    "document_ref": "2 Prices 210701.odt: 2. Pr In. Con. d1)"
}

_2StPr_cond_d2 = {
    "name": "Con_d2",
    "group": "Con_d",
    "description": "(DHPD / DHPD-2)**e2Pcb > C2Pcd",
    "notes": "C2Pcd  = 1.00 ... 1.20; e2Pcb=0.4; applies when DHP between 0.2 and 0.3999",
    "exponent": 0.4,
    "DHPd_from": 0.2,
    "DHPd_to": 0.3999,
    "C2Pcd": 1.05,
    "C2Pcd_min": 0.0,
    "C2Pcd_max": 1.2,
    "audit_list": [
        "DHP",
        "DHP.D-2"
    ],
    "document_ref": "2 Prices 210701.odt: 2. Pr In. Con. d2)"
}

_2StPr_cond_d3 = {
    "name": "Con_d3",
    "group": "Con_d",
    "description": "(DHPD / DHPD-2)**e2Pcb > C2Pcd",
    "notes": "C2Pcd  = 1.00 ... 1.20; e2Pcb=0.6; applies when DHP between 0.4 and 0.6999",
    "exponent": 0.6,
    "DHPd_from": 0.4,
    "DHPd_to": 0.6999,
    "C2Pcd": 1.05,
    "C2Pcd_min": 0.0,
    "C2Pcd_max": 1.2,
    "audit_list": [
        "DHP",
        "DHP.D-2"
    ],
    "document_ref": "2 Prices 210701.odt: 2. Pr In. Con. d3)"
}

_2StPr_cond_d4 = {
    "name": "Con_d4",
    "group": "Con_d",
    "description": "(DHPD / DHPD-2)**e2Pcb > C2Pcd",
    "notes": "C2Pcd  = 1.00 ... 1.20; e2Pcb=0.85; applies when DHP between 0.7 and 1.1999",
    "exponent": 0.85,
    "DHPd_from": 0.7,
    "DHPd_to": 1.1999,
    "C2Pcd": 1.05,
    "C2Pcd_min": 0.0,
    "C2Pcd_max": 1.2,
    "audit_list": [
        "DHP",
        "DHP.D-2"
    ],
    "document_ref": "2 Prices 210701.odt: 2. Pr In. Con. d4)"
}

_2StPr_cond_d5 = {
    "name": "Con_d5",
    "group": "Con_d",
    "description": "(DHPD / DHPD-2)**e2Pcb > C2Pcd",
    "notes": "C2Pcd  = 1.00 ... 1.20; e2Pcb=1; applies when DHP between 1.2 and higher",
    "exponent": 1,
    "DHPd_from": 1.2,
    "DHPd_to": 1000000,
    "C2Pcd": 1.05,
    "C2Pcd_min": 0.0,
    "C2Pcd_max": 1.2,
    "audit_list": [
        "DHP",
        "DHP.D-2"
    ],
    "document_ref": "2 Prices 210701.odt: 2. Pr In. Con. d5)"
}
#endregion

#region cond_e
_2StPr_cond_e1 = {
    "name": "Con_e1",
    "group": "Con_e",
    "description": "(DHPD / DHPD-3)**e2Pcb > C2Pce",
    "notes": "C2Pce  = 1.00 ... 1.20; e2Pcb=0.3; applies when DHP between 0 and 0.1999",
    "exponent": 0.3,
    "DHPd_from": 0.0,
    "DHPd_to": 0.1999,
    "C2Pce": 1.07,
    "C2Pce_min": 0.0,
    "C2Pce_max": 1.2,
    "audit_list": [
        "DHP",
        "DHP.D-3"
    ],
    "document_ref": "2 Prices 210701.odt: 2. Pr In. Con. e1)"
}

_2StPr_cond_e2 = {
    "name": "Con_e2",
    "group": "Con_e",
    "description": "(DHPD / DHPD-3)**e2Pcb > C2Pce",
    "notes": "C2Pce  = 1.00 ... 1.20; e2Pcb=0.4; applies when DHP between 0.2 and 0.3999",
    "exponent": 0.4,
    "DHPd_from": 0.2,
    "DHPd_to": 0.3999,
    "C2Pce": 1.07,
    "C2Pce_min": 0.0,
    "C2Pce_max": 1.2,
    "audit_list": [
        "DHP",
        "DHP.D-3"
    ],
    "document_ref": "2 Prices 210701.odt: 2. Pr In. Con. e2)"
}

_2StPr_cond_e3 = {
    "name": "Con_e3",
    "group": "Con_e",
    "description": "(DHPD / DHPD-3)**e2Pcb > C2Pce",
    "notes": "C2Pce  = 1.00 ... 1.20; e2Pcb=0.6; applies when DHP between 0.4 and 0.6999",
    "exponent": 0.6,
    "DHPd_from": 0.4,
    "DHPd_to": 0.6999,
    "C2Pce": 1.07,
    "C2Pce_min": 0.0,
    "C2Pce_max": 1.2,
    "audit_list": [
        "DHP",
        "DHP.D-3"
    ],
    "document_ref": "2 Prices 210701.odt: 2. Pr In. Con. e3)"
}

_2StPr_cond_e4 = {
    "name": "Con_e4",
    "group": "Con_e",
    "description": "(DHPD / DHPD-3)**e2Pcb > C2Pce",
    "notes": "C2Pce  = 1.00 ... 1.20; e2Pcb=0.85; applies when DHP between 0.7 and 1.1999",
    "exponent": 0.85,
    "DHPd_from": 0.7,
    "DHPd_to": 1.1999,
    "C2Pce": 1.07,
    "C2Pce_min": 0.0,
    "C2Pce_max": 1.2,
    "audit_list": [
        "DHP",
        "DHP.D-3"
    ],
    "document_ref": "2 Prices 210701.odt: 2. Pr In. Con. e4)"
}

_2StPr_cond_e5 = {
    "name": "Con_e5",
    "group": "Con_e",
    "description": "(DHPD / DHPD-3)**e2Pcb > C2Pce",
    "notes": "C2Pce  = 1.00 ... 1.20; e2Pcb=1; applies when DHP between 1.2 and higher",
    "exponent": 1,
    "DHPd_from": 1.2,
    "DHPd_to": 1000000,
    "C2Pce": 1.07,
    "C2Pce_min": 0.0,
    "C2Pce_max": 1.2,
    "audit_list": [
        "DHP",
        "DHP.D-3"
    ],
    "document_ref": "2 Prices 210701.odt: 2. Pr In. Con. e5)"
}
#endregion

# region condition f
_2StPr_cond_f = {
    "name": "Con_f",
    "group": "Con_f",
    "description": "(DHPGrAvlo D > C2Pcf) AND (DCP < {1.05} * DOPD-1)",
    "notes": "C2Pcf = 0.90 ...1.10",
    "C2Pcf": 0.98,
    "C2Pcf_min": 0.9,
    "C2Pcf_max": 1.1,
    "audit_list": [
        "DHPGrAvLo",
        "DCP",
        "DOP.D-1"
    ],
    "adjustors": [
        1.05
    ],
    "document_ref": "2 Prices 210701.odt: 2. Pr In. Con. f)"
}
# endregion

#region cond_g
_2StPr_cond_g = {    
    "name": "Con_g",
    "group": "Con_g",
    "description": "(DHPGr > C2Pcgs) AND (DHPGrAvshD-1 < C2Pcgb) AND ((DHPGrAvsh D / DHPGrAvsh D-1) > C2PcgA) AND ((DHPGrAvsh D / DHPGrAvsh D-2) > C2PcgA) AND (DHPGrDifD-1 < C2PcgD)",
    "notes": "C2Pcgs = 0.9500 ... 1.0500; C2Pcgb = 0.9000 ... 1.0500; C2PcgA   = 1.000 ... 1.050; C2PcgD  = 0.0000 ...0.1000",
    "C2Pcgs": 1.02,
    "C2Pcgs_min": 0.95,
    "C2Pcgs_max": 1.05,
    "C2Pcgb": 0.995,
    "C2Pcgb_min": 0.9,
    "C2Pcgb_max": 1.05,
    "C2PcgA": 1.0,
    "C2PcgA_min": 1.0,
    "C2PcgA_max": 1.05,
    "C2PcgD": 0.1,
    "C2PcgD_min": 0.0,
    "C2PcgD_max": 0.1,
    "audit_list": [
        "DHPgr",
        "DHPGrAvsh",
        "DHPGrAvsh.D-1",
        "DHPGrAvsh.D-2",
        "DHPGrDiF.D-1"
    ],
    "document_ref": "2 Prices 210701.odt: 2. Pr In. Con. g)"
}
#endregion

# region condition h
_2StPr_cond_h = {
    "name": "Con_h",
    "group": "Con_h",
    "description": "DHPGrAvloD > {0.9995} AND DHPGrDislD-1-< C2Pch",
    "notes": "C2Pch = 0.0000 ...0.0100",
    "C2Pch": 0.9,
    "C2Pch_min": 0.9,
    "C2Pch_max": 1.1,
    "audit_list": [
        "DHPGrAvLo",
        "DHPGrDiSl.D-1"
    ],
    "adjustors": [
        0.9995
    ],
    "document_ref": "2 Prices 210701.odt: 2. Pr In. Con. h)"
}
# endregion

#region Cond_i
_2StPr_cond_i = {
    "name": "Con_i",
    "group": "Con_i",
    "description": "DHPGrAvshoD < {1} AND DHPGrAvloD > {1} AND DMPD > DMPD-1 AND DMPD-3 > DMPD-2 AND DCPD > DOPD",
    "notes": "NO PARAMETERS",
    "audit_list": [
        "DHPGrAvsho",
        "DHPGrAvlo",
        "DMP",
        "DMP.D-1",
        "DMP.D-2",
        "DMP.D-3",
        "DCP",
        "DOP"
    ],
    "adjustors": [
        1,
        1
    ],
    "document_ref": "2 Prices 210701.odt: 2. Pr In. Con. i)"
}
#endregion

#region Cond_j
_2StPr_cond_j = {
    "name": "Con_j",
    "group": "Con_j",
    "description": "{3} * SBrD / (SBrD-2 + SBrD-3 + SBrD-4 ) OR {1.5} * (SBrD + SBrD-1) / (SBrD-3 + SBrD-4 + SBrD-5) whichever is greater than {1.3}",
    "notes": "NO PARAMETERS",
    "audit_list": [
        "SBr",
        "SBr.D-1",
        "SBr.D-2",
        "SBr.D-3",
        "SBr.D-4",
        "SBr.D-5"
    ],
    "adjustors": [
        3,
        1.5,
        1.3
    ],
    "document_ref": "2 Prices 210701.odt: 2. Pr In. Con. j)"
}
#endregion

default_2StPr_conditions = [
    _2StPr_cond_a1,
    _2StPr_cond_a2,
    _2StPr_cond_a3,

    _2StPr_cond_b1,
    _2StPr_cond_b2,
    _2StPr_cond_b3,
    _2StPr_cond_b4,
    _2StPr_cond_b5,

    _2StPr_cond_c1,
    _2StPr_cond_c2,
    _2StPr_cond_c3,
    _2StPr_cond_c4,
    _2StPr_cond_c5,

    _2StPr_cond_d1,
    _2StPr_cond_d2,
    _2StPr_cond_d3,
    _2StPr_cond_d4,
    _2StPr_cond_d5,

    _2StPr_cond_e1,
    _2StPr_cond_e2,
    _2StPr_cond_e3,
    _2StPr_cond_e4,
    _2StPr_cond_e5,

    _2StPr_cond_f,
    _2StPr_cond_g,
    _2StPr_cond_h,
    _2StPr_cond_i,
    _2StPr_cond_j,

]

def _2StPr_min_max_value_condition(cond :dict) ->list:
    ''' 
    Retrieve the min,max,current value & setting_name as a 
    list of tuples from the _2StPr_conditions. Mostly this list just contains
    one tuple ie there's only one setting, but eg see Con_g where there are more
    '''

    #giant case statement
    # if cond['name'] == 'Con_a':
    #     return [(cond['C1DHPlast3hi_min'],cond['C1DHPlast3hi_max'],cond['C1DHPlast3hi'],'C1DHPlast3hi')]
    if cond['name'] == 'Con_b1':
        return [(cond['C2Pcb_min'],cond['C2Pcb_max'],cond['C2Pcb'],'C2Pcb')]
    elif cond['name'] == 'Con_b2':
        return [(cond['C2Pcb_min'],cond['C2Pcb_max'],cond['C2Pcb'],'C2Pcb')]
    elif cond['name'] == 'Con_b3':
        return [(cond['C2Pcb_min'],cond['C2Pcb_max'],cond['C2Pcb'],'C2Pcb')]
    elif cond['name'] == 'Con_b4':
        return [(cond['C2Pcb_min'],cond['C2Pcb_max'],cond['C2Pcb'],'C2Pcb')]
    elif cond['name'] == 'Con_b5':
        return [(cond['C2Pcb_min'],cond['C2Pcb_max'],cond['C2Pcb'],'C2Pcb')]

    elif cond['name'] == 'Con_c1':
        return [(cond['C2Pcc_min'],cond['C2Pcc_max'],cond['C2Pcc'],'C2Pcc')]
    elif cond['name'] == 'Con_c2':
        return [(cond['C2Pcc_min'],cond['C2Pcc_max'],cond['C2Pcc'],'C2Pcc')]
    elif cond['name'] == 'Con_c3':
        return [(cond['C2Pcc_min'],cond['C2Pcc_max'],cond['C2Pcc'],'C2Pcc')]
    elif cond['name'] == 'Con_c4':
        return [(cond['C2Pcc_min'],cond['C2Pcc_max'],cond['C2Pcc'],'C2Pcc')]
    elif cond['name'] == 'Con_c5':
        return [(cond['C2Pcc_min'],cond['C2Pcc_max'],cond['C2Pcc'],'C2Pcc')]


    elif cond['name'] == 'Con_d1':
        return [(cond['C2Pcd_min'],cond['C2Pcd_max'],cond['C2Pcd'],'C2Pcd')]
    elif cond['name'] == 'Con_d2':
        return [(cond['C2Pcd_min'],cond['C2Pcd_max'],cond['C2Pcd'],'C2Pcd')]
    elif cond['name'] == 'Con_d3':
        return [(cond['C2Pcd_min'],cond['C2Pcd_max'],cond['C2Pcd'],'C2Pcd')]
    elif cond['name'] == 'Con_d4':
        return [(cond['C2Pcd_min'],cond['C2Pcd_max'],cond['C2Pcd'],'C2Pcd')]
    elif cond['name'] == 'Con_d5':
        return [(cond['C2Pcd_min'],cond['C2Pcd_max'],cond['C2Pcd'],'C2Pcd')]

    elif cond['name'] == 'Con_e1':
        return [(cond['C2Pce_min'],cond['C2Pce_max'],cond['C2Pce'],'C2Pce')]
    elif cond['name'] == 'Con_e2':
        return [(cond['C2Pce_min'],cond['C2Pce_max'],cond['C2Pce'],'C2Pce')]
    elif cond['name'] == 'Con_e3':
        return [(cond['C2Pce_min'],cond['C2Pce_max'],cond['C2Pce'],'C2Pce')]
    elif cond['name'] == 'Con_e4':
        return [(cond['C2Pce_min'],cond['C2Pce_max'],cond['C2Pce'],'C2Pce')]
    elif cond['name'] == 'Con_e5':
        return [(cond['C2Pce_min'],cond['C2Pce_max'],cond['C2Pce'],'C2Pce')]

    elif cond['name'] == 'Con_f':
        return [(cond['C2Pcf_min'],cond['C2Pcf_max'],cond['C2Pcf'],'C2Pcf')]

    elif cond['name'] == 'Con_g':
        return [
               (cond['C2Pcgs_min'],cond['C2Pcgs_max'],cond['C2Pcgs'],'C2Pcgs'),
               (cond['C2Pcgb_min'],cond['C2Pcgb_max'],cond['C2Pcgb'],'C2Pcgb'),
               (cond['C2PcgA_min'],cond['C2PcgA_max'],cond['C2PcgA'],'C2PcgA'),
               (cond['C2PcgD_min'],cond['C2PcgD_max'],cond['C2PcgD'],'C2PcgD'),
               ]
    elif cond['name'] == 'Con_h':
        return [(cond['C2Pch_min'],cond['C2Pch_max'],cond['C2Pch'],'C2Pch')]


    return [(0,0,0,'?')] # indicates no parameters at all

''' 
    NOTE: here we load the conditions from the _2StPr_conditions.json file, passing in the above defaults 
'''
#effectively global, a dict of dicts
# {
#  'Con_a1': {'cond['name']': 'Con_a1', 'description':  ...}, 
#   ...
#  'Con_b1': {'cond['name']': 'Con_b1', 'description': ... },
#  'Con_b2': {'cond['name']': 'Con_b2', 'description': ... },
#   ...
#  'Con_j': {'cond['name']' : 'Con_j', 'description': ...}
# }  
_2StPr_conditions = load_prepare_2StPr_conditions(g._2STPR_CONDITIONS_FQ, default_2StPr_conditions)

# force sync the associated audit_results 
sync_2StPr_audit_structure(_2StPr_conditions)

