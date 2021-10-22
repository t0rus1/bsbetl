import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from bsbetl import app_helpers, g
from bsbetl.app import app
from bsbetl.app_helpers import init_page_size_input
from bsbetl.func_helpers import save_and_reload_page_size
from dash.dash import no_update
from dash.dependencies import ALL, MATCH, Input, Output, State
from dash.exceptions import PreventUpdate
from pandas.core.indexing import is_label_like

############################################################
_3V2d_red_columns = [ 'RbSDV.D-7÷RbSDV.D-4' ]


layout_results_3V2d = html.Div(children=[
    html.H3(
        children=[
            html.Span('RESULTS 3. Stage, Vol up few days (no big jump) "V2d":', className='border-highlight')],
        className='tab-header'
    ),
    html.Div(
        children=[
            html.Button(
                id='btn-pagesize-3V2d',
                children='set',
                className='link-button',
                title='set page size',
                style={'float': 'right'},
            ),
            dcc.Input(
                id='3V2d-page-size-inp',
                type='number',
                min=10, 
                max=2000,
                step=1,
                value=init_page_size_input('3V2d_page_size'),
                placeholder='rows',
                style={'float': 'right'},
            )
        ]
    ),
    html.Div(
        children=[
            dcc.RadioItems(
                id='all-V2d-passing-chk',
                options=[
                    {'label': f'ONLY {g.PASS} values', 'value': 'passing_only'},
                    {'label': f'ONLY {g.FAIL} values', 'value': 'failing_only'},
                    {'label': f'Reset', 'value': 'clear_filtering'},
                ],
                value='clear_filtering'
            ),
            html.Button(
                id='load-3V2d-results-btn',
                className='link-button-refresh',
                children="Apply / ReLoad",
                title="see audit trail report resulting from 'results-3st-v2d' command",
                style={'margin-right': '5px'},
                disabled=False,
            ),
            html.Div(
                id='3V2d-status-msg-res',
                className='sw-muted-label',
                children="This page displays the audit results (if any) of the command 'results-3st-v2d'. Actual shares qualifying will be found in the Overview for results V2d",
                style={'display':'contents'}
            ),
        ]
    ),
    html.Div(
        id='3V2d-audit-view-div',
        children=[
            html.Blockquote(
                children=[
                    'You are in restricted AUDIT view',
                    html.Button(
                        id='back-to-3V2d-btn',
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
            html.Span('3V2d Results', className='border-highlight')],
        className='tab-header'
    ),
    dash_table.DataTable(
        id='3V2d-results-table',
        #columns=app_helpers.build_3jP_datatable_column_dicts(),
        #page_size=100,
        filter_action='native',  # 'native',
        #filter_query='',
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
            'minWidth': '20px', #'165px', 'width': '165px', 'maxWidth': '165px',
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
        style_data_conditional=app_helpers.red_failures(_3V2d_red_columns),
        virtualization=True,
    ),
    dcc.Markdown(
        id='3V2d-results-textarea',
        children='Results audit trail',
        style={'width': '100%', 'height': 400},
    ),    
])

@app.callback(
    [Output('3V2d-results-table','data'),
    Output('3V2d-status-msg-res','children'),
    Output('3V2d-results-table', 'page_size'),
    Output('3V2d-results-table', 'columns'),
    Output('3V2d-results-table', 'fixed_columns'),
    Output('3V2d-results-table', 'fixed_rows'),
    Output('3V2d-results-textarea','children'),
    Output('3V2d-page-size-inp', 'value'),
    ],
    Input('load-3V2d-results-btn','n_clicks'),
    Input('btn-pagesize-3V2d','n_clicks'),
    State('all-V2d-passing-chk','value'),
    prevent_initial_call=False
)
def  load_3V2d_results(n_clicks, n_clicks2, passing_spec):

    # we need to know how we got triggered - by 'load results' button 
    # or by 'back to results view' button. If the latter, we ignore and
    #  clear the selectect columns
    # see https://dash.plotly.com/advanced-callbacks

    sharelist='Default' #'results_V2d'
    fixed_columns={ 'headers': True, 'data': 2 }
    fixed_rows={'headers':True, 'data':0}

    #we get our page size not from the input field, but rather from the runtime config
    #and in fact then update the input field with this value to reflect this value
    page_size_wanted = g.CONFIG_RUNTIME['3V2d_page_size']
    dash_page_size = page_size_wanted

    columns=app_helpers.build_3V2d_datatable_column_dicts(sharelist)
    if len(columns)>0:
        # dataframe file exists
        data = app_helpers.get_res_dataframe_as_dict('3V2d', sharelist, [], passing_spec ) 

        if data is None or len(data) == 0:
            status_msg = f"ZERO shares in Results"
        else:
            status_msg = f"{len(data)} shares presented. Sort the last column (RbSDV.D-7÷RbSDV.D-4) ascending to see which shares might qualify"

        report = app_helpers.display_results_report('_3V2d')
    else:
        data=[]
        status_msg = f"Data not found. Have you run the commands up to 'results-3st-v2d' since you ran 'process-3'?"
        report = status_msg
        fixed_columns = no_update

    return [data, status_msg, dash_page_size,columns,
                fixed_columns,fixed_rows,report,page_size_wanted]

@app.callback(
    Output('load-3V2d-results-btn','n_clicks'),
    Input('btn-pagesize-3V2d','n_clicks'),
    State('3V2d-page-size-inp','value'),
    prevent_initial_call=True
)
def set_3V2d_pg_size(n_clicks,page_size):
    ''' respond to set page size btn link '''

    save_and_reload_page_size('3V2d_page_size', page_size)
    # this should cause a refresh
    return 0

