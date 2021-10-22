import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from bsbetl import app_helpers, g
from bsbetl.app import app
from bsbetl.app_helpers import init_page_size_input, red_failures
from bsbetl.func_helpers import save_and_reload_page_size
from bsbetl.results._2StPr_conditions import _2StPr_conditions
from dash.dependencies import ALL, MATCH, Input, Output, State
from dash.exceptions import PreventUpdate

############################################################
_2StPr_red_columns = [  'Con_b1','Con_b2','Con_b3','Con_b4','Con_b5',
                        'Con_c1','Con_c2','Con_c3','Con_c4','Con_c5',
                        'Con_d1','Con_d2','Con_d3','Con_d4','Con_d5',
                        'Con_e1','Con_e2','Con_e3','Con_e4','Con_e5',
                        'Con_f','Con_g','Con_h','Con_i','Con_j'
                    ]

tweaked_widths = [
        {'if': {'column_id': 'id'}, 'width': '10px'},
        {'if': {'column_id': 'Con_a1'}, 'width': '180px'},
        {'if': {'column_id': 'Con_a2'}, 'width': '180px'},
        {'if': {'column_id': 'Con_a3'}, 'width': '180px'},

        {'if': {'column_id': 'Con_b1'}, 'width': '200px'},
        {'if': {'column_id': 'Con_b2'}, 'width': '200px'},
        {'if': {'column_id': 'Con_b3'}, 'width': '200px'},
        {'if': {'column_id': 'Con_b4'}, 'width': '200px'},
        {'if': {'column_id': 'Con_b5'}, 'width': '200px'},

        {'if': {'column_id': 'Con_c1'}, 'width': '200px'},
        {'if': {'column_id': 'Con_c2'}, 'width': '200px'},
        {'if': {'column_id': 'Con_c3'}, 'width': '200px'},
        {'if': {'column_id': 'Con_c4'}, 'width': '200px'},
        {'if': {'column_id': 'Con_c5'}, 'width': '200px'},

        {'if': {'column_id': 'Con_d1'}, 'width': '200px'},
        {'if': {'column_id': 'Con_d2'}, 'width': '200px'},
        {'if': {'column_id': 'Con_d3'}, 'width': '200px'},
        {'if': {'column_id': 'Con_d4'}, 'width': '200px'},
        {'if': {'column_id': 'Con_d5'}, 'width': '200px'},

        {'if': {'column_id': 'Con_e1'}, 'width': '200px'},
        {'if': {'column_id': 'Con_e2'}, 'width': '200px'},
        {'if': {'column_id': 'Con_e3'}, 'width': '200px'},
        {'if': {'column_id': 'Con_e4'}, 'width': '200px'},
        {'if': {'column_id': 'Con_e5'}, 'width': '200px'},
    ]

layout_results_2StPr = html.Div(children=[
    html.H3(
        children=[
            html.Span('RESULTS-2StPr Stage → (To detect shares by suspicious price behaviour)', className='border-highlight')],
        className='tab-header'
    ),
    html.Div(
        children=[
            html.Button(
                id='btn-pagesize-2stPr',
                children='set',
                className='link-button',
                title='set page size',
                style={'float': 'right'},
            ),
            dcc.Input(
                id='2StPr-page-size-inp',
                type='number',
                min=10,
                max=2000,
                step=1,
                value=init_page_size_input('2StPr_page_size'),
                placeholder='rows',
                style={'float': 'right'},
            )
        ]
    ),
    html.Div(
        children=[
            html.Button(
                id='2StPr-load-audit-btn',
                className='link-button-refresh',
                children="(Re)Load Audit report (for most recently run 'results-2st-pr' command)",
                title="eg After parameter change and re-run of 'results-2st-pr' command or to enable relevant ov columns to be added (on the right) for selected condition column",
                style={'margin-right': '5px'}
            ),
            html.Div(
                id='2StPr-recompute-msg-res',
                className='sw-muted-label',
                children='',
                style={'display':'contents'}
            ),
        ]
    ),
    html.Div(
        children=[
            dcc.RadioItems(
                id='all-2StPr-passing-chk',
                options=[
                    {'label': f'ONLY {g.PASS} values', 'value': 'passing_only'},
                    {'label': f'ONLY {g.FAIL} values', 'value': 'failing_only'},
                    {'label': f'Reset', 'value': 'clear_filtering'},
                ],
                value='clear_filtering',
                #style={'float': 'left'},
            ),
            html.Button(
                id='load-2StPr-results-btn',
                className='link-button-refresh',
                children='Apply / ReLoad',
                title='load 2StPr Results into the grid',
                style={'margin-left': '10px'},
                disabled=False,
            ),
            html.Div(
                id='2StPr-status-msg-res',
                className='sw-muted-label',
                children="This page displays the results of the command 'results-2st-pr'",
                style={'clear':'both'}
            ),
        ]
    ),
    html.Div(
        id='2StPr-audit-view-div',
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
            html.Span('2StPr Stage Results', className='border-highlight')],
        className='tab-header'
    ),
    dash_table.DataTable(
        id='2StPr-results-table',
        columns=app_helpers.build_2StPr_results_datatable_column_dicts('2StPr',[],''),
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
        style_table={'minWidth': '100%', 'overflowX': 'auto'},  
        style_cell={
            # all three widths are needed
            'minWidth': '20px', #'width': '140px', 'maxWidth': '140px',
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
        style_data_conditional= red_failures(_2StPr_red_columns) + tweaked_widths,
        virtualization=True,
    ),
    html.H3("'results-2st-pr' command Audit Report:"),
    dcc.Markdown(
        id='2StPr-results-textarea',
        children='Results audit trail',
        style={'width': '100%', 'height': 400},
    ),    
])

''' callbacks '''

@app.callback(
    [Output('2StPr-results-table','tooltip_header'),
    Output('2StPr-recompute-msg-res','children'),
    Output('load-2StPr-results-btn','disabled'),
    Output('2StPr-results-textarea','children'),
    Output('2StPr-results-table','selected_columns'),
    ],
    Input('2StPr-load-audit-btn','n_clicks'),
    State('2StPr-results-table','columns'),
    prevent_initial_call=False
)
def load_2StPr_audit_results(n_clicks :int, columns :list):
        
    # returns a dict of audit lists, keyed on 'a1','a2', ...  'b', 'c' ...
    # computed and saved when command 'results-2st-pr' was most recently run
    _2StPr_conditions_audit_dict = g.CONFIG_RUNTIME['audit_structure_2StPr']
    
    tips = app_helpers.build_results_datatable_col_tooltips(columns, _2StPr_conditions_audit_dict)

    msg = f"For an 'Audit' view of a particular condition column (showing associated Ov columns), select a condition column"

    report = app_helpers.display_results_report('_2StPr')

    # also deselect any currently selected columns
    return [tips, msg, False, report,[]] 

@app.callback(
    [Output('2StPr-results-table','data'),
    Output('2StPr-results-table','columns'),
    Output('2StPr-status-msg-res','children'),
    Output('2StPr-audit-view-div','style'),
    Output('2StPr-results-table', 'page_size'),
    Output('2StPr-results-table','fixed_columns'),
    Output('2StPr-results-table','fixed_rows'),
    Output('2StPr-page-size-inp', 'value'),
    ],
    [Input('load-2StPr-results-btn','n_clicks'),
     Input('2StPr-results-table','selected_columns'),
    ],
    [State('2StPr-results-table','selected_columns'),
     State('all-2StPr-passing-chk','value')
     ],
    prevent_initial_call=True
)
def  load_2StPr_results(load_results_clicks, audit_cols, audit_cols_state :list, passing_spec):

    # we need to know how we got triggered - by 'load results' button 
    # or by 'back to results view' button. If the latter, we ignore and
    #  clear the selectect columns
    # see https://dash.plotly.com/advanced-callbacks

    print(f"passing_spec={passing_spec}")

    sharelist='Default'
    fixed_columns={ 'headers': True, 'data': 2 }
    fixed_rows={'headers':True, 'data':0}

    #we get our page size not from the input field, but rather from the runtime config
    #and in fact then update the input field with this value to reflect this value
    page_size_wanted = g.CONFIG_RUNTIME['2StPr_page_size']
    dash_page_size = page_size_wanted


    ctx = dash.callback_context
    if not ctx.triggered:
        load_button_id = 'No clicks yet' # should nver be
    else:
        load_button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if audit_cols is not None:
        # force a re-load into Audit view
        audit_cols_state = audit_cols
        load_button_id='load-2StPr-results-btn'

    # grab the extra ov columns for reference audit purposes from the tooltip_header
    # only one such column ought to be selected
    audit_view_style={'display' : 'none'}
    _2StPr_ov_audit_cols=[]
    col_under_audit = ''

    if load_button_id=='load-2StPr-results-btn' and isinstance(audit_cols_state,list) and len(audit_cols_state) > 0:
        col_under_audit = audit_cols_state[0] # eg 'Con_b1'
        _2StPr_ov_audit_cols=_2StPr_conditions[col_under_audit]['audit_list'] # eg ['DHP', 'DHOCP']

    col_specs=app_helpers.build_2StPr_results_datatable_column_dicts('2StPr', _2StPr_ov_audit_cols, col_under_audit)
    
    _2StPr_data = app_helpers.get_res_dataframe_as_dict('2StPr', sharelist, _2StPr_ov_audit_cols, passing_spec)    

    if col_under_audit != '':
        status_msg = f"In audit view, relevant columns are shown for the condition under focus. To filter a column for success use the expression contains '✓' or, for failure contains '🗙'" 
        audit_view_style={'display':'contents'}
    else:
        if _2StPr_data is None or len(_2StPr_data) == 0:
            if _2StPr_data is None:
                shim="Results could not be not found."
                status_msg = f"{shim}. Have you run the commands up to 'results-2st-pr' since you ran 'process-3' ?"
            elif len(_2StPr_data)==0:
                shim = f"{len(_2StPr_data)} rows"
                status_msg=f"{shim}. Conditions may be too strict. If you relax conditions, then re-run commands up to 'results-2st-pr' command. Click the 'update' link button afterwards"  
        else:
            shim = f"{len(_2StPr_data)} rows"
            status_msg = f"{shim}. Conditions may be adjusted on the Conditions tab, then re-run 'results-2st-pr' command. Click the 'update' link button afterwards"

    return [_2StPr_data, col_specs, status_msg, audit_view_style, 
            dash_page_size, fixed_columns, fixed_rows, page_size_wanted]

@app.callback(
    Output('load-2StPr-results-btn','n_clicks'),
    Input('btn-pagesize-2stPr','n_clicks'),
    State('2StPr-page-size-inp','value'),
    prevent_initial_call=True
)
def set_2StPr_pg_size(n_clicks,page_size):
    ''' respond to set page size btn link '''

    save_and_reload_page_size('2StPr_page_size', page_size)
    # this should cause a refresh
    return 0


# @app.callback(
#     Output('2StPr-results-table','filter_query'),
#     Output('2StPr-results-table','filter_action'),
#     Input('all-2StPr-passing-chk','value'),
#     prevent_initial_call=True
# )
# def filter_all_2StPr_passing(value):

#     filter_action = 'native'
#     qry=[]
#     if value=='all_passing':
#         qry.append('{Con_b1} contains ✓ AND {Con_b2} contains ✓ AND {Con_b3} contains ✓ AND {Con_b4} contains ✓ AND {Con_b5} contains ✓ AND')
#         qry.append('{Con_c1} contains ✓ AND {Con_c2} contains ✓ AND {Con_c3} contains ✓ AND {Con_c4} contains ✓ AND {Con_c5} contains ✓ AND')
#         qry.append('{Con_d1} contains ✓ AND {Con_d2} contains ✓ AND {Con_d3} contains ✓ AND {Con_d4} contains ✓ AND {Con_d5} contains ✓ AND')
#         qry.append('{Con_e1} contains ✓ AND {Con_e2} contains ✓ AND {Con_e3} contains ✓ AND {Con_e4} contains ✓ AND {Con_e5} contains ✓ AND')
#         qry.append('{Con_f} contains ✓ AND {Con_g} contains ✓ AND {Con_h} contains ✓ AND {Con_i} contains ✓ AND {Con_j} contains ✓')
#         filter_query=' '.join(qry)
#     elif value=='any_passing':
#         qry.append('{Con_b1} contains ✓ OR {Con_b2} contains ✓ OR {Con_b3} contains ✓ OR {Con_b4} contains ✓ OR {Con_b5} contains ✓ OR')
#         qry.append('{Con_c1} contains ✓ OR {Con_c2} contains ✓ OR {Con_c3} contains ✓ OR {Con_c4} contains ✓ OR {Con_c5} contains ✓ OR')
#         qry.append('{Con_d1} contains ✓ OR {Con_d2} contains ✓ OR {Con_d3} contains ✓ OR {Con_d4} contains ✓ OR {Con_d5} contains ✓ OR')
#         qry.append('{Con_e1} contains ✓ OR {Con_e2} contains ✓ OR {Con_e3} contains ✓ OR {Con_e4} contains ✓ OR {Con_e5} contains ✓ OR')
#         qry.append('{Con_f} contains ✓ OR {Con_g} contains ✓ OR {Con_h} contains ✓ OR {Con_i} contains ✓ OR {Con_j} contains ✓')
#         filter_query=' '.join(qry)
#     else:
#         filter_query=''
#         filter_action='none'

#     #print(filter_query)
#     return [filter_query,filter_action]
