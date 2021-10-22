''' 1 St.: Conditions to enter the 2. Stage: '''

from bsbetl import g
from bsbetl.g_helpers import load_prepare_1_conditions, sync_1_conditions_audit_structure


_1St_cond_a = {
    "name": "Con_a",
    "group": "Con_a",
    "description": "SDHPGr1.shoD > {1.005} AND ((SDT1.fD > {10000}) OR (SDT1.slD > {5000}))",
    "notes": "NO PARAMETERS",
    "audit_list": [
        "SDHPGr1sh",
        "SDT1f",
        "SDT1sl"
    ],
    "adjustors": [
        1.005,
        6000.0,
        3000.0
    ],
    "document_ref": "1 210317.odt: Pr 1. Con. a)"
}


_1St_cond_b = {
    "name": "Con_b",
    "group": "Con_b",
    "description": "SDHPGr1.mD > {1} AND ((SDT1.fD > {10000}) OR (SDT1.slD > {5000}))",
    "notes": "NO PARAMETERS",
    "audit_list": [
        "SDHPGr1m",
        "SDT1f",
        "SDT1sl"
    ],
    "adjustors": [
        1.0,
        6000.0,
        3000.0
    ],
    "document_ref": "1 210317.odt: Pr 1. Con. b)"
}

_1St_cond_c = {
    "name": "Con_c",
    "group": "Con_c",
    "description": "SDHPGr1.lo D > {1} AND ((SDT1.fD > {10000}) OR (SDT1.slD > {5000}))",
    "notes": "NO PARAMETERS",
    "audit_list": [
        "SDHPGr1lo",
        "SDT1f",
        "SDT1sl"
    ],
    "adjustors": [
        1,
        10000,
        5000
    ],
    "document_ref": "1 210317.odt: Pr 1. Con. c)"
}

_1St_cond_d = {
    "name": "Con_d",
    "group": "Con_d",
    "description": "SDHPGr1.sh D > {0.995} AND ((SDT1.fD > {10000}) OR (SDT1.slD > {5000})) AND DTF1. D > {3}",
    "notes": "NO PARAMETERS",
    "audit_list": [
        "SDHPGr1sh",
        "SDT1f",
        "SDT1sl",
        "DTF"
    ],
    "adjustors": [
        0.995,
        10000,
        5000,
        3
    ],
    "document_ref": "1 210317.odt: Pr 1. Con. d)"
}


default_1_conditions = [
    _1St_cond_a,
    _1St_cond_b,
    _1St_cond_c,
    _1St_cond_d,    
]

def _1_min_max_value_condition(cond :dict) ->list:
    ''' 
    Retrieve the min,max,current value & setting_name as a list of tuples from the _1_conditions. 
    '''

    # no parameters, so
    return [(0,0,0,'?')]


''' 
    NOTE: here we load the conditions from the _1_conditions.json file, passing in the above defaults 
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
_1St_conditions = load_prepare_1_conditions(g._1_CONDITIONS_FQ, default_1_conditions)

# force sync the associated audit_results 
sync_1_conditions_audit_structure(_1St_conditions)

