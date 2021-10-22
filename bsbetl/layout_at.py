import math

import dash
import dash_table
from dash import dcc, html
from dash.dependencies import (ALL, MATCH, ClientsideFunction, Input, Output,
                               State)
from dash.exceptions import PreventUpdate
from numpy.lib.function_base import append
from pandas.core.accessor import PandasDelegate

from bsbetl import app_helpers, g
from bsbetl.alltable_calcs import at_columns
from bsbetl.app import app
from bsbetl.app_helpers import at_data_style, init_page_size_input
from bsbetl.func_helpers import (config_shares_list_2_names_or_numbers,
                                 save_and_reload_page_size,
                                 save_runtime_config)
from bsbetl.plots import plot_dashboard_share_chart

layout_at = [
    html.H3(
        children=[
            html.Span(f'ALL_TABLES for period {g.CONFIG_RUNTIME["process-3-last-start"]} to {g.CONFIG_RUNTIME["process-3-last-end"]}', className='border-highlight')],
        className='tab-header'
    ),
    html.Div(
        id= 'dummy',
        children=''
    ),
    html.Div(
        id='conds-tab-summary',
        children='Inspect All-Table calculation results here (post processing). Select a share list and a share... NOTE: Up to 4 share lists (Default, 3jP, V2d, 3nH) should appear once all results processing has also been run',
        className='sw-muted-label'
    ),
    html.Div(children=[
        dcc.Dropdown(
            id='sharelists-dropdown',
            #options=app_helpers.sharelists_options(mastershares_wanted=True),
            options= app_helpers.alltables_sharelists_options(),
            value='Default.shl', # g.CONFIG_RUNTIME['last_processed_sharelist']+'.shl',
            placeholder="Select a sharelist",
            className='dropdown',
            style={'float': 'left', 'width': '260px'},
            persistence=True,
            persistence_type='local',
        ),
        dcc.Dropdown(
            id='shares-dropdown',
            # options=app_helpers.shares_dropdown_options('Default.shl'),
            placeholder="Select a share to view its all-table",
            optionHeight=26,
            value=None,
            className='dropdown',
            style={'float': 'left', 'width': '440px'},
            persistence=True,
            persistence_type='local',
        ),
        html.Label(id='at-share-info-label', children='selection info...', className='share-info'),
    ]),
    html.Div(children=[
        dcc.Slider(
            id='stage-at-slider',
            #tooltip={'always_visible': True, 'placement': 'bottom'},
            min=1,
            max=2,
            step=1,
            value=2,
            className='stages-slider',
            marks={
                1: 'Minutely',
                2: 'Daily',
                # 3: '3',
                # 4: '4',
            },
            included=False,
        ),
    ], style={'clear': 'both'}
    ),
    html.Div(children=[
        dcc.Dropdown(
            id='calcs-at-dropdown',
            options=app_helpers.get_at_calcs_dropdown_options(stage=0),
            placeholder="Column sets per calculation - NOTE calc results appear only in their respective Minutely/Daily All-Table (see slider above). Choose calc(s) , then click 'refresh')",
            multi=True,
            value=None,
            className='dropdown',
            style={'overflow': 'visible', 'width': '100%', },
        ),
    ], style={'clear': 'both'}
    ),
    html.Div(
        className='show-hide-container',
        children=[
            html.Button(
                id='btn-at-fields-reveal',
                className='link-button',
                children='Select|Hide All-Table Columns',
                title='click to reveal|hide column selection checkboxes',
                value='1',
            ),
            html.Button(
                id='at-refresh',
                className='link-button-refresh',
                children='refresh',
                value='1',
                title='click to display new selection of columns',
            ),
            html.Label(id='at-last-date-label', children='',
                       className='last-date-info'),
            dcc.Checklist(
                id='checklist-at-day-ends',
                options=[
                    {'label': 'Day-ends only', 'value': 'dayends'}
                ],
                value=[],
                labelStyle={'display': 'inline'},
                style={'display': 'inline', 'margin-right': '10px'},
            ),
            html.Button(
                id='btn-chart-selected-cols',
                className='link-button-refresh',
                children='Charts for columns selected in the table',
                title='charts those columns whose column headers are selected',
                value='1',
                #style={'float': 'right'}
            ),
            html.Div(id='selections_warning_div', children='Ensure desired column headers are selected',style={'display': 'none', 'margin-left': '10px', 'color': 'firebrick'}),
            html.Button(
                id='btn-lastpage-at',
                children='last pg',
                className='link-button',
                title='go to last page',
                style={'float': 'right'},
            ),
            html.Button(
                id='btn-pagesize-at',
                children='set',
                className='link-button',
                title='set page size',
                style={'float': 'right'},
            ),
            dcc.Input(
                id='at-page-size-inp',
                type='number',
                min=10,
                max=2000,
                step=1,
                value=init_page_size_input('at_page_size'),
                style={'float': 'right'},
            ),
            html.Button(
                id='btn-chart-set',
                className='link-button-refresh',
                children='Charts for selected Calculations',
                title='Charts all selected Calculations',
                value='1',
                style={'float': 'right', 'margin-right': '10px'}
            ),
        ], style={'overflow': 'hidden'}
    ),
    html.Div(
        id='at-containing-div',
        children=[
            html.Div(
                id='status-msg-at',
                className='status-msg',
            ),
            html.Div(
                id='at-fields-div',
                children=[
                    html.Div(children=[
                        dcc.Checklist(
                            id='at-fields-checklist',
                            #options=app_helpers.get_alltable_fields_options(),
                            value=app_helpers.get_alltable_fields_initial_values(),
                            labelStyle={'display': 'inline-block'}
                        ),
                    ], style={'overflow': 'hidden'}
                    ),
                ], style={'display': 'none'} # {'display': 'block', 'overflow': 'hidden'}
            ),
            html.Div(
                id='at-filter-query-div',
                children='',
                className='filter-query',
            ),
            dash_table.DataTable(
                id='share-dash-table',
                # columns=app_helpers.build_share_datatable_columns(),
                #fixed_columns={'headers': True, 'data': 1},
                page_action='native',
                page_current=0,
                page_size=10,
                data=None,
                filter_action='custom',  # 'native'
                filter_query='',
                sort_action='native',
                tooltip_duration=None,
                column_selectable='multi',
                #row_selectable='multi', 
                #row_selectable='single',
                selected_columns=[],
                selected_rows=[],
                # style_as_list_view=True,
                style_table={'minWidth': '100%'},
                style_header={
                    'backgroundColor': 'white',
                    'fontWeight': 'bold',
                    'border': '1px solid black',
                },
                style_cell={
                    # all three widths are needed
                    'minWidth': '80px',# 'width': '120px', 'maxWidth': '120px',
                    'overflow': 'hidden',
                    'textOverflow': 'ellipsis',
                },   
                style_data_conditional=at_data_style,
                persistence=True,
                persisted_props=['selected_rows'],
                virtualization=True,
            ),
        ], style={'overflow': 'hidden'}
    ),
]

''' callbacks for layout_at '''


@app.callback(
    Output('shares-dropdown', 'options'),
    Input('sharelists-dropdown', 'value'),
    #Input('bourse-radioitems', 'value')]
)
def sharelist_chosen(input_value): #, input1):
    mediated_input = 'Default.shl' if input_value == None else input_value
    bourse_filter_value = g.DEFAULT_BOURSE #if input_value == None else input1
    try:
        ddo = app_helpers.shares_dropdown_options(mediated_input, bourse_filter_value)
        return ddo
    except FileNotFoundError as exc:
        print(f'sharelist {input_value} not found. Have you perhaps started a process-3 again?')
        return dash.no_update


@app.callback(
    Output('at-fields-div', 'style'),
    [Input('btn-at-fields-reveal', 'n_clicks')],
    [State('at-fields-div', 'style')],
    prevent_initial_call=True
)
def at_columns_hide_select_chosen(n_clicks, input1: str):
    if input1 == {'display': 'none'}:
        return {'display': 'block'}
    else:
        return {'display': 'none'}

@app.callback(
    [Output('status-msg-at', 'children'),
     Output('share-dash-table', 'columns'),
     Output('share-dash-table', 'data'),
     Output('share-dash-table', 'tooltip_header'),
     Output('btn-chart-selected-cols', 'disabled'),
     Output('at-last-date-label', 'children'),
     Output('at-filter-query-div', 'children'),
     Output('share-dash-table', 'page_size'),
     Output('calcs-at-dropdown', 'options'),
     #Output('share-dash-table', 'page_current'),
     Output('at-fields-checklist','options'),
     Output('share-dash-table','fixed_columns'),
     Output('share-dash-table','fixed_rows'),
     Output('share-dash-table','row_selectable'),
     Output('at-page-size-inp', 'value')
     ],
    [Input('shares-dropdown', 'value'),
     Input('at-refresh', 'n_clicks'),
     Input('stage-at-slider', 'value'),
     Input('share-dash-table', 'filter_query'),
     ],
    [State('at-fields-checklist', 'value'),
     State('checklist-at-day-ends', 'value'),
     #State('virtual-cols-at-dropdown', 'value'),
     ],
)
def share_chosen(share_name_num: str, n_clicks: int, stage: int, filter, 
                 checked_cols: list, dayends_only: bool ): # virtual_cols: list,
    """ extract dataframe from HDFStore
        input_value is string containing share_name followed by share_number eg:
        ANGLO AMERICAN SP.ADR 1/2      A143BR.ETR
        or
        Use ALL Shares                 IGNORE
    """

    #we get our page size not from the input field, but rather from the runtime config
    #and in fact then update the input field with this value to reflect this value
    if stage==1:
        page_size_wanted=516
    else:
        page_size_wanted=g.CONFIG_RUNTIME['at_page_size']

    dash_page_size = page_size_wanted

    fixed_columns={} # { 'headers': True, 'data': 1 }
    fixed_rows={'headers':True, 'data':0}

    fields_chklist_options=app_helpers.get_alltable_fields_options(stage)

    calc_options = app_helpers.get_at_calcs_dropdown_options(stage)

    checked_col_specs = app_helpers.build_share_datatable_columns(checked_cols, stage, None) # virtual_cols

    col_tooltips = app_helpers.build_share_datatable_col_tooltips(checked_cols)
    

    if isinstance(share_name_num, str) and not share_name_num.endswith('IGNORE'):

        # retrieve and build data structure for the dash datatable - store globally
        at_columns.share_dict = app_helpers.get_share_dataframe_as_dict(
            share_name_num, checked_cols,
            stage=stage, dayends_only=dayends_only, filter=filter, virtual_cols=None)

        if isinstance(at_columns.share_dict, list):

            # date_time assumed ALWAYS selected
            first_dt = at_columns.share_dict[0]['date_time'][:11]
            last_dt = at_columns.share_dict[-1]['date_time'][:11]
            status_msg = f"{first_dt} → {last_dt} (last {len(at_columns.share_dict)} rows ... calculated from a 'start_date' of {g.CONFIG_RUNTIME['last_calculations_start_date']})"
            last_date_label_msg = f'last processed date: {last_dt}'
            # col_options_for_stage,
            return [status_msg, checked_col_specs, at_columns.share_dict, col_tooltips, 
                    False, last_date_label_msg, filter, dash_page_size, 
                    calc_options, fields_chklist_options, fixed_columns, 
                    fixed_rows, 'multi', page_size_wanted]
        else:
            status_msg = f"ERROR: '{share_name_num}' not found in SHARES store, stage {stage}. Inspect '{g.CSV_BY_SHARE_FOLDER}' folder & file of the share for clues. Perhaps no data for the period?"
            # col_options_for_stage,
            #return dash.no_update
            return [status_msg, checked_col_specs, None, None, True, 
                    filter, '',  dash_page_size, calc_options,  
                    fields_chklist_options, fixed_columns, 
                    fixed_rows,'multi', page_size_wanted]
    else:
        # col_options_for_stage,
        return ['Select the AT fields (aphabetically sorted) you would like displayed...', 
                None, None, None, True, filter, '',  dash_page_size, calc_options,
                fields_chklist_options, fixed_columns, 
                fixed_rows, 'multi', page_size_wanted]


@app.callback(
    Output('at-fields-checklist', 'value'),
    Input('calcs-at-dropdown', 'value')
)
def at_calculations_chosen(calcs_selected):

    #print(f'calcs_selected={calcs_selected}')
    if isinstance(calcs_selected, list) and len(calcs_selected) > 0:
        wanted_cols = ['date_time', 'price', 'volume']
        for cols_for_calc in calcs_selected:
            for col in cols_for_calc.split(','):
                wanted_cols.append(col)

        # print(wanted_cols)
        return wanted_cols
    else:
        # init_cols = app_helpers.get_alltable_fields_initial_values()
        # return init_cols
        raise PreventUpdate


@app.callback(
    Output('local-store', 'data'),
    Input({'type': 'input-parameter', 'index': ALL}, 'value'),
    [State({'type': 'input-parameter', 'index': ALL}, 'id'),
     State('local-store', 'data')
     ],
    prevent_initial_call=True
)
def filter_parameter_changed(value, id, data):
    ''' fires when plugin filter parameter is changed by the user
    NOTE we can get here from EITHER the all-tables OR overview tabs
    '''

    # print(f'filter_parameter_changed in. id={id}, data={data}')
    data = data or {'dummy_key': 0}
    for i, param_dict in enumerate(id):
        # data[id[0]['index']] = value[0]
        data[param_dict['index']] = value[i]

    #print(f'filter_parameter_changed out data={data}')
    return data


@app.callback(
    Output('selections_warning_div','style'),
    #Output("hidden_div_for_redirect_callback", "children"),
    Input('btn-chart-selected-cols', 'n_clicks'),
    [State('shares-dropdown', 'value'),
     State('share-dash-table', 'selected_columns'),
     State('stage-at-slider', 'value')
     ],
    prevent_initial_call=True
)
def selected_columns_chart_chosen(input_value: str, share_name_num: str, cols_to_plot: list, stage: int):
    ''' create a plot and get it displayed '''

    # (regular) cols_to_plot must be mediated by stage
    stage_cols = [
        col for col in cols_to_plot if (col in at_columns.AT_STAGE_TO_COLS[stage])] # or (col in virt_cols)]

    if len(cols_to_plot)>0 and isinstance(share_name_num, str) and len(share_name_num) > 0:
        # print(stage_cols)
        # print(at_columns.AT_COLS_AFFINITY)
        last_plot_tuple = plot_dashboard_share_chart(share_name_num, stage_cols, stage, data_source='local-store', use_config_date_range=True)
        app_helpers.assign_global_at_plot_values(last_plot_tuple)
        #print(f'selected_columns_chart_chosen, type(g.at_plot_df_datetime_col)={type(g.at_plot_df_datetime_col)}')
        #print(f'selected_columns_chart_chosen={g.at_plot_df_datetime_col}')
        return {'display': 'none', 'margin-left': '10px', 'color': 'firebrick'}
        #return dcc.Location(pathname='/apps/at_charts',id='does not matter')
    else:
        return {'display': 'inline', 'margin-left': '10px', 'color': 'firebrick'}
        #raise PreventUpdate

@app.callback(
    Output('dummy', 'children'),
    [Input('btn-chart-set', 'n_clicks'),
     State('calcs-at-dropdown', 'value')
    ],
    [State('shares-dropdown', 'value'),
     #State('share-dash-table', 'selected_columns'),
     State('stage-at-slider', 'value'),
     #State('virtual-cols-at-dropdown', 'value'),
     ],
    prevent_initial_call=True
)
def selected_calculations_chart_chosen(input_value: str, calcs_selected, share_name_num: str, stage: int):
    ''' create a plot and get it displayed '''

    #print(f'calcs_selected={calcs_selected}')
    cols_to_plot = ['date_time', 'price', 'volume']
    if isinstance(calcs_selected, list) and len(calcs_selected) > 0:
        for cols_for_calc in calcs_selected:
            for col in cols_for_calc.split(','):
                cols_to_plot.append(col)
    else:
        return ''

    # (regular) cols_to_plot must be mediated by stage
    stage_cols = [
        col for col in cols_to_plot if (col in at_columns.AT_STAGE_TO_COLS[stage])] # or (col in virt_cols)]

    #print(f'stage_cols={stage_cols}')

    if isinstance(share_name_num, str) and len(share_name_num) > 0:
        #print(f'stage_cols={stage_cols}')
        # print(at_columns.AT_COLS_AFFINITY)
        last_plot_tuple = plot_dashboard_share_chart(share_name_num, stage_cols, stage, data_source='hdf', use_config_date_range=True) #'hdf'
        app_helpers.assign_global_at_plot_values(last_plot_tuple)
        return ''
    else:
        return ''


@app.callback(
    Output('at-refresh','n_clicks'),
    Input('btn-pagesize-at','n_clicks'),
    State('at-page-size-inp','value'),
    prevent_initial_call=True
)
def set_at_page_size(n_clicks,page_size):

    save_and_reload_page_size('at_page_size', page_size)
    # this should cause a refresh
    return 0
    #return dash.no_update

@app.callback(
    Output('share-dash-table','page_current'),
    Input('btn-lastpage-at','n_clicks'),
    State('share-dash-table','data'),
    State('at-page-size-inp','value'),
)
def go_to_last_page(n_clicks, data, cur_page_size):

    if data is not None:
        last_page = math.ceil(len(data) / cur_page_size) - 1
        #print(last_page)
        return last_page
    else:
        return dash.no_update


@app.callback(
    Output('share-dash-table', "style_data_conditional"),
    Input('share-dash-table', "selected_rows")
)
def style_selected_rows(sel_rows):

    at_hilite_style = [ {"if": {"filter_query": "{{id}}={}".format(i)}, "backgroundColor": "lightgoldenrodyellow",} for i in sel_rows ]

    if sel_rows is None or len(sel_rows)==0:
        return dash.no_update

    val = at_data_style + at_hilite_style

    return val

@app.callback(
    Output('at-share-info-label','children'),
    Input('shares-dropdown', 'value'),
    prevent_initial_call = True
)
def update_share_info(share_and_number):

    sharelists_list = []
    _3jP_list = config_shares_list_2_names_or_numbers(g.CONFIG_RUNTIME['_3jP_list'],numbers_wanted=True)
    _V2d_list = config_shares_list_2_names_or_numbers(g.CONFIG_RUNTIME['_V2d_list'],numbers_wanted=True)
    _3nH_list = config_shares_list_2_names_or_numbers(g.CONFIG_RUNTIME['_3nH_list'],numbers_wanted=True)

    #Aareal Bank AG                 540811.ETR
    share_num = share_and_number[-11:-1] # there's a \n at the end of the line

    if share_num in _3jP_list:
        sharelists_list.append('3jP')
    if share_num in _V2d_list:
        sharelists_list.append('V2d')
    if share_num in _3nH_list:
        sharelists_list.append('3nH')

    inform=''
    if len(sharelists_list)>0:
        inform = f"this share is currently also in the following 'selection sharelist(s)': {', '.join(sharelists_list)}"

    return inform



