from logging import disable
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import ALL, MATCH, Input, Output, State
from dash.exceptions import PreventUpdate
import dash_table
from pandas.core.indexing import is_label_like

from bsbetl import app_helpers, functions, g
from bsbetl.app import app
from bsbetl.func_helpers import save_and_reload_page_size

############################################################

layout_results_combined_1_2 = html.Div(children=[
    html.H3(
        children=[
            html.Span("Combined 1St,2StPr and 2StVols results (produced by the command 'results-3st-jp' from which onward share selection occurs)", className='border-highlight')],
        className='tab-header'
    ),
    html.Div(
        children=[
            html.Button(
                id='btn-pagesize-comb',
                children='set',
                className='link-button',
                title='set page size',
                style={'float': 'right'}, 
            ),
            dcc.Input(
                id='comb-page-size-inp',
                type='number',
                min=10,
                max=2000,
                step=1,
                placeholder='rows',
                style={'float': 'right'},
            )
        ]
    ),
    html.Div(
        children=[
            # dcc.RadioItems(
            #     id='sharelists-comb-stage-radio',
            #     options=app_helpers.get_results_key_options(g._COMBINED_1_2_RESULTS_STORE_FQ),
            #     value=app_helpers.get_results_key_default_value(g._COMBINED_1_2_RESULTS_STORE_FQ),
            #     labelStyle={'display': 'block'}
            # ),
            html.Button(
                id='load-comb-results-btn',
                className='link-button-refresh',
                children="Load results",
                title='load current Results tables into the frames',
                style={'margin-right': '5px'},
                disabled=False,
            ),
            # dcc.Checklist(
            #     id='all-1St-passing-chk',
            #     options=[
            #         {'label': 'Filter for ALL conditions passed', 'value': 'all_passing'},
            #     ],
            #     #value=[]
            # ),
            html.Div(
                id='comb-status-msg-res',
                className='sw-muted-label',
                children="This page displays the results after commands 'results-3st-jp1'",
                style={'display':'contents'}
            ),
        ]
    ),
    html.Div(
        id='comb-audit-view-div',
        children=[
            html.Blockquote(
                children=[
                    'You are in restricted AUDIT view',
                    html.Button(
                        id='back-to-comb-btn',
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
            html.Span('Combined 1_2 Results', className='border-highlight')],
        className='tab-header'
    ),
    dash_table.DataTable(
        id='comb-results-table',
        #columns=app_helpers.build_combined_1_2_datatable_column_dicts(),
        #page_size=100,
        filter_action='native',  # 'native',
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
            'minWidth': '150px', 'width': '150px', 'maxWidth': '150px',
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
        style_data_conditional=[
            {
                'if': {
                    'row_index': 'odd',  # number | 'odd' | 'even'
                    # 'column_id': 'date_time'
                },
                'backgroundColor': 'ghostwhite',
                # 'color': 'white'
            },
            {
                'if': {
                    'column_type': 'numeric',
                },
                'textAlign': 'right',
            },
        ],
    ),
])

@app.callback(
    [Output('comb-results-table','data'),
    Output('comb-status-msg-res','children'),
    Output('comb-results-table', 'page_size'),
    Output('comb-results-table','columns'),
    Output('comb-results-table','fixed_columns'),
    Output('comb-results-table','fixed_rows'),
    ],
    Input('load-comb-results-btn','n_clicks'),
    Input('btn-pagesize-comb','n_clicks'),
    State('comb-page-size-inp', 'value'),
    #State('sharelists-comb-stage-radio','value'),
    prevent_initial_call=False
)
def  load_combined_1_2_results(n_clicks, n_clicks2, page_size_wanted): #, sharelist :str):

    # we need to know how we got triggered - by 'load results' button 
    # or by 'back to results view' button. If the latter, we ignore and
    #  clear the selectect columns
    # see https://dash.plotly.com/advanced-callbacks

    sharelist = 'Default'
    #print(f'sharelist={sharelist}')
    fixed_columns={ 'headers': True, 'data': 3 }
    fixed_rows={'headers':True, 'data':0}

    page_size = save_and_reload_page_size('Combined_1_2_page_size', page_size_wanted)
    columns = app_helpers.build_combined_1_2_datatable_column_dicts(sharelist)

    data = app_helpers.get_res_dataframe_as_dict('combined_1_2', sharelist, [], None)    
    if data is not None and len(data)>0:
        #good case
        status_msg = f"{len(data)} rows. Serves as a summary of the preceding stages, used by the following stages."
        return [data, status_msg, page_size,columns, fixed_columns, fixed_rows]
    elif data is not None and len(data)==0:
        # zero shares
        status_msg = f"{len(data)} shares in the combined dataframe. Have you run the commands 'result-1', 'results-2st-pr' and 'results-2st-vols' as well as 'results-3st-jp1' ?"
    else:
        status_msg = f"results not found! - Have you run commands 'result-1', 'results-2st-pr' and 'results-2st-vols' as well as 'results-3st-jp1' ? Also, restart the web server to be sure."
        return [[], status_msg, page_size,columns,fixed_columns,fixed_rows] 


