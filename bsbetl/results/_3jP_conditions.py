# region condition
from bsbetl.g_helpers import load_prepare_1_conditions
from bsbetl import g


_3jP_cond_a = {
    'name': 'Con_a',
    'group': 'Con_a',
    'description': 'Refer 3. St jP 1.: Select shares:',
    'notes': 'CjP = 1.00 ... 1.20',
    'CjP': 1.1,
    'CjP_min': 1.00,
    'CjP_max': 1.20,
    'audit_list': ['DHP','DHOCP.D-1'],   
    'adjustors': [],
    'document_ref': '3 jumped Price 210623.odt: Select shares',
}
# endregion

default_3jP_conditions = [
    _3jP_cond_a
]

def _3jP_min_max_value_condition(cond :dict) ->list:
    ''' 
    Retrieve the min,max,current value & setting_name as a 
    list of tuples from the _3jP_conditions. Mostly this list just contains
    one tuple ie there's only one setting, but eg see Con_g where there are more
    '''

    if cond['name'] == 'Con_a':
        return [(cond['CjP_min'],cond['CjP_max'],cond['CjP'],'CjP')]
    return [(0,0,0,'?')] # indicates no parameters at all

''' 
    NOTE: here we load the conditions from the _3jP_conditions.json file, passing in the above defaults 
'''
_3jP_conditions = load_prepare_1_conditions(g._3JP_CONDITIONS_FQ, default_3jP_conditions)
