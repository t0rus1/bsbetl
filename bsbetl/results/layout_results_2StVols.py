import dash
import dash_table
from bsbetl import app_helpers, g
from bsbetl.app import app
from bsbetl.app_helpers import init_page_size_input
from bsbetl.func_helpers import save_and_reload_page_size
from bsbetl.results._2StVols_conditions import _2StVols_conditions
from dash import dcc, html
from dash.dependencies import ALL, MATCH, Input, Output, State
from dash.exceptions import PreventUpdate

############################################################
_2StVols_red_columns = ['Con_a1','Con_a2','Con_b','Con_c','Con_d','Con_e','Con_f']

layout_results_2StVols = html.Div(children=[
    html.H3(
        children=[
            html.Span('RESULTS-2St Vols Stage → (Conditions to meet to enter the 3. Stage )', className='border-highlight')],
        className='tab-header'
    ),
    html.Div(
        children=[
            html.Button(
                id='btn-pagesize-2StVols',
                children='set',
                className='link-button',
                title='set page size',
                style={'float': 'right'},
            ),
            dcc.Input(
                id='2StVols-page-size-inp',
                type='number',
                min=10,
                max=2000,
                step=1,
                value=init_page_size_input('2StVols_page_size'),
                placeholder='rows',
                style={'float': 'right'},
            )
        ]
    ),
    html.Div(
        children=[
            html.Button(
                id='2StVols-load-audit-btn',
                className='link-button-refresh',
                children="(Re)Load Audit report (for most recently run 'results-2st-vols' command)",
                title="eg After parameter change and re-run of 'results-2st-vols' command or to enable relevant ov columns to be added (on the right) for selected condition column",
                style={'margin-right': '5px'}
            ),
        ]
    ),
    html.Div(
        children=[
            dcc.RadioItems(
                id='all-2StVols-passing-chk',
                options=[
                    {'label': f'ONLY {g.PASS} values', 'value': 'passing_only'},
                    {'label': f'ONLY {g.FAIL} values', 'value': 'failing_only'},
                    {'label': f'Reset', 'value': 'clear_filtering'},
                ],
                value='clear_filtering'
            ),
            html.Button(
                id='load-2StVols-results-btn',
                className='link-button-refresh',
                children='Apply / ReLoad',
                title='load current Results tables into the frames',
                style={'margin-right': '5px', 'display': 'block'},
                disabled=False,
            ),
            html.Div(
                id='2StVols-recompute-msg-res',
                className='sw-muted-label',
                children="This page displays the results of the command 'results-2st-vols'",
                style={'display':'contents'}
            ),
            html.Div(
                id='2StVols-status-msg-res',
                className='sw-muted-label',
                children='',
                style={'display':'contents'}
            ),
        ]
    ),
    html.Div(
        id='2StVols-audit-view-div',
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
            html.Span('2StVols Stage Results', className='border-highlight')],
        className='tab-header'
    ),
    dash_table.DataTable(
        id='2StVols-results-table',
        columns=app_helpers.build_2StVols_results_datatable_column_dicts('2StVols',[],''),
        #page_size=100,
        filter_action='none',  # 'native',
        filter_query='',
        sort_action='native',
        # sort_mode='multi',
        column_selectable='single',
        fixed_columns={'headers': True, 'data': 3},
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
            'minWidth': '15px', #'width': '100px', 'maxWidth': '100px',
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
        style_data_conditional=app_helpers.red_failures(_2StVols_red_columns),
        virtualization=True,
    ),
    dcc.Markdown(
        id='2StVol-results-textarea',
        children='Results audit trail',
        style={'width': '100%', 'height': 400},
    ),    

])

''' callbacks '''

@app.callback(
    [Output('2StVols-results-table','tooltip_header'),
    Output('2StVols-recompute-msg-res','children'),
    Output('load-2StVols-results-btn','disabled'),
    Output('2StVol-results-textarea','children'),
    Output('2StVols-results-table','selected_columns'),
    ],
    Input('2StVols-load-audit-btn','n_clicks'),
    State('2StVols-results-table','columns'),
    prevent_initial_call=False
)
def load_2StVols_audit_results(n_clicks :int, columns :list):
        
    # returns a dict of audit lists, keyed on 'a1','a2', ...  'b', 'c' ...
    # get audit results of last 'results-2st-vols' command
    _2StVols_conditions_audit_dict = g.CONFIG_RUNTIME['audit_structure_2StVols']
    
    tips = app_helpers.build_results_datatable_col_tooltips(columns, _2StVols_conditions_audit_dict)

    msg = f"For an 'Audit' view of a particular condition column (showing associated Ov columns), select a condition column"

    report = app_helpers.display_results_report('_2StVols')
    # also deselect any currently selected columns
    return [tips, msg, False, report,[]]

@app.callback(
    [Output('2StVols-results-table','data'),
    Output('2StVols-results-table','columns'),
    Output('2StVols-status-msg-res','children'),
    Output('2StVols-audit-view-div','style'),
    Output('2StVols-results-table', 'page_size'),
    Output('2StVols-results-table','fixed_columns'),
    Output('2StVols-results-table','fixed_rows'),
    Output('2StVols-page-size-inp', 'value'),
    ],
    [Input('load-2StVols-results-btn','n_clicks'),
     Input('2StVols-results-table', 'selected_columns'),
    ],
    [State('2StVols-results-table','selected_columns'),
     State('all-2StVols-passing-chk','value')
     ],
    prevent_initial_call=True
)
def  load_2StVols_results(load_results_clicks, audit_cols, audit_cols_state :list, passing_spec): 

    # we need to know how we got triggered - by 'load results' button 
    # or by 'back to results view' button. If the latter, we ignore and
    #  clear the selectect columns
    # see https://dash.plotly.com/advanced-callbacks

    sharelist='Default'
    fixed_columns={ 'headers': True, 'data': 2 }
    fixed_rows={'headers':True, 'data':0}

    #we get our page size not from the input field, but rather from the runtime config
    #and in fact then update the input field with this value to reflect this value
    page_size_wanted = g.CONFIG_RUNTIME['2StVols_page_size']
    dash_page_size = page_size_wanted


    ctx = dash.callback_context
    if not ctx.triggered:
        load_button_id = 'No clicks yet' # should nver be
    else:
        load_button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if audit_cols is not None:
        # force a re-load into Audit view
        audit_cols_state = audit_cols
        load_button_id='load-2StVols-results-btn'

    # grab the extra ov columns for reference audit purposes from the tooltip_header
    # only one such column ought to be selected
    audit_view_style={'display' : 'none'}
    _2StVols_ov_audit_cols=[]
    col_under_audit = ''

    if load_button_id=='load-2StVols-results-btn' and isinstance(audit_cols,list) and len(audit_cols) > 0:
        col_under_audit = audit_cols[0]
        _2StVols_ov_audit_cols=_2StVols_conditions[col_under_audit]['audit_list']

    col_specs=app_helpers.build_2StVols_results_datatable_column_dicts('2StVols', _2StVols_ov_audit_cols, col_under_audit)
    _2StVols_data = app_helpers.get_res_dataframe_as_dict('2StVols', sharelist, _2StVols_ov_audit_cols, passing_spec)    

    if col_under_audit != '':
        status_msg = f'In audit view, relevant columns are shown for the condition under focus'
        audit_view_style={'display':'contents'}
    else:
        if _2StVols_data is None or len(_2StVols_data) == 0:
            if _2StVols_data is None:
                shim="Results could not be not found."
                status_msg = f"{shim}. Have you run the command 'results-2st-vols' since you ran 'process-3'. Was there perhaps an error? Try restarting the web server."
            elif len(_2StVols_data)==0:
                shim = f"{len(_2StVols_data)} shares qualify"
                status_msg=f"{shim}. Conditions may be too strict. Conditions may be adjusted on the Conditions tab, then re-run 'results-1' command. You may have to restart the web server if expected changes are not seen."  
        else:
            status_msg = f"{len(_2StVols_data)} rows. Conditions may be adjusted on the Conditions tab, then re-run 'results-1' command. You may have to restart the web server if expected changes are not seen."

    return [_2StVols_data, col_specs, status_msg, audit_view_style,
            dash_page_size,fixed_columns,fixed_rows, page_size_wanted]

@app.callback(
    Output('load-2StVols-results-btn','n_clicks'),
    Input('btn-pagesize-2StVols','n_clicks'),
    State('2StVols-page-size-inp','value'),
    prevent_initial_call=True
)
def set_2StVols_pg_size(n_clicks,page_size):
    ''' respond to set page size btn link '''

    save_and_reload_page_size('2StVols_page_size', page_size)
    # this should cause a refresh
    return 0

# @app.callback(
#     Output('2StVols-results-table','filter_query'),
#     Input('all-2StVols-passing-chk','value')
# )
# def filter_all_2StPr_passing(value):

#     if isinstance(value,list) and len(value) > 0 and value[0]=='all_passing':
#         qry=[]
#         qry.append("{Con_a1} eq ✓ and {Con_a2} ne 🗙")
#         qry.append("and {Con_b} ne 🗙")
#         qry.append("and {Con_c} ne 🗙")
#         qry.append("and {Con_d} ne 🗙")
#         qry.append("and {Con_e} eq ✓")
#         qry.append("and {Con_f} ne 🗙")
#         filter_query=' '.join(qry)
#     else: 
#         filter_query=""

#     return filter_query

# @app.callback(
#     Output('2StVols-results-table','filter_query'),
#     Output('2StVols-results-table','filter_action'),
#     Input('all-2StVols-passing-chk','value'),
#     prevent_initial_call=True
# )
# def filter_all_2StVols_passing(value):

#     filter_action='native'
#     if value=='all_passing':
#         filter_query='{Con_a1} contains ✓ AND {Con_a2} contains ✓ AND {Con_b} contains ✓ AND {Con_c} contains ✓ AND {Con_d} contains ✓ AND {Con_e} contains ✓ AND {Con_f} contains ✓'
#     elif value=='any_passing':
#         filter_query='{Con_a1} contains ✓ OR {Con_a2} contains ✓ OR {Con_b} contains ✓ OR {Con_c} contains ✓ OR {Con_d} contains ✓ OR {Con_e} contains ✓ OR {Con_f} contains ✓'
#     else: 
#         filter_query=''
#         filter_action='none'

#     print(f'value={value}, filter_query={filter_query}')
#     return [filter_query,filter_action]
