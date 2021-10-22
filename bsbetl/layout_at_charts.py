import json
from datetime import date, datetime

from dash import dcc, html
from dash.dependencies import ALL, MATCH, Input, Output, State
from dash.exceptions import PreventUpdate
from numpy.lib.utils import lookfor

from bsbetl import app_helpers, g
from bsbetl.app import app
from bsbetl.func_helpers import save_runtime_config
from bsbetl.functions import provide_datepicker
from bsbetl.plots import plot_dashboard_share_chart

''' all-table charts '''

layout_at_charts = [
    html.Div(
        id='hidden-xaxis-div',
        children='not yet loaded',
        style={'clear': 'both', 'display': 'none'},
    ),
    html.Div(children=[
        html.Button(
            id='at-chart-reset-btn',
            children='Reset Calendars',
            title='Set date range to that which the process-3 command was last run',
        ),
        html.Label('Charting date range',style={'margin-left': '15px' }),
        dcc.DatePickerSingle(
            id='charts-date-picker-range-start',
            display_format='YYYY_MM_DD',
            month_format='YYYY_MM_DD',
            min_date_allowed=g.CONFIG_RUNTIME['process-3-last-start'].replace('_','-'),
            max_date_allowed=g.CONFIG_RUNTIME['process-3-last-end'].replace('_','-'),
            placeholder='Start Date',
            #initial_visible_month=g.CONFIG_RUNTIME['process-3-last-start'], 
            # updatemode='singledate',
            # persistence_type='memory',
            # persisted_props=[],
            # persistence=False
        ),            
        dcc.DatePickerSingle(
            id='charts-date-picker-range-end',
            display_format='YYYY_MM_DD',
            month_format='YYYY_MM_DD',
            min_date_allowed=g.CONFIG_RUNTIME['process-3-last-start'].replace('_','-'),
            max_date_allowed=g.CONFIG_RUNTIME['process-3-last-end'].replace('_','-'),
            placeholder='End Date'
            #initial_visible_month=g.CONFIG_RUNTIME['process-3-last-start'],
            # updatemode='singledate',
            # persistence_type='memory',
            # persisted_props=[],
            # persistence=False
        ),            
        html.Button(
            id='at-chart-apply-btn',
            children='Apply',
            title='Cause new date range to become effective'
        ),
        html.Label(
            id='at-chart-hover-label',
            children='',
            style={'color': 'tomato','margin-top': '15px', 'float': 'right'}
        ),
        html.Div(
            id='at-chart-status-msg',
            children='The last prepared chart (if available)...',
            className='status-msg'
        ),
        dcc.Graph(
            id='at-chart',
            # figure=g.at_plot_figure
        ),
    ])
]

@app.callback(
    [Output('charts-date-picker-range-start','date'),
    Output('charts-date-picker-range-end','date')],
    Input('at-chart-reset-btn','n_clicks'),
    prevent_initial_call=True
)
def reset_calendars(n_clicks):
    return [g.CONFIG_RUNTIME['process-3-last-start'].replace('_','-'), g.CONFIG_RUNTIME['process-3-last-end'].replace('_','-')]


@app.callback(
    [Output('hidden-xaxis-div', 'children'),
     Output('at-chart', 'figure')],
    Input('at-chart-apply-btn', 'n_clicks'),
    State('hidden-xaxis-div', 'children'),
    #prevent_initial_call=True
)
def refresh_chart(n_clicks, xaxis_lookup_dict_json):

    try:
        last_plot_tuple = plot_dashboard_share_chart(g.at_plot_share_name_num, g.at_plot_stage_cols, g.at_plot_stage, g.at_plot_data_source, use_config_date_range=True)
        if last_plot_tuple[1] is not None:
            # assume we can use it
            app_helpers.assign_global_at_plot_values(last_plot_tuple)
            #update the config chart_start and chart_end settings to the reality of the dataframe
            scs = last_plot_tuple[1].tolist()[0]
            sce = last_plot_tuple[1].tolist()[-1]
            if isinstance(scs,str) and isinstance(sce,str):
                pass
            else:
                # assume its a pandas Timestamp
                scs = scs.strftime('%Y-%m-%d')
                sce = sce.strftime('%Y-%m-%d')
            g.CONFIG_RUNTIME['setting_chart_start'] = scs
            g.CONFIG_RUNTIME['setting_chart_end'] = sce
            
            #save_runtime_config() 
        else:
            print('last_plot_tuple is None')
            raise PreventUpdate

    except AttributeError as exc:
        print(f'refresh_chart exception: {exc}')
        raise PreventUpdate


    if True: #xaxis_lookup_dict_json == 'not yet loaded':
        #print('not yet loaded')
        # first time: grab the date_time series in the global and store it for
        # ongoing use in the chart hover callbacks
        if g.at_plot_df_datetime_col is not None:
            dict_to_dump=g.at_plot_df_datetime_col.astype(str).to_dict()
            #print(f'dict_to_dump={dict_to_dump.values()}')
            hidden_xaxis_dict_json = json.dumps(dict_to_dump)
        else:
            raise PreventUpdate
    else:
        #print('loaded')
        # use what was previously stored
        hidden_xaxis_dict_json = xaxis_lookup_dict_json

    if (not g.at_plot_figure is None):
        #print(f'hidden_xaxis_dict_json={hidden_xaxis_dict_json}')
        return [hidden_xaxis_dict_json, g.at_plot_figure]
    else:
        raise PreventUpdate


@app.callback(
    Output('at-chart-hover-label', 'children'),
    Input('at-chart', 'hoverData'),
    State('hidden-xaxis-div', 'children'),
    prevent_initial_call=True
)
def display_hover_data(hoverData, xaxis_loopkup_json):
    ''' NOTE. must be improved
    It is very inefficient to be deserializing a large json string every hover event '''

    #{'points': [{'curveNumber': 0, 'pointNumber': 4615, 'pointIndex': 4615, 'x': 4615, 'y': 56.5}]}
    curve = hoverData['points'][0]['curveNumber']

    y_value = hoverData['points'][0]['y']
    y_val = '{:3}'.format(y_value)

    # x_value represents total minutes into the period
    x_value = hoverData['points'][0]['x']
    x_point_index = hoverData['points'][0]['pointIndex']

    # lookup the corresponding extact date time by referencing
    # the global dataframe column holding the original ['date_time'] column
    # NO, not any more - we refer to the json lookup data stored in the hidden div
    # which was originally grabbed from the global g.at_plot_df_datetime_col[x_value]
    #located_minute = g.at_plot_df_datetime_col[x_value]
    xaxis_info_dict = json.loads(xaxis_loopkup_json)

    # print(xaxis_info_dict)
    # print(str(x_value))

    try:
        located_minute = xaxis_info_dict[str(x_value)]
        return f"{located_minute} => {y_val}"  # " (curve {curve})"
    except KeyError:
        #located_minute = xaxis_info_dict[str(x_point_index)]
        pass
        return ''

@app.callback(
    Output('at-chart-status-msg','n_clicks'),
    Input('charts-date-picker-range-start','date'),
    State('charts-date-picker-range-end','date'),
    prevent_initial_call=True
)
def datepicker_start_changes(start,end):

    #print(start_date,end_date)
    g.CONFIG_RUNTIME['setting_chart_start'] = start # eg 2021-05-10
    save_runtime_config() 
    return 0

@app.callback(
    Output('at-chart-status-msg','children'),
    Input('charts-date-picker-range-end','date'),
    State('charts-date-picker-range-start','date'),
    prevent_initial_call=True
)
def datepicker_end_changes(end,start):

    g.CONFIG_RUNTIME['setting_chart_end'] = end # eg 2021-05-10
    save_runtime_config() 
    print(f"datepicker_end_change: {g.CONFIG_RUNTIME['setting_chart_end']}")
    return f"Date range: {start} --> {end}"

