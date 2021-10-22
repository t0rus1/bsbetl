import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from bsbetl import app_helpers, functions, g
from bsbetl.app import app
from bsbetl.app_helpers import init_page_size_input
from bsbetl.func_helpers import save_and_reload_page_size
from dash.dash import no_update
from dash.dependencies import ALL, MATCH, Input, Output, State
from dash.exceptions import PreventUpdate

############################################################

layout_results_3jP = html.Div(children=[
    html.H3(
        children=[
            html.Span('RESULTS 3.Stage, jumped Price "jP":', className='border-highlight')],
        className='tab-header'
    ),
    html.Div(
        children=[
            html.Button(
                id='btn-pagesize-3jP',
                children='set',
                className='link-button',
                title='set page size',
                style={'float': 'right'},
            ),
            dcc.Input(
                id='3jP-page-size-inp',
                type='number',
                min=10,
                max=2000,
                step=1,
                value=init_page_size_input('3jP_page_size'),
                placeholder='rows',
                style={'float': 'right'},
            )
        ]
    ),
    html.Div(
        children=[
            dcc.RadioItems(
                id='all-3jP-passing-chk',
                options=[
                    {'label': f'ONLY {g.PASS} values', 'value': 'passing_only'},
                    {'label': f'ONLY {g.FAIL} values', 'value': 'failing_only'},
                    {'label': f'Reset', 'value': 'clear_filtering'},
                ],
                value='clear_filtering'
            ),
            html.Button(
                id='load-3jP-results-btn',
                className='link-button-refresh',
                children="Apply / ReLoad",
                title='load current Results tables into the frames',
                style={'margin-right': '5px'},
                disabled=False,
            ),
            html.Div(
                id='3jP-status-msg-res',
                className='sw-muted-label',
                children="This page will display the results (if any) of the command 'results-3st-jp'",
                style={'display':'contents'}
            ),
        ]
    ),
    html.Div(
        id='3jP-audit-view-div',
        children=[
            html.Blockquote(
                children=[
                    'You are in restricted AUDIT view',
                    html.Button(
                        id='back-to-3jP-btn',
                        children='back to full Results view',
                        className='plain-link'
                    ),
                ],
                className='filter-query'
            )
        ],
        style={'display':'none'}
    ),
    html.H5(
        children=[
            html.Span('3jP Results', className='border-highlight')],
        className='tab-header'
    ),
    dash_table.DataTable(
        id='3jP-results-table',
        #columns=app_helpers.build_3jP_datatable_column_dicts(),
        #page_size=100,
        filter_action='native',  # 'native',
        filter_query='',
        sort_action='native',
        # sort_mode='multi',
        column_selectable='single',
        #fixed_columns={'headers': True, 'data': 2},
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
            'minWidth': '15px',# 'width': '135px', 'maxWidth': '135px',
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
        style_data_conditional=app_helpers.red_failures(['3. StjP1']),
        virtualization=True,
    ),
    dcc.Markdown(
        id='3jP-results-textarea',
        children='Results audit trail',
        style={'width': '100%', 'height': 400},
    ),    
])

@app.callback(
    [Output('3jP-results-table','data'),
    Output('3jP-status-msg-res','children'),
    Output('3jP-results-table', 'page_size'),
    Output('3jP-results-table', 'columns'),
    Output('3jP-results-table', 'fixed_columns'),
    Output('3jP-results-table', 'fixed_rows'),
    Output('3jP-results-textarea','children'),
    Output('3jP-page-size-inp', 'value'),
    ],
    [Input('load-3jP-results-btn','n_clicks'),
     Input('btn-pagesize-3jP','n_clicks')
    ],
    [State('all-3jP-passing-chk','value')
    ],
    prevent_initial_call=False
)
def  load_3jP_results(n_clicks, n_click2, passing_spec):

    # we need to know how we got triggered - by 'load results' button 
    # or by 'back to results view' button. If the latter, we ignore and
    #  clear the selectect columns
    # see https://dash.plotly.com/advanced-callbacks

    sharelist='Default'
    fixed_columns={'headers': True, 'data': 1}
    fixed_rows={'headers':True, 'data':0}

    #we get our page size not from the input field, but rather from the runtime config
    #and in fact then update the input field with this value to reflect this value
    page_size_wanted = g.CONFIG_RUNTIME['3jP_page_size']
    dash_page_size = page_size_wanted

    columns=app_helpers.build_3jP_datatable_column_dicts(sharelist)
    #print(columns)

    if len(columns)>0:
        # dataframe file exists
        data = app_helpers.get_res_dataframe_as_dict('3jP_part2', sharelist, [], passing_spec) 

        if data is None or len(data) == 0:
            if data is None: # unlikely
                status_msg = f"Results not found. Have you run the commands up to 'results-3st-jp' since you ran 'process-3'?"
            else: # data is empty
                status_msg = f"ZERO shares qualify for further jP related calculations."
                status_msg = status_msg + " (Inspect _Combined_1_2 results for reasons) then Adjust 'Conditions' (if applicable) on the Parameters tab and re-run from 'results-1st'"
        else:
            # expected, usual case
            status_msg = f"{len(data)} rows. Summarises results processing of Results 1, -2StPr, -2StVols and -3jP: Sort column '3. StjP1' ascending, to see the shares selected per section 3 St jP of doc '3 jumped Price 210623.odt"

        report = app_helpers.display_results_report('_3jP_part1')
    else:
        data = []
        num_3jP_shares = len(g.CONFIG_RUNTIME['_3jP_list'])
        if num_3jP_shares==0:
            status_msg = f"3jP results found no qualifying shares (no shares will be displayed)"
        else:
            status_msg = f"Data not found. Have you run the commands up to 'results-3st-jp' since you ran 'process-3'?"
        
        report = app_helpers.display_results_report('_3jP_part1')        
        fixed_columns = no_update

    return [data, status_msg, dash_page_size,columns,fixed_columns,fixed_rows,report, page_size_wanted]

@app.callback(
    Output('load-3jP-results-btn','n_clicks'),
    Input('btn-pagesize-3jP','n_clicks'),
    State('3jP-page-size-inp','value'),
    prevent_initial_call=True
)
def set_3jP_pg_size(n_clicks,page_size):
    ''' respond to set page size btn link '''

    save_and_reload_page_size('3jP_page_size', page_size)
    # this should cause a refresh
    return 0
