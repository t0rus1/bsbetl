import os
import re
from os.path import exists

import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import ALL, MATCH, Input, Output, State
from dash.exceptions import PreventUpdate
from dash_core_components.Checklist import Checklist
from dash_core_components.Dropdown import Dropdown
from dash_html_components.Span import Span

#from flask_caching import Cache
#from bsbetl.app import cache
from bsbetl import app_helpers, g
from bsbetl.app import app
from bsbetl.func_helpers import save_and_reload_page_size, save_runtime_config
from bsbetl.app_helpers import init_page_size_input, ov_data_style
from bsbetl.ov_calcs import ov_columns, ov_params
from bsbetl.plots import plot_dashboard_share_chart

layout_ov = [
    html.H3(
        children=[
            html.Span(f'OVERVIEWS for period {g.CONFIG_RUNTIME["process-3-last-start"]} to {g.CONFIG_RUNTIME["process-3-last-end"]}', className='border-highlight')],
        className='tab-header'
    ),
    html.Div(
        id='conds-tab-summary',
        children='Inspect recently computed Overviews here (post process-3 & post result commands). Select for Sharelist and time granularity...',
        className='sw-muted-label'
    ),
    html.Div(children=[
        dcc.RadioItems(
            id='sharelists-stage-radio',
            options=app_helpers.get_overview_key_options(),
            #value=app_helpers.get_overview_fields_initial_values(),
            value=app_helpers.get_overview_key_default_value('Default_2'),
            labelStyle={'display': 'inline-block'}
        ),
        html.Button(
            children='Hide|Select Columns',
            id='btn-choose-ov-columns',
            className='link-button',
            title='click to set Overview columns',
        ),
        html.Button(
            children='refresh',
            id='btn-refresh-ov',
            className='link-button-refresh',
            title='click to re-display',
            style={'display': 'inline'},
        ),
        html.Button(
            id='btn-pagesize-ov',
            children='set',
            className='link-button',
            title='set page size',
            style={'float': 'right'},
        ),
        dcc.Input(
            id='ov-page-size-inp',
            type='number',
            min=10,
            max=2000,
            value=init_page_size_input('ov_page_size'),
            step=1,
            style={'float': 'right'},
        ),
    ], style={'overflow': 'hidden'}),
    html.Div(
        id='status-msg-calc-fields',
        children='Choose from Calculations in dropdown list below in order to preselect associated columns:',
        className='sw-muted-label',
    ),
    html.Div(children=[
        dcc.Dropdown(
            id='calcs-ov-dropdown',
            options=app_helpers.get_ov_calcs_dropdown_options(stage=0), 
            placeholder="Column selection by calculation and stage (click 'Refresh' once selected)",
            multi=True,
            value=None,
            className='dropdown',
            style={'overflow': 'visible', 'width': '100%', },
        ),
    ], style={'clear': 'both'}
    ),
    html.Div(
        children=[
            html.Div(
                id='status-msg-ov',
                className='status-msg',
                children='ready...',
                style={'overflow': 'hidden'}
            ),
            html.Div(
                id='div-ov-columns',
                children=[
                    dcc.Checklist(
                        id='ov-columns-checklist',
                        options=app_helpers.get_overview_fields_options(),
                        value=app_helpers.get_overview_fields_initial_values(),
                        labelStyle={'display': 'inline-block'}
                    ),
                ],
                style={
                    'display': 'block', 'overflow': 'hidden'
                }
            ),
            html.Hr(),
            html.Label('AT Variables to chart for currently selected share:'),
            html.Button(
                id='btn-charts-ov',
                className='link-button-refresh',
                children='Charts',
                # value='1',
                disabled=True,
                style={'float': 'right', 'margin-right': '10px'}
            ),
            html.Button(
                id='set-default-at-plot-columns',
                children='Set the selections below as default  - (restart web server after doing so)',
                className='link-button-refresh',
                style={'float': 'right'}
            ),
            html.Div(
                id='div-ov-at-columns',
                children=[
                    dcc.Checklist(
                        id='ov-at-columns-checklist',
                        options=app_helpers.get_alltable_fields_options(),
                        value=app_helpers.get_alltable_fields_plot_values(),
                        labelStyle={'display': 'inline-block'}
                    ),
                ],
                style={
                    'display': 'block', 'overflow': 'hidden', 'clear': 'both' 
                }
            ),
        ], style={'overflow': 'hidden'}
    ),
    html.Div(children=[
        dcc.Dropdown(
            id='ov-filter-dropdown',
            options=app_helpers.ov_filter_query_options(),
            placeholder='Select from previously saved filter queries...',
            optionHeight=26,
            className='dropdown',
        ),
        html.Form(
            id='ov-filter-query-form',
            children=[
                html.Span([
                    dcc.Input(
                        id='ov-filter-query-inp',
                        type='text',
                        debounce=True,
                        # size='115',
                        # className='filter-query'
                    ),
                ]),
                html.Button(
                    id='ov-filter-query-save-btn',
                    children='Save query',
                    disabled=True,
                    className='filter-query-btn',
                ),
                html.Span([
                    dcc.Input(
                        id='ov-filter-query-name-input',
                        type='text',
                        # size='60',
                        placeholder='supply a name (.ovq will be appended)',
                        debounce=True,
                        # style={
                        #     'display': 'none',
                        # }
                    )
                ]),
            ],
        ),
    ],
        style={'overflow': 'hidden'}
    ),
    dash_table.DataTable(
        id='overview-dash-table',
        columns=app_helpers.build_overview_datatable_column_dicts(ov_columns.OV_COLUMNS_INITIAL, 1),
        page_size=100,
        filter_action='native',  # 'native',
        filter_query='',
        sort_action='native',
        # sort_mode='multi',
        # column_selectable='single',
        #fixed_columns={'headers': True, 'data': 3},
        fixed_rows={'headers': True, 'data': 0},
        editable=True,
        cell_selectable=True,
        row_selectable='multi',
        # selected_rows=[],
        page_action='native',
        tooltip_duration=None,
        tooltip_delay=0,
        # style_as_list_view=True,
        # style_table={'overflowX': 'auto'},
        style_table={'minWidth': '100%'}, #{'overflowX': 'auto'},  
        style_cell={
            # all three widths are needed
            'minWidth': '100px', 'width': '100px', 'maxWidth': '100px',
            'overflow': 'hidden',
            'textOverflow': 'ellipsis',
        },   
        style_header={
                    'backgroundColor': 'white',
                    'fontWeight': 'bold',
                    'border': '1px solid black',
        },
        style_data_conditional=ov_data_style,
        virtualization=True,
    ),
    html.Div(
        id='div-ov-dummy'
    )
]


''' callbacks for layout_ov '''


@app.callback(
    Output('div-ov-columns', 'style'),
    Input('btn-choose-ov-columns', 'n_clicks'),
    State('div-ov-columns', 'style'),  prevent_initial_call=True,
)
def ov_columns_selection_chosen(n_clicks, input1: str):

    if input1 == {'display': 'none'}:
        return {'display': 'block'}
    else:
        return {'display': 'none'}


@app.callback(
    Output('overview-dash-table', 'filter_query'),
    Input('ov-filter-dropdown', 'value'),
    State('sharelists-stage-radio', 'value'),
    prevent_initial_call=True
)
def query_dropdown_changed(query_filter_file_name: str, shl_stage: int):
    ''' extract the query contained in the query filter file and apply 
    TODO dont allow filters which reference columns not currently on display
    '''

    # shl_stage = eg  '\Default_1'

    query_content = ''
    if isinstance(query_filter_file_name, str):
        query_filter_file_name_fq = f'{g.CONTAINER_PATH}\{g.OV_QUERY_FILTERS_FOLDER}\\stage{shl_stage[-1]}\{query_filter_file_name}.ovq'
        with open(query_filter_file_name_fq) as ovqf:
            query_content = ovqf.read()

    return query_content

@ app.callback(
    [Output('status-msg-ov', 'children'),
     Output('overview-dash-table', 'columns'),
     Output('overview-dash-table', 'data'),
     Output('overview-dash-table', 'tooltip_header'),
     Output('ov-filter-query-inp', 'value'),
     #Output('ov-columns-checklist', 'options'),
     Output('ov-filter-query-save-btn', 'disabled'),
     Output('ov-filter-dropdown', 'options'),
     Output('overview-dash-table','page_size'),
     Output('ov-page-size-inp', 'value'),
     Output('overview-dash-table', 'fixed_columns'),
     Output('overview-dash-table', 'fixed_rows'),
     ],
    [Input('btn-refresh-ov', 'n_clicks'),
     Input('sharelists-stage-radio', 'value'),
     Input('overview-dash-table', 'filter_query'),
     ],
    [State('ov-columns-checklist', 'value'),
     State('local-store', 'data'),
     ],
    prevent_initial_call=False
)
def overview_refresh_wanted(n_clicks, shl_stage, filter, columns, local_store_data):

    stage = int(shl_stage[-1])

    #we get our page size not from the input field, but rather from the runtime config
    #and in fact then update the input field with this value to reflect this value
    page_size_wanted=g.CONFIG_RUNTIME['ov_page_size']

    dash_page_size = page_size_wanted

    fixed_columns={} # {'headers': True, 'data': 3 }
    fixed_rows={'headers':True, 'data':0}

    datatable_col_specs = app_helpers.build_overview_datatable_column_dicts(columns, stage)

    col_tooltips = app_helpers.build_ov_datatable_col_tooltips(columns, stage)

    filter_options = app_helpers.ov_filter_query_options(stage)

    # input3, the local-store dictionary, holds our filter parameters as input by the user
    # example local-store dict for
    # {'dummy_key': 0, 'VolLastDay_0': 1, 'BroadnessAndVP_0': 1.4, 'BroadnessAndVP_1': 2000}
    # note the dictionary will in general contain many entries, a set for each filter plugin

    ov_dict = app_helpers.get_ov_dataframe_as_dict(columns, stage=stage, shl_stage=shl_stage) 

    if isinstance(ov_dict, list):
        status_msg = f'Overview {shl_stage} has {len(ov_dict)} rows'
        output_ary = [status_msg, datatable_col_specs, ov_dict, col_tooltips, 
                        filter,  False, filter_options, dash_page_size, page_size_wanted,
                        fixed_columns, fixed_rows]
        return output_ary
    else:
        print('overview_refresh_wanted: ov_dict returned was bad')
        # status_msg = f'Couldn\'t extract overview from HDFStore for overviews stage {stage}. See log file {g.DEFAULT_LOGNAME}'
        # return [status_msg, datatable_col_specs, None, col_tooltips, filter, enabled_ov_fields, filter == '']
        raise PreventUpdate


@app.callback(
    Output('ov-filter-query-name-input', 'style'),
    Input('ov-filter-query-save-btn', 'n_clicks'),
    State('ov-filter-query-name-input', 'value'),
    State('ov-filter-query-inp', 'value'),
    State('sharelists-stage-radio', 'value'),
    State('ov-filter-dropdown', 'options'),
    prevent_initial_call=True
)
def ov_filter_query_save_wanted(n_clicks: int, save_name: str, filter_query_content: str, shl_stage: int, cur_filter_queries):
    ''' save a new ov filter query '''

    #print(f'ov-filter-query-save-btn clicked savve_name={save_name}')
    stage=int(shl_stage[-1])

    if save_name == None:
        return {'display': 'inline-block'}
    else:
        # save the query content
        save_name = re.sub(r'\.ovq$', '', save_name)
        save_name_fq = f'{g.CONTAINER_PATH}\{g.OV_QUERY_FILTERS_FOLDER}\\stage{stage}\{save_name}.ovq'
        # lets have a backup copy
        bakup_name_fq = f'{save_name_fq}.bak'
        if exists(save_name_fq) and exists(bakup_name_fq):
            os.remove(bakup_name_fq)
            os.rename(save_name_fq, bakup_name_fq)
        # save
        with open(save_name_fq, 'w') as ovqf:
            ovqf.write(filter_query_content)

        #updated_filter_query_options = app_helpers.ov_filter_query_options(stage)

        # updated_filter_query_options]
        return {'display': 'none'}

@app.callback(
    Output('btn-charts-ov', 'disabled'),
    Input('overview-dash-table', 'active_cell'),
    prevent_initial_call=True
)
def share_selected(active_cell):
    disabled = active_cell is None
    return disabled


@app.callback(
    Output('div-ov-dummy', 'children'),
    Input('btn-charts-ov', 'n_clicks'),
    State('overview-dash-table', 'active_cell'),
    State('overview-dash-table', 'data'),
    State('sharelists-stage-radio', 'value'),
    State('ov-at-columns-checklist','value'),
    prevent_initial_call=True
)
def overview_charts_wanted(n_clicks, active_cell, tabledata, shl_stage, columns):
    # NOTE active_cell will only have a 'row_id' key if table data has a 'id' field
    # example active_cell:
    # {'row': 0, 'column': 3, 'column_id': 'VP', 'row_id': '511880.ETR'}

    # we need to locate data assoc with row_id
    #print(active_cell)
    #print(columns)

    stage=int(shl_stage[-1])

    if isinstance(active_cell, dict):
        rows = [row for row in tabledata if row['id'] == active_cell['row_id']]
        if len(rows) == 1:
            row_data = rows[0]
            share_name = row_data['ShareName']
            share_num = row_data['ShareNumber']
            # required_name_num_length = len('ANHEUSER-BUSCH INBEV           A2ASUV.ETR\n')
            share_name_num = share_name.ljust(31) + f'{share_num}\n'

            if isinstance(share_name_num, str) and len(share_name_num) > 0:
                try:
                    last_plot_tuple = plot_dashboard_share_chart(share_name_num, columns, stage, data_source='hdf',use_config_date_range=True)
                    app_helpers.assign_global_at_plot_values(last_plot_tuple)

                except:
                    # ignore it if user clicks on columns we dont intend to react on
                    # like eg ShareNumber, ShareName
                    pass
    else:
        print('no share selected?')

    return ''

@app.callback(
    Output('ov-columns-checklist', 'value'),
    Output('status-msg-calc-fields','children'),
    Input('calcs-ov-dropdown', 'value'),
    prevent_initial_call=True
)
def ov_calculations_chosen(calcs_selected):

    #col_options_for_stage = app_helpers.get_alltable_fields_options(stage)
    # if len(input_value) > 0 and input_value[0] == 'setall':
    #     return app_helpers.get_alltable_fields_allvalues()  # ['date_time']
    # else:
    #     return app_helpers.get_alltable_fields_initial_values()

    if isinstance(calcs_selected, list) and len(calcs_selected) > 0:
        wanted_cols = ['date_time', 'ShareNumber','ShareName']
        for cols_for_calc in calcs_selected:
            for col in cols_for_calc.split(','):
                wanted_cols.append(col)

        #print(f'wanted_cols={wanted_cols}')
        return [wanted_cols, f"[ {', '.join(wanted_cols)} ] "]
    else:
        init_cols = app_helpers.get_overview_fields_initial_values()
        return [init_cols, '']

@app.callback(
    Output('ov-at-columns-checklist','value'),
    Input('set-default-at-plot-columns','n_clicks'),
    State('ov-at-columns-checklist','value'),
    prevent_initial_call=True
)
def save_default_at_plot_columns(n_clicks,columns):

    if isinstance(columns,list) and len(columns)>0:
        scrubbed_columns = [col for col in columns if not col in ['date_time']]
        if len(scrubbed_columns) > 0:
            #print(scrubbed_columns)
            g.CONFIG_RUNTIME['ov_at_plot_columns'] = scrubbed_columns
            save_runtime_config()

    #re-affirm these
    at_cols = app_helpers.get_alltable_fields_plot_values()
    return at_cols

@app.callback(
    Output('btn-refresh-ov','n_clicks'),
    Input('btn-pagesize-ov','n_clicks'),
    State('ov-page-size-inp','value'),
    prevent_initial_call=True
)
def set_ov_page_size(n_clicks,page_size):

    save_and_reload_page_size('ov_page_size', page_size)
    # this should cause a refresh
    return 0
