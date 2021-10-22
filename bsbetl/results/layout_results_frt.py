import os
import re
from os.path import exists

import dash_core_components as dcc
import dash_html_components as html
import dash_table
from bsbetl import app_helpers, g
from bsbetl.alltable_calcs import at_columns, at_params
from bsbetl.app import app
from bsbetl.func_helpers import save_and_reload_page_size
from bsbetl.functions import read_status_report_md, write_status_report_md
from bsbetl.ov_calcs import frt_columns, ov_columns, ov_params
from bsbetl.plots import plot_dashboard_share_chart
from dash.dash import no_update
from dash.dependencies import ALL, MATCH, Input, Output, State
from dash.exceptions import PreventUpdate
from dash_core_components.Checklist import Checklist
from dash_core_components.Dropdown import Dropdown
from dash_html_components.Span import Span

layout_frt = [
    html.H3(
        children=[
            html.Span('FINAL RESULTS TABLE', className='border-highlight')],
        className='tab-header'
    ),
    html.Div(
        children=[
            html.Button(
                id='btn-page-size-frt',
                children='set',
                className='link-button',
                title='set page size',
                #style={'float': 'right'},
            ),
            dcc.Input(
                id='frt-page-size-inp',
                type='number',
                min=10, 
                max=2000,
                step=1,
                #value=app_helpers.init_page_size_input('FRT_page_size'),
                placeholder='rows',
                #style={'float': 'right'},
            )
        ],
    ),
    dcc.Dropdown(
        id='frt_views_dropdown',
        options=[
            {'label': 'Default View', 'value': 'default'},
            {'label': 'All Columns', 'value': 'all'}
        ],
        value='default',
        placeholder='preset(s) of columns to view',
        multi=False
    ),
    html.Div(
        children=[
            html.Button(
                id='load-frt-results-btn',
                className='link-button-refresh',
                children="(re)load FRT",
                title="see Final Results Table resulting from 'results-4st-frt' command",
                style={'margin-right': '5px'},
                disabled=False,
            ),
            html.Div(
                id='frt-status-msg-res',
                className='sw-muted-label',
                children="This page displays the audit results (if any) of the command 'results-4st-frt'.",
                style={'display':'contents'}
            ),
        ]
    ),
    dash_table.DataTable(
        id='frt-results-table',
        #columns=app_helpers.build_3jP_datatable_column_dicts(),
        page_size=100,
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
            'minWidth': '120px', # 'width': '120px', 'maxWidth': '160px',
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
        #style_data_conditional=app_helpers.red_failures(_3V2d_red_columns),
        virtualization=True,
    ),
    dcc.Markdown(
        id='frt-results-textarea',
        children='Final Results audit trail',
        style={'width': '100%', 'height': 400},
    ),    
    html.Div(
        id='div-frt-dummy'
    )
]


''' callbacks for layout_frt '''

@app.callback(
    [Output('frt-results-table','data'),
    Output('frt-status-msg-res','children'),
    Output('frt-results-table', 'page_size'),
    Output('frt-results-table', 'columns'),
    Output('frt-results-table', 'fixed_columns'),
    Output('frt-results-table', 'fixed_rows'),
    Output('frt-results-textarea','children'),
    Output('frt-page-size-inp', 'value'),
    ],
    [Input('load-frt-results-btn','n_clicks'),
    Input('btn-page-size-frt','n_clicks'),
    Input('frt_views_dropdown','value')],
    prevent_initial_call=False
)
def  load_frt_results(n_clicks, n_clicks2, view):

    # we need to know how we got triggered - by 'load results' button 
    # or by 'back to results view' button. If the latter, we ignore and
    #  clear the selectect columns
    # see https://dash.plotly.com/advanced-callbacks

    sharelist='Default' 
    fixed_rows={'headers':True, 'data':0}
    fixed_columns={ 'headers': True, 'data': 3 }
    default_cols = frt_columns.FRT_COLUMNS

    #we get our page size not from the input field, but rather from the runtime config
    #and in fact then update the input field with this value to reflect this value
    page_size_wanted = g.CONFIG_RUNTIME['FRT_page_size']
    dash_page_size = page_size_wanted

    wanted_cols=[]
    if 'default' == view:
        wanted_cols = [col for col in default_cols]
    elif 'all' == view:
        wanted_cols=[]

    # dont want fixed columns if too few on view anyway
    if len(wanted_cols) > len(default_cols):
        fixed_columns={ 'headers': True, 'data': len(default_cols) }
    

    columns=app_helpers.build_frt_datatable_column_dicts(sharelist,wanted_cols)
    if len(columns)>0:
        # dataframe file exists
        data = app_helpers.get_res_dataframe_as_dict('FRT', sharelist, [], None ) 

        if data is None or len(data) == 0:
            status_msg = f"ZERO shares in Results"
        else:
            status_msg = f"{len(data)} shares presented."

        report = app_helpers.display_results_report('_FRT')
    else:
        data=[]
        status_msg = f"Data not found. Have you run the commands up to 'results-3st-v2d' since you ran 'process-3'?"
        report = status_msg
        fixed_columns = no_update

    return [data, status_msg, dash_page_size,columns,
                fixed_columns,fixed_rows,report,page_size_wanted]


@app.callback(
    Output('load-frt-results-btn','n_clicks'),
    Input('btn-page-size-frt','n_clicks'),
    State('frt-page-size-inp','value'),
    prevent_initial_call=True
)
def set_FRT_pg_size(n_clicks,page_size):
    ''' respond to set page size btn link '''
    
    print(f'set_FRT_pg_size={page_size}')

    save_and_reload_page_size('FRT_page_size', page_size)
    # this should cause a refresh
    return 0
