import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from bsbetl import app_helpers, g
from bsbetl.app import app
from bsbetl.app_helpers import init_page_size_input
from bsbetl.func_helpers import save_and_reload_page_size
from bsbetl.results._1St_conditions import _1St_conditions
from dash.dependencies import ALL, MATCH, Input, Output, State
from dash.exceptions import PreventUpdate

############################################################


layout_results_1St = html.Div(children=[
    html.H3(
        children=[
            html.Span('RESULTS-1st Stage → (To sort out shares which are long-term downwards and do not look as turning.)', className='border-highlight')],
        className='tab-header'
    ),
    html.Div(
        children=[
            html.Button(
                id='btn-pg-size-1St',
                children='set',
                className='link-button',
                title='set page size',
                style={'float': 'right'},
            ),
            dcc.Input(
                id='1St-page-size-inp',
                type='number',
                min=10,
                max=2000,
                step=1,
                value=init_page_size_input('1St_page_size'),
                placeholder='rows',
                style={'float': 'right'},
            )
        ]
    ),
    html.Div(
        children=[
            html.Button(
                id='1St-load-audit-btn',
                className='link-button-refresh',
                children="(Re)Load Audit report (for most recently run 'results-1' command)",
                title="eg After parameter change and re-run of 'results-1' command or to enable relevant ov columns to be added (on the right) for selected condition column",
                style={'margin-right': '5px'}
            ),
            html.Div(
                id='1St-recompute-msg-res',
                className='sw-muted-label',
                children='',
                style={'display':'contents'}
            ),
        ]
    ),
    html.Div(
        children=[
            html.Div(
                children=[
                    dcc.RadioItems(
                        id='all-1St-passing-chk',
                        options=[
                            {'label': f'ONLY {g.PASS} values', 'value': 'passing_only'},
                            {'label': f'ONLY {g.FAIL} values', 'value': 'failing_only'},
                            {'label': f'Reset', 'value': 'clear_filtering'},
                        ],
                        value='clear_filtering',
                        #style={'float': 'left'},
                    ),
                ],
            ),
            html.Button(
                id='load-1St-results-btn',
                className='link-button-refresh',
                children='Apply / ReLoad',
                title='load current Results tables into the frames',
                style={'margin-left': '10px'},
                disabled=False,
            ),
            html.Div(
                id='1St-status-msg-res',
                className='sw-muted-label',
                children="This page displays the results of the command 'results-1'",
                style={'clear':'both'}
            ),
        ]
    ),
    html.Div(
        id='1St-audit-view-div',
        children=[
            html.Blockquote(
                children=[
                    "Restricted AUDIT view, focussing on ONE condition only. Click '(Re)Load Audit report' for full original Results view",
                ],
                className='sw-emphasis-label'
            )
        ],
        style={'display':'none'}
    ),
    html.H5(
        children=[
            html.Span('1st Stage Results', className='border-highlight')],
        className='tab-header'
    ),
    dash_table.DataTable(
        id='1St-results-table',
        columns=app_helpers.build_1St_results_datatable_column_dicts('1St',[],''),
        #page_size=100,
        filter_action='none',  # 'native',
        filter_query='',
        sort_action='native',
        # sort_mode='multi',
        column_selectable='single',
        #fixed_columns={'headers': True, 'data': 3},
        editable=False,
        cell_selectable=True,
        #row_selectable='multi',
        # selected_rows=[],
        page_action='native',
        tooltip_duration=None,
        tooltip_delay=0,
        # style_as_list_view=True,
        style_table={'minWidth': '100%'}, #{'overflowX': 'auto'},  
        style_cell={
            # all three widths are needed
            'minWidth': '15px', #'width': '120px', 'maxWidth': '120px',
            'overflow': 'hidden',
            'textOverflow': 'ellipsis',
        },   
        style_header={
            'backgroundColor': 'white',
            'fontWeight': 'bold',
            'border': '1px solid black',
            'textDecoration': 'underline',
            'textDecorationStyle': 'dotted',
        },
        style_data_conditional=app_helpers.red_failures(['Con_a','Con_b','Con_c','Con_d']),
        virtualization=True,
    ),
    dcc.Markdown(
        id='1St-results-textarea',
        children='Results audit trail:',
        style={'width': '100%', 'height': 200},
    ),    
])




''' callbacks '''

@app.callback(
    [Output('1St-results-table','tooltip_header'),
    Output('1St-recompute-msg-res','children'),
    Output('load-1St-results-btn','disabled'),
    Output('1St-results-textarea','children'),
    Output('1St-results-table','selected_columns'),
    ],
    Input('1St-load-audit-btn','n_clicks'),
    State('1St-results-table','columns'),
    prevent_initial_call=False
)
def load_1St_results_audit_trail(n_clicks :int, columns :list):
        
    # a dict of audit lists, keyed on 'a', 'b', 'c' ... saved during command 'results-1'
    _1St_conditions_audit_dict = g.CONFIG_RUNTIME['audit_structure_1St']
    
    tips = app_helpers.build_results_datatable_col_tooltips(columns, _1St_conditions_audit_dict)

    msg = f"For an 'Audit' view of a particular condition column (showing associated Ov columns), select a condition column"

    report = app_helpers.display_results_report('_1St')
    # also deselect any currently selected columns
    return [tips, msg, False, report,[]]


@app.callback(
    [Output('1St-results-table','data'),
    Output('1St-results-table','columns'),
    Output('1St-status-msg-res','children'),
    Output('1St-audit-view-div','style'),
    Output('1St-results-table', 'page_size'),
    Output('1St-results-table','fixed_columns'),
    Output('1St-results-table','fixed_rows'),
    Output('1St-page-size-inp', 'value'),
    ],
    [Input('load-1St-results-btn','n_clicks'),
     Input('1St-results-table','selected_columns'),
    ],
    [State('1St-results-table','selected_columns'),
     State('all-1St-passing-chk','value')
    ],
    prevent_initial_call=True
)
def  load_1St_results(load_results_clicks, audit_cols,  audit_cols_state :list, passing_spec): 

    # we need to know how we got triggered - by 'load results' button 
    # or by 'back to results view' button. If the latter, we ignore and
    #  clear the selectect columns
    # see https://dash.plotly.com/advanced-callbacks

    #print(f"passing_spec={passing_spec}")

    sharelist='Default'
    fixed_columns={ 'headers': True, 'data': 2 }
    fixed_rows={'headers':True, 'data':0}

    #we get our page size not from the input field, but rather from the runtime config
    #and in fact then update the input field with this value to reflect this value
    page_size_wanted = g.CONFIG_RUNTIME['1St_page_size']
    dash_page_size = page_size_wanted

    ctx = dash.callback_context
    if not ctx.triggered:
        load_button_id = 'No clicks yet' # should nver be
    else:
        load_button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if audit_cols is not None:
        # force a re-load into Audit view
        audit_cols_state = audit_cols
        load_button_id='load-1St-results-btn'

    # grab the extra ov columns for reference audit purposes from the tooltip_header
    # only one such column ought to be selected
    audit_view_style={'display' : 'none'}
    _1St_ov_audit_cols=[]
    col_under_audit = ''

    if load_button_id=='load-1St-results-btn' and isinstance(audit_cols_state,list) and len(audit_cols_state) > 0:
        col_under_audit = audit_cols_state[0]
        _1St_ov_audit_cols=_1St_conditions[col_under_audit]['audit_list']


    col_specs=app_helpers.build_1St_results_datatable_column_dicts('1St', _1St_ov_audit_cols, col_under_audit)
    _1St_data = app_helpers.get_res_dataframe_as_dict('1St', sharelist, _1St_ov_audit_cols, passing_spec)    
    #print(f"_1St_data = {_1St_data}")

    if col_under_audit != '':
        status_msg = f'In audit view, relevant columns are shown for the condition under focus'
        audit_view_style={'display':'contents'}
    else:
        if _1St_data is None or  len(_1St_data) == 0:
            if _1St_data is None:
                shim="Results could not be not found."
                status_msg = f"{shim}. Have you run the command 'results-1' since you ran 'process-3'. Was there perhaps an error? Try restarting the web server."
            elif len(_1St_data)==0:
                shim = f"ZERO shares in Results"
                status_msg=f"{shim}. Conditions may be too strict. Conditions may be adjusted on the Conditions tab, then re-run 'results-1' command. You may have to restart the web server if expected changes are not seen."  
        else:
            status_msg = f"{len(_1St_data)} rows. Conditions may be adjusted on the Conditions tab, then re-run 'results-1' command. You may have to restart the web server if expected changes are not seen."

    return [_1St_data, col_specs, status_msg, audit_view_style,
            dash_page_size, fixed_columns, fixed_rows, page_size_wanted]

@app.callback(
    Output('load-1St-results-btn','n_clicks'),
    Input('btn-pg-size-1St','n_clicks'),
    State('1St-page-size-inp','value'),
    prevent_initial_call=True
)
def set_1st_pg_size(n_clicks,page_size):
    ''' respond to set page size btn link '''

    save_and_reload_page_size('1St_page_size', page_size)
    # this should cause a refresh
    return 0


# @app.callback(
#     Output('1St-results-table','filter_query'),
#     Output('1St-results-table','filter_action'),
#     Input('all-1St-passing-chk','value'),
#     prevent_initial_call=True
# )
# def filter_all_1St_passing(value):

#     filter_action='native'
#     if value=='passing_only':
#         filter_query='{Con_a} contains ✓ OR {Con_b} contains ✓ OR {Con_c} contains ✓ OR {Con_d} contains ✓'
#     elif value=='failing_only':
#         filter_query='{Con_a} contains 🗙 OR {Con_b} contains 🗙 OR {Con_c} contains 🗙 OR {Con_d} contains 🗙'
#     else: 
#         filter_query=''
#         filter_action='none'

#     #print(f'value={value}, filter_query={filter_query}')
#     return [filter_query,filter_action]

