import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import ALL, MATCH, Input, Output, State
from dash.exceptions import PreventUpdate

from bsbetl import app_helpers
from bsbetl.alltable_calcs import at_params
from bsbetl.app import app
from bsbetl.ov_calcs import ov_params

############################################################

layout_parms = html.Div(children=[
    html.H3(
        children=[
            html.Span('PARAMETERS', className='border-highlight')],
        className='tab-header'
    ),
    html.Div(
        id='conds-tab-summary',
        children='Adjust All-table and Overview calculation parameters here...',
        className='sw-muted-label'
    ),
    html.Div(
        children='Ready...',
        id='tabs-params-status-msg',
        className='status-msg',
    ),
    dcc.Tabs(
        id='tabs-params',
        value='tab-at',
        parent_className='custom-tabs',
        persistence=False,
        children=[
            dcc.Tab(id='t1', label='All-Table calculations Parameters',
                    value='tab-at', className='custom-tab', selected_className='custom-tab--selected'),
            dcc.Tab(id='t2', label='Overview calculations Parameters',
                    value='tab-ov', className='custom-tab', selected_className='custom-tab--selected'),
        ],
        style={'height': '36px'},
    ),
    html.Div(
        id='tabs-params-content',
        className='calc-parameters-form'
    ),
    html.Button(
        id='calc-params-save-btn',
        children='Save',
        className='link-button-refresh'
    )
])


''' callbacks for layout_parms '''


@ app.callback(
    Output('tabs-params-content', 'children'),
    Input('tabs-params', 'value')
)
def render_params_content(tab):

    #print(tab)
    if tab == 'tab-at':
        return app_helpers.params_formfields(at_params.at_calc_params, 'at')
    elif tab=='tab-ov':
        return app_helpers.params_formfields(ov_params.ov_calc_params, 'ov')


@ app.callback(
    Output('t1', 'label'),
    Input({'type': 'at', 'index': ALL}, 'value'),
    prevent_initial_call=True,
)
def at_param_change(input):
    # transfer the value(s) back into at_calc_params
    # relying on the preservation of the original insertion order
    # as per python 3.7+

    # input is a scalar (when only one parameter) or a list
    # at_params.at_calc_params is a dict
    # here is an example of one entry
    # {'atp_dummyPriceSMA_periods': {'name': 'atp_dummyPriceSMA_periods', 'calculation': 'dummyPriceSMA', 'min': 5, 'max': 400, 'setting': 200}}

    # NOTE
    # this function is the same as the one below
    # except its for the at_calcs (as opposed to the ov_calcs)
    dirty = False
    if (isinstance(input, list) and len(input) > 0):
        i = 0
        for parm in at_params.at_calc_params.keys():
            # trust the order!
            clean = at_params.at_calc_params[parm]['setting'] == input[i]
            if not clean:
                at_params.at_calc_params[parm]['setting'] = input[i]
                dirty = True
            i = i+1

    if dirty:
        return 'All-Table calculations Parameters*'
    else:
        raise PreventUpdate  # no change


@ app.callback(
    Output('t2', 'label'),
    Input({'type': 'ov', 'index': ALL}, 'value'),
    prevent_initial_call=True,
)
def ov_param_change(input):
    # transfer the value(s) back into ov_calc_params
    # relying on the preservation of the original insertion order
    # as per python 3.7+

    # NOTE
    # see notes above - this function is the same as the one above
    # except its for the ov_calcs (as opposed to the at_calcs)
    dirty = False
    if (isinstance(input, list) and len(input) > 0):
        i = 0
        for parm in ov_params.ov_calc_params.keys():
            # trust the order!
            # are we about to chnage the setting
            clean = ov_params.ov_calc_params[parm]['setting'] == input[i]
            if not clean:
                ov_params.ov_calc_params[parm]['setting'] = input[i]
                dirty = True
            i = i+1

    if dirty:
        return 'Overview calculations Parameters*'
    else:
        raise PreventUpdate  # no change





@ app.callback(
    Output('tabs-params-status-msg', 'children'),
    Input('calc-params-save-btn', 'n_clicks'),
    [
        State('t1', 'label'),
        State('t2', 'label'),
    ],
    prevent_initial_call=True
)
def save_parameters(n_clicks, at_label, ov_label):
    ''' save at_calc_params, ov_calc_params '''

    if at_label.endswith('*'):
        app_helpers.save_at_calc_params()
    if ov_label.endswith('*'):
        app_helpers.save_ov_calc_params()
    

    if not at_label.endswith('*') and not ov_label.endswith('*'):
        return ('no changes to save...')
    else:
        return 'Settings saved...'
