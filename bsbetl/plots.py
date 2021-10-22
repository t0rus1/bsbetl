from datetime import timedelta
from numpy.core.fromnumeric import trace
from numpy.lib.twodim_base import _trilu_indices_form_dispatcher

import pandas as pd
from pandas.core.frame import DataFrame
import plotly.graph_objects as go
from plotly.missing_ipywidgets import FigureWidget

from bsbetl import g
from bsbetl.alltable_calcs import at_columns
from bsbetl.app_helpers import get_stored_df_by_sharelist_entry
from bsbetl.calc_helpers import between_dates_condition, daterange, get_start_end_date, one_day_filter

def trace_colour(index :int) ->int:
    return g.DEFAULT_PLOTLY_COLORS[index % len(g.DEFAULT_PLOTLY_COLORS)]


def secondary_axis_dict(variables,trace_num,var,max_price,min_price,max_volume,min_volume):
    return dict(
            title=f"{variables[trace_num-1]}",
            linecolor=trace_colour(trace_num-1),
            titlefont=dict(
                color=trace_colour(trace_num-1)
            ),
            tickfont=dict(
                color=trace_colour(trace_num-1)
            ),
            anchor="free",
            overlaying="y",
            side="left",
            position=0.075*(trace_num),
            showgrid=False,
            #range=[min_price,max_price] if var in at_columns.PRICE_AFFINITY else None,
            range=limit_range(var,min_price,max_price,min_volume,max_volume)            
        )

def limit_range(var,min_all_prices,max_all_prices,min_all_volumes,max_all_volumes):

    if var in at_columns.PRICE_AFFINITY:
        return [min_all_prices,max_all_prices]
    elif var in at_columns.VOLUME_AFFINITY:
        return [min_all_volumes,max_all_volumes]
    else:
        return None


def traces_to_panel(df_calcs, variables, panel_num, panel2vars, x_values, max_all_prices, min_all_prices,max_all_volumes, min_all_volumes) -> FigureWidget:

    fig = go.Figure()
    # go thru each panel and append traces
    for panel in range(1, panel_num+1):
        # gather each variable of the panel into a dict
        panel_y_values = {}
        for var in panel2vars[panel]:
            # fill forward any NaN valuesin 'Daily' columns
            if var in df_calcs.columns:  # g.AT_COLS_DAILY:
                df_calcs[var].fillna(value=None, method='ffill',
                                     axis='index', inplace=True)
            # add (another) column to the y_values to be plotted on this panel
            panel_y_values[var] = df_calcs[var].array

        trace_num = 1
        for yvals_var in panel_y_values.keys():
            #print(f'yvals_var={yvals_var}') 
            #also fig.append_trace
            if trace_num==1:
                fig.add_trace(
                    go.Scatter(name=yvals_var, marker_color=trace_colour(trace_num-1), x=x_values, y=panel_y_values[yvals_var]),
                    #row=panel, col=1
                )
                # primary y axis
                fig.update_layout(       
                    # spikedistance=1000,    
                    # xaxis=dict(
                    #     showspikes=True,
                    #     # Format spike
                    #     spikethickness=2,
                    #     spikedash="dot",
                    #     spikecolor="#999999",
                    #     spikemode="across",
                    # ),         
                    yaxis=dict(
                        title=f"{variables[trace_num-1]}",
                        linecolor=trace_colour(trace_num-1),
                        showgrid=False,
                        titlefont=dict(
                            color=trace_colour(trace_num-1)
                        ),
                        tickfont=dict(
                            color=trace_colour(trace_num-1)
                        ),
                        #range=[min_all_prices,max_all_prices] if yvals_var in at_columns.PRICE_AFFINITY else None,
                        range=limit_range(yvals_var,min_all_prices,max_all_prices,min_all_volumes,max_all_volumes)
                        # showspikes=True,
                        # # Format spike
                        # spikethickness=2,
                        # spikedash="dot",
                        # spikecolor="#999999",
                        # spikemode="across",
                    ),
                    
                )
                # if yvals_var in at_columns.PRICE_AFFINITY:
                #     fig.update_layout(yaxis=dict(range=[0, max_all_prices]))
            else:
                # rest of the traces
                fig.add_trace(
                    go.Scatter(name=yvals_var, marker_color=trace_colour(trace_num-1), x=x_values, y=panel_y_values[yvals_var], yaxis=f'y{trace_num}'),
                )
                if trace_num == 2:
                    fig.update_layout(
                        yaxis2=secondary_axis_dict(variables,trace_num,yvals_var,max_all_prices,min_all_prices,max_all_volumes,min_all_volumes),
                    )
                if trace_num == 3:
                    fig.update_layout(
                        yaxis3=secondary_axis_dict(variables,trace_num,yvals_var,max_all_prices,min_all_prices,max_all_volumes,min_all_volumes)                   
                    )
                if trace_num == 4:
                    fig.update_layout(
                        yaxis4=secondary_axis_dict(variables,trace_num,yvals_var,max_all_prices,min_all_prices,max_all_volumes,min_all_volumes)
                    )
                if trace_num == 5:
                    fig.update_layout(
                        yaxis5=secondary_axis_dict(variables,trace_num,yvals_var,max_all_prices,min_all_prices,max_all_volumes,min_all_volumes)
                    )
                if trace_num == 6:
                    fig.update_layout(
                        yaxis6=secondary_axis_dict(variables,trace_num,yvals_var,max_all_prices,min_all_prices,max_all_volumes,min_all_volumes)
                    )
                if trace_num == 7:
                    fig.update_layout(
                        yaxis7=secondary_axis_dict(variables,trace_num,yvals_var,max_all_prices,min_all_prices,max_all_volumes,min_all_volumes)
                    )
                if trace_num == 8:
                    fig.update_layout(
                        yaxis8=secondary_axis_dict(variables,trace_num,yvals_var,max_all_prices,min_all_prices,max_all_volumes,min_all_volumes)
                    )
                if trace_num == 9:
                    fig.update_layout(
                        yaxis9=secondary_axis_dict(variables,trace_num,yvals_var,max_all_prices,min_all_prices,max_all_volumes,min_all_volumes)
                    )
                # if yvals_var in at_columns.PRICE_AFFINITY:
                #     fig.update_layout(yaxis=dict(range=[0, max_all_prices]))

            trace_num=trace_num+1
            if trace_num > 9:
                break

        fig.update_xaxes(
            rangebreaks=[
                # hide weekends (only works on daily data)
                dict(bounds=["sat", "mon"]),
                # dict(values=["2015-12-25", "2016-01-01"])  # hide Christmas and New Year's
            ],
            # rangeslider_visible=True,
        )

    return fig

def build_panel_dictionaries(variables) -> tuple:
    
    var2panel = {}
    panel2vars = {}
    panel2titles = {}
    panel_num = 1

    for var in variables:
        #print(f'var in variables: var={var}')
        if len(var2panel) == 0:
            # first var goes into first panel
            var2panel[var] = panel_num
            panel2vars[panel_num] = [var]
            panel2titles[panel_num] = var
            #print(f'var {var} now assigned to panel_num {panel_num}. panel2vars[{panel_num}] is {panel2vars[panel_num]}')
        else:
            # panels already exist - can we overlay?
            # eg var = SDAP1 gives PRICE_AFFINITY
            own_affinity = at_columns.AT_COLS_AFFINITY[var]
            #print(f'next var {var}, has affinity {own_affinity}')
            # is there already a panel holding a variable with the same affinity?
            already_enpanneled_vars = [key for key in var2panel.keys()]
            #print(f'inspect already_enpanneled: {already_enpanneled_vars}')
            unassigned_to_panel = True
            for panel in panel2vars.keys():
                #print(f'checking affinities already in panel {panel}')
                for other_var in panel2vars[panel]:
                    if True: #at_columns.AT_COLS_AFFINITY[other_var] == own_affinity:
                        # we should overlay
                        var2panel[var] = panel
                        panel2vars[panel].append(var)
                        panel2titles[panel] = panel2titles[panel] + f', {var}'
                        unassigned_to_panel = False
                        break

            if unassigned_to_panel:
                #print(f'new panel required for {var}')
                # new panel required
                panel_num = panel_num+1
                var2panel[var] = panel_num
                panel2vars[panel_num] = []
                panel2vars[panel_num].append(var)
                panel2titles[panel_num] = var

    return (var2panel, panel2vars, panel2titles, panel_num)

def plot_dashboard_share_chart(share_name_num: str, variables: list, stage: int, data_source: str, use_config_date_range :bool) -> tuple:
    """ plotly express. create a chart for a share """

    #print(f'variables={variables}')
                       
    pd.options.plotting.backend = "plotly"

    # user does not need to have chosen date_time, in fact its not wanted
    try:
        variables.remove('date_time')
    except ValueError:
        pass

    # we no longer automatically pull the dataframe from the store
    # (since we now support plugin filters which add arbitrary columns)
    if data_source == 'hdf':
        df_calcs = get_stored_df_by_sharelist_entry(share_name_num, stage)
        #print(df_calcs.head(1))

    elif data_source == 'local-store':
        df_calcs = DataFrame(at_columns.share_dict)
    else:
        # should not happen
        return (None,None,None,None,None,None)

    # lets not have an index
    df_calcs.reset_index(inplace=True)
    #print(df_calcs.columns)

    # limit date range to that dictated by the last saved config_runtime range
    if False and use_config_date_range:
        chart_start=g.CONFIG_RUNTIME['setting_chart_start']
        chart_end=g.CONFIG_RUNTIME['setting_chart_end']
        #print(f'setting_chart_start & _end currently: {chart_start} {chart_end}')
        if (chart_start is not None) and (chart_end is not None):
            #date_range_condition = df_calcs.index.to_series().between(chart_start, chart_end)
            df_calcs = df_calcs[df_calcs['date_time'] >= chart_start]
            df_calcs = df_calcs[df_calcs['date_time'] <= chart_end]
            #df_calcs = df_calcs.copy()

    # ensure columns in a common affinity share the same scale
    prices=[]
    for var in variables:
        if var in at_columns.PRICE_AFFINITY:
            prices.append(var)
    prices_max = df_calcs[prices].max() # returns a series
    prices_min = df_calcs[prices].min() # returns a series
    max_of_all_prices = prices_max.max()
    min_of_all_prices = prices_min.min()
    
    volumes=[]
    for var in variables:
        if var in at_columns.VOLUME_AFFINITY:
            volumes.append(var)
    volumes_max = df_calcs[volumes].max() # returns a series
    volumes_min = df_calcs[volumes].min() # returns a series
    max_of_all_volumes = volumes_max.max()
    min_of_all_volumes = volumes_min.min()

      

    if stage == 1:
        # see https://strftime.org/
        # x_values = df_calcs['date_time']
        # NOTE unfortunately, with stage 1 (minute granularity) plotly inserts the weekend minutes into
        # the x_values regardless of the fact that this data IS NOT present
        # so we resort to using the default integer range (index was deleted above)
        x_values = df_calcs.index  # in minutes granularity - but no after hours or weekends
        # but note the column df_calcs['date_time'] is still present, so we can use this
        # to enable a hover lookup of integer index to obtain the actual date-time band
        # print(df_calcs['date_time'][140254])
    else:
        x_values = df_calcs['date_time']

    # print(f'x_values in the data range from {x_values[0]} to {x_values[-1]}')
    #print(f'x_values={x_values}')

    # df_calcs, as stored, contains days from config_settings.analysis_start_date

    # build a variable->panel dictionary 
    var2panel, panel2vars, panel2titles, panel_num = build_panel_dictionaries(variables)

    titles = []
    for panel in panel2titles.keys():
        titles.append(panel2titles[panel])

    # plot the traces in a figure widget
    fig = traces_to_panel(df_calcs, variables, panel_num, panel2vars, x_values, max_of_all_prices, min_of_all_prices, max_of_all_volumes, min_of_all_volumes)

    try:
        ht=g.CONFIG_RUNTIME['graph_height']
        wd=g.CONFIG_RUNTIME['graph_width']
    except KeyError:
        print(f"GRAPH HEIGHT and or WIDTH could not be retrieved from runtime config, using default values...")
        ht=800
        wd=1600

    granularity = 'minutes' if stage == 1 else 'daily'
    fig.update_layout(height=ht, width=wd, title_text=f'{share_name_num}    ({granularity})')
    #fig.show()  TODO restore this at some time

    return (fig, df_calcs['date_time'], share_name_num, variables, stage, data_source)
