import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import ALL, MATCH, Input, Output, State
from dash.exceptions import PreventUpdate

from bsbetl import app_helpers
#from bsbetl.app_helpers import dp_stage2_conditions_formfields
from bsbetl.app import app
from bsbetl.ov_calcs import ov_params
#from bsbetl.results_initial.dp_conditions import dp_init_conditions, dp_init_min_max_value_condition
#from bsbetl.results_initial.dv_conditions import dv_init_conditions, dv_init_min_max_value_condition
#from bsbetl.results_stage2.dp_stage2_conditions import dp_stage2_conditions, dp_stage2_min_max_value_condition
from bsbetl.results._1St_conditions import _1St_conditions,_1_min_max_value_condition
from bsbetl.results._2StPr_conditions import _2StPr_conditions,_2StPr_min_max_value_condition
from bsbetl.results._2StVols_conditions import _2StVols_conditions,_2StVols_min_max_value_condition
from bsbetl.results._3jP_conditions import _3jP_conditions ,_3jP_min_max_value_condition

############################################################

layout_conds = html.Div(children=[
    html.H3(
        children=[
            html.Span('CONDITIONS', className='border-highlight')],
        className='tab-header'
    ),
    html.Div(
        id='conds-tab-summary',
        children='Adjust Ov filter conditions here. See Results- tabs for Results...',
        className='sw-muted-label'
    ),
    html.Div(
        children='Ready...',
        id='tabs-conds-status-msg',
        className='status-msg',
    ),
    dcc.Tabs(
        id='tabs-conds',
        value='tab-1St',
        parent_className='custom-tabs',
        persistence=False,
        children=[
            dcc.Tab(id='t1St', label='1St. Conditions',
                    value='tab-1St', className='custom-tab', selected_className='custom-tab--selected'),
            dcc.Tab(id='t2St', label='2St. Price Conditions',
                    value='tab-2StPr', className='custom-tab', selected_className='custom-tab--selected'),
            dcc.Tab(id='t2StVols', label='2St. Volumes Conditions',
                    value='tab-2StVols', className='custom-tab', selected_className='custom-tab--selected'),
            dcc.Tab(id='t3jP', label='3jP Conditions',
                    value='tab-3jP', className='custom-tab', selected_className='custom-tab--selected'),
            # dcc.Tab(id='t3', label='Initial Conditions (Daily Prices)',
            #         value='tab-dp', className='custom-tab', selected_className='custom-tab--selected'),
            # dcc.Tab(id='t4', label='Initial Conditions (Vols)',
            #         value='tab-vols', className='custom-tab', selected_className='custom-tab--selected'),
            # dcc.Tab(id='t5', label='Stage_2 Conditions (Daily Prices)',
            #         value='tab-dp2', className='custom-tab', selected_className='custom-tab--selected'),
        ],
        style={'height': '36px'},
    ),
    html.Div(
        id='tabs-conds-content',
        className='calc-parameters-form'
    ),
    html.Button(
        id='calc-conds-save-btn',
        children='Save',
        className='link-button-refresh'
    )
])


''' callbacks for layout '''


@ app.callback(
    Output('tabs-conds-content', 'children'),
    Input('tabs-conds', 'value')
)
def render_params_content(tab):

    if tab=='tab-1St':
        tab_content = app_helpers._1_conditions_formfields('1St')
        return tab_content
    if tab=='tab-2StPr':
        tab_content = app_helpers._2StPr_conditions_formfields('2StPr')
        return tab_content
    if tab=='tab-2StVols':
        tab_content = app_helpers._2StVols_conditions_formfields('2StVols')
        return tab_content
    if tab=='tab-3jP':
        tab_content = app_helpers._3jP_conditions_formfields('3jP')
        return tab_content


@ app.callback(
    Output('t1St', 'label'),
    Input({'type': '1St', 'index': ALL}, 'value'),
    prevent_initial_call=True,
)
def param_1St_change(input):
    # transfer the value(s) back into at_calc_params
    # relying on the preservation of the original insertion order
    # as per python 3.7+

    # input is a scalar (when only one parameter) or a list
    # at_params.at_calc_params is a dict
    # here is an example of one entry
    # {'atp_dummyPriceSMA_periods': {'name': 'atp_dummyPriceSMA_periods', 'calculation': 'dummyPriceSMA', 'min': 5, 'max': 400, 'setting': 200}}

    # NOTE
    # this function is the same as the ones above
    # except its for the dp_init_conditions (as opposed to the at_calcs or ov_calcs)
    # dp_init_conditions is a dict of dicts (see dp_conditions.py)
    # {
    #  'Con_a': {'cond['name']': 'Con_a', 'description':  ...}, 
    #  'Con_b1': {'cond['name']': 'Con_b1', 'description': ... },
    #  'Con_b2': {'cond['name']': 'Con_b2', 'description': ... },
    #   ...
    #  'Con_j': {'cond['name']' : 'Con_j', 'description': ...}
    # }  

    #print(input)

    dirty = False
    adj_index=0
    if (isinstance(input, list) and len(input) > 0):
        i = 0
        for cond in _1St_conditions.keys():
            #print(cond)
            immvc = _1_min_max_value_condition(_1St_conditions[cond]) #-> list of tuple [(min,max,value,setting_name),..]
            # trust the order!
            #print(immvc)
            for setting_tuple in immvc:
                if setting_tuple[3] == '?': 
                    continue
                try:
                    clean = setting_tuple[2] == input[i]
                    if not clean:
                        _1St_conditions[cond][setting_tuple[3]] = input[i]
                        dirty = True
                        break # one such occurence is enough
                    i = i+1
                except IndexError as ie:
                    pass # Con_j has no input thus it causes this exception            
            if dirty:
                break  # one such occurence is enough

            # assess also the adjustors
            #compare input to current adjustors _1St_conditions[cond]['adjustors']
            cur_adj_strings = [str(i) for i in _1St_conditions[cond]['adjustors']]
            ref_adj_values = ';'.join(cur_adj_strings)
            if input[adj_index] != ref_adj_values:
                #print(f'dirty! {input[adj_index]}  vs {ref_adj_values}')
                _1St_conditions[cond]['adjustors'] = [float(i) for i in input[adj_index].split(';')]
                #print(f"new adjustors: {_1St_conditions[cond]['adjustors']}")
                dirty=True
                break

            adj_index = adj_index + 1

    if dirty:
        return '1St Conditions*'
    else:
        raise PreventUpdate  # no change


@ app.callback(
    Output('t2St', 'label'),
    Input({'type': '2StPr', 'index': ALL}, 'value'),
    prevent_initial_call=True,
)
def param_2StPr_change(input):
    # transfer the value(s) back into dv_init_conditions
    # relying on the preservation of the original insertion order
    # as per python 3.7+

    # input is a scalar (when only one parameter) or a list
    # at_params.at_calc_params is a dict
    # here is an example of one entry
    # {'atp_dummyPriceSMA_periods': {'name': 'atp_dummyPriceSMA_periods', 'calculation': 'dummyPriceSMA', 'min': 5, 'max': 400, 'setting': 200}}

    # NOTE
    # this function is the same as the ones above
    # except its for the dv_init_conditions (as opposed to the at_calcs or ov_calcs)
    # dv_init_conditions is a dict of dicts (see dv_conditions.py)
    # {
    #  'Con_a': {'cond['name']': 'Con_a', 'description':  ...}, 
    #  'Con_b1': {'cond['name']': 'Con_b1', 'description': ... },
    #   ...
    # }  

    # print(input)
    # print(len(input))

    dirty = False
    if (isinstance(input, list) and len(input) > 0):
        input_index=0
        for cond in _2StPr_conditions.keys():            
            #print(f'cond={cond}') #, adj_index={adj_index}')
            immvcs = _2StPr_min_max_value_condition(_2StPr_conditions[cond]) #-> list of tuples [(min,max,value,setting_name)...]
            input_offset=0
            for setting_tuple in immvcs:
                try:
                    clean = setting_tuple[3]=='?' or setting_tuple[2] == input[input_index+input_offset]
                    if not clean:
                        #print(f'input_index={input_index}, input_offset={input_offset}')
                        #print(f'cond={cond}, setting_tuple={setting_tuple}, input_index={input_index}, input_offset={input_offset}, corresp input = {input[input_index+input_offset]}')
                        _2StPr_conditions[cond][setting_tuple[3]] = input[input_index+input_offset]
                        dirty = True
                        #print(f'dirty, setting_tuple[2]: {setting_tuple[2]} vs (effective_input_idx={input_index+input_offset}) {input[input_index+input_offset]}')
                        #print(_2StPr_conditions)
                        break # one such occurence is enough
                    if setting_tuple[3] != '?':
                        input_offset = input_offset+1
                except IndexError as ie:
                    pass # Con_j has no input thus it causes this exception
            if dirty:
                break # one such occurence is enough

            # assess also the adjustors
            if 'adjustors' in _2StPr_conditions[cond]:
                #adjust input index reference to be pointing to comparable slot
                #ie move to 'next' condition start slot, then back off by number of adjustor values
                synced_adj_index = input_index + app_helpers.num_inputs_for_condition(_2StPr_conditions[cond]) - 1 #len(_2StPr_conditions[cond]['adjustors'])
                existing_adjustments_ary = [str(i) for i in _2StPr_conditions[cond]['adjustors']]
                #print(f"input_index={input_index}, synced_adj_index={synced_adj_index}, existing_adjustments_ary={existing_adjustments_ary}")
                if len(existing_adjustments_ary) > 0:
                    existing_adjustments_semis_ary = ';'.join(existing_adjustments_ary)
                    if len(input[synced_adj_index]) > 0 and (input[synced_adj_index] != existing_adjustments_semis_ary):
                        #print(f'change from {existing_adjustments_semis_ary} wanted')
                        _2StPr_conditions[cond]['adjustors'] = [float(i) for i in input[synced_adj_index].split(';') if i != '']
                        #print(f"to new adjustors: {_2StPr_conditions[cond]['adjustors']}")
                        dirty=True
                        break

            #move input index to next condition
            input_index = input_index + app_helpers.num_inputs_for_condition(_2StPr_conditions[cond])


    if dirty:
        #print('DIRTY')
        return '2St. Price Conditions*'
    else:
        raise PreventUpdate  # no change

@ app.callback(
    Output('t2StVols', 'label'),
    Input({'type': '2StVols', 'index': ALL}, 'value'),
    prevent_initial_call=True,
)
def param_2StVols_change(input):
    # transfer the value(s) back into dv_init_conditions
    # relying on the preservation of the original insertion order
    # as per python 3.7+

    # input is a scalar (when only one parameter) or a list
    # at_params.at_calc_params is a dict
    # here is an example of one entry
    # {'atp_dummyPriceSMA_periods': {'name': 'atp_dummyPriceSMA_periods', 'calculation': 'dummyPriceSMA', 'min': 5, 'max': 400, 'setting': 200}}

    # NOTE
    # this function is the same as the ones above
    # except its for the dv_init_conditions (as opposed to the at_calcs or ov_calcs)
    # dv_init_conditions is a dict of dicts (see dv_conditions.py)
    # {
    #  'Con_a': {'cond['name']': 'Con_a', 'description':  ...}, 
    #  'Con_b1': {'cond['name']': 'Con_b1', 'description': ... },
    #   ...
    # }  

    #print(input)

    dirty = False
    if (isinstance(input, list) and len(input) > 0):
        input_index=0
        for cond in _2StVols_conditions.keys():            
            #print(f'cond={cond}') #, adj_index={adj_index}')
            immvcs = _2StVols_min_max_value_condition(_2StVols_conditions[cond]) #-> list of tuples [(min,max,value,setting_name)...]
            input_offset=0
            for setting_tuple in immvcs:
                try:
                    clean = setting_tuple[3]=='?' or setting_tuple[2] == input[input_index+input_offset]
                    if not clean:
                        #print(f'input_index={input_index}, input_offset={input_offset}')
                        #print(f'cond={cond}, setting_tuple={setting_tuple}, input_index={input_index}, input_offset={input_offset}, corresp input = {input[input_index+input_offset]}')
                        _2StVols_conditions[cond][setting_tuple[3]] = input[input_index+input_offset]
                        dirty = True
                        #print(f'dirty, setting_tuple[2]: {setting_tuple[2]} vs (effective_input_idx={input_index+input_offset}) {input[input_index+input_offset]}')
                        #print(_2StVols_conditions)
                        break # one such occurence is enough
                    if setting_tuple[3] != '?':
                        input_offset = input_offset+1
                except IndexError as ie:
                    pass # Con_j has no input thus it causes this exception
            if dirty:
                break # one such occurence is enough

            # assess also the adjustors
            if 'adjustors' in _2StVols_conditions[cond]:
                #adjust input index reference to be pointing to comparable slot
                #ie move to 'next' condition start slot, then back off by number of adjustor values
                synced_adj_index = input_index + app_helpers.num_inputs_for_condition(_2StVols_conditions[cond]) - 1 
                existing_adjustments_ary = [str(i) for i in _2StVols_conditions[cond]['adjustors']]
                #print(f"input_index={input_index}, synced_adj_index={synced_adj_index}, existing_adjustments_ary={existing_adjustments_ary}")
                if len(existing_adjustments_ary) > 0:
                    existing_adjustments_semis_ary = ';'.join(existing_adjustments_ary)
                    if len(input[synced_adj_index]) > 0 and (input[synced_adj_index] != existing_adjustments_semis_ary):
                        #print(f'change from {existing_adjustments_semis_ary} wanted')
                        _2StVols_conditions[cond]['adjustors'] = [float(i) for i in input[synced_adj_index].split(';') if i!='']
                        #print(f"to new adjustors: {_2StVols_conditions[cond]['adjustors']}")
                        dirty=True
                        break

            #move input index to next condition
            input_index = input_index + app_helpers.num_inputs_for_condition(_2StVols_conditions[cond])


    if dirty:
        #print('DIRTY')
        return '2St. Volumes Conditions*'
    else:
        raise PreventUpdate  # no change


@ app.callback(
    Output('t3jP', 'label'),
    Input({'type': '3jP', 'index': ALL}, 'value'),
    prevent_initial_call=True,
)
def param_3jP_change(input):
    # transfer the value(s) back into dv_init_conditions
    # relying on the preservation of the original insertion order
    # as per python 3.7+

    # input is a scalar (when only one parameter) or a list
    # at_params.at_calc_params is a dict
    # here is an example of one entry
    # {'atp_dummyPriceSMA_periods': {'name': 'atp_dummyPriceSMA_periods', 'calculation': 'dummyPriceSMA', 'min': 5, 'max': 400, 'setting': 200}}

    # NOTE
    # this function is the same as the ones above
    # except its for the dv_init_conditions (as opposed to the at_calcs or ov_calcs)
    # dv_init_conditions is a dict of dicts (see dv_conditions.py)
    # {
    #  'Con_a': {'cond['name']': 'Con_a', 'description':  ...}, 
    #  'Con_b1': {'cond['name']': 'Con_b1', 'description': ... },
    #   ...
    # }  

    #print(input)

    dirty = False
    if (isinstance(input, list) and len(input) > 0):
        input_index=0
        for cond in _3jP_conditions.keys():            
            #print(f'cond={cond}') #, adj_index={adj_index}')
            immvcs = _3jP_min_max_value_condition(_3jP_conditions[cond]) #-> list of tuples [(min,max,value,setting_name)...]
            input_offset=0
            for setting_tuple in immvcs:
                try:
                    clean = setting_tuple[3]=='?' or setting_tuple[2] == input[input_index+input_offset]
                    if not clean:
                        #print(f'input_index={input_index}, input_offset={input_offset}')
                        #print(f'cond={cond}, setting_tuple={setting_tuple}, input_index={input_index}, input_offset={input_offset}, corresp input = {input[input_index+input_offset]}')
                        _3jP_conditions[cond][setting_tuple[3]] = input[input_index+input_offset]
                        dirty = True
                        #print(f'dirty, setting_tuple[2]: {setting_tuple[2]} vs (effective_input_idx={input_index+input_offset}) {input[input_index+input_offset]}')
                        #print(_2StVols_conditions)
                        break # one such occurence is enough
                    if setting_tuple[3] != '?':
                        input_offset = input_offset+1
                except IndexError as ie:
                    pass # Con_j has no input thus it causes this exception
            if dirty:
                break # one such occurence is enough

            # assess also the adjustors
            if 'adjustors' in _3jP_conditions[cond]:
                #adjust input index reference to be pointing to comparable slot
                #ie move to 'next' condition start slot, then back off by number of adjustor values
                synced_adj_index = input_index + app_helpers.num_inputs_for_condition(_3jP_conditions[cond]) - 1 
                existing_adjustments_ary = [str(i) for i in _3jP_conditions[cond]['adjustors']]
                #print(f"input_index={input_index}, synced_adj_index={synced_adj_index}, existing_adjustments_ary={existing_adjustments_ary}")
                if len(existing_adjustments_ary) > 0:
                    existing_adjustments_semis_ary = ';'.join(existing_adjustments_ary)
                    if len(input[synced_adj_index]) > 0 and (input[synced_adj_index] != existing_adjustments_semis_ary):
                        #print(f'change from {existing_adjustments_semis_ary} wanted')
                        _3jP_conditions[cond]['adjustors'] = [float(i) for i in input[synced_adj_index].split(';') if i!='']
                        #print(f"to new adjustors: {_3jP_conditions[cond]['adjustors']}")
                        dirty=True
                        break

            #move input index to next condition
            input_index = input_index + app_helpers.num_inputs_for_condition(_3jP_conditions[cond])


    if dirty:
        #print('DIRTY')
        return '3jP Conditions*'
    else:
        raise PreventUpdate  # no change

@ app.callback(
    Output('tabs-conds-status-msg', 'children'),
    [Input('calc-conds-save-btn', 'n_clicks'),   
     State('t1St', 'label'),
     State('t2St', 'label'),
     State('t2StVols', 'label'),
     State('t3jP', 'label'),
    ],
    prevent_initial_call=True
)
def save_parameters(n_clicks, t1_label, t2_label, t3_label, t4_label):
    ''' save '''


    if t1_label.endswith('*'):
        app_helpers.save_1St_conditions()
    if t2_label.endswith('*'):
        app_helpers.save_2StPr_conditions()
    if t3_label.endswith('*'):
        app_helpers.save_2StVols_conditions()
    if t4_label.endswith('*'):
        app_helpers.save_3jP_conditions()

    if not t1_label.endswith('*') and not t2_label.endswith('*') and not t3_label.endswith('*') and not t4_label.endswith('*'):
        return ('no changes to save...')
    else:
        return 'Settings saved...'
