#from bsbetl.cli import start
#from bsbetl.functions import get_date_for_busdays_back, provide_datepicker
from os import environ
from dash.development.base_component import Component
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import ClientsideFunction, Input, Output
from dash_html_components.Button import Button
#from dash_html_components.Button import Button

from flask import request

from bsbetl.app import app
#from bsbetl.app import cache
from bsbetl.results import (layout_results_1St, layout_results_2StPr, layout_results_2StVols, layout_results_combined_1_2, layout_results_3jP, layout_results_3V2d, layout_results_3nH, layout_results_frt)
from bsbetl import (g, layout_ov, layout_at, layout_screener, layout_shl, layout_status, layout_parms, layout_conds, layout_at_charts) 


def serve_layout():
    return html.Div([
        # local storage
        dcc.Store(id='local-store', storage_type='memory'),
        #dcc.Store(id='local-graph-store', storage_type='memory'),

        # represents the URL bar, doesn't render anything
        dcc.Location(id='url', refresh=True),

        html.Button(id='scrollBtn',children='Go to top'),

        # app header across top
        html.Div(
            [
                #html.Div(id="hidden_div_for_redirect_callback"),
                html.Div(
                    id='top-banner-div',
                    children=[
                        html.Label(
                            children=f'SW post-processing Web Dashboard',
                            className='app-header--title'
                        ),
                        html.Label(
                            id='shwpy-version',
                            children=f'v{g.CONFIG_RUNTIME["version"]}', className='sw-muted-label',style={'margin-left': '5px'}),
                        html.Button(id='force-update-link', children='🗘 refresh', title='force a full page refresh',
                                    style={'float': 'right'}, className='link-button-refresh'),
                    ]
                )
            ],
            className='app-header',
        ),
        # nav buttons strip
        html.Div(
            className='nav-strip',
            children=[
                html.Label(' ➤ '),
                # dcc.Link('Commands', href='/apps/commands', className='dash-link', refresh=True),
                # dcc.Link('Shutdown', href='/shutdown', className='dash-link', refresh=True),
                dcc.Link('Status', href='/apps/status', className='dash-link', refresh=True),
                #dcc.Link('Settings', href='/apps/settings', className='dash-link', refresh=True),
                dcc.Link('Sharelists', href='/apps/shl', className='dash-link', refresh=True),
                dcc.Link('Screeners', href='/apps/screener', className='dash-link', refresh=True),
                dcc.Link('Parameters', href='/apps/parms', className='dash-link', refresh=True),
                dcc.Link('Conditions', href='/apps/conds', className='dash-link', refresh=True),
                dcc.Link('All-Tables', href='/apps/at', className='dash-link', refresh=True),
                dcc.Link('Results 1St', href='/apps/results-1St', className='dash-link', refresh=True),
                dcc.Link('...2StPr', href='/apps/results-2StPr', className='dash-link', refresh=True),
                dcc.Link('...2StVols', href='/apps/results-2StVols', className='dash-link', refresh=True),
                #dcc.Link('...Combined_1_2', href='/apps/results-combined-1-2', className='dash-link', refresh=True),
                dcc.Link('...3jP', href='/apps/results-3jP', className='dash-link', refresh=True),
                dcc.Link('...3V2d', href='/apps/results-3V2d', className='dash-link', refresh=True),
                dcc.Link('...3nH', href='/apps/results-3nH', className='dash-link', refresh=True),
                dcc.Link('Overviews', href='/apps/ov', className='dash-link', refresh=True),
                dcc.Link('Final Results', href='/apps/frt', className='dash-link', refresh=True),
                dcc.Link('Last-Chart', href='/apps/at_charts',target='_blank', className='dash-link', refresh=True, id='recent-charts-dcclink', title='if available, allows you to recall last chart rendered', style={'float': 'right'}),
            ]
        ),
        # dynamically filled page content
        html.Div(id='page-content')
    ])

app.layout = serve_layout

''' Click handler for the pop-up 'Go to top' button 
    See custom-script.js in the assets folder
'''
app.clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='top_function'
    ),
    Output('last-proc','children'),
    Input('scrollBtn','n_clicks')
)

def shutdown():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

#@cache.cached(timeout=10)
@ app.callback(Output('page-content', 'children'),
               [Input('url', 'pathname'),
                Input('force-update-link','n_clicks')
               ])
def display_page(pathname, n_clicks):
    ''' when browser location changes, this fires '''

    # change layout according to pathname
    # print(f'pathname={pathname}')

    # if pathname == '/apps/commands':
    #     #app.title='SW: commands'
    #     return layout_cmd.layout_cmd
    #cache.clear()

    if pathname =='/shutdown':
        shutdown()
        return html.Div([
            html.H3(f'You are on page {pathname} - the SW web server has been shut down. It can only be re-started via the Python terminal.')
        ])

    if pathname == '/apps/shl':
        #app.title='SW: sharelists'
        return layout_shl.layout_shl
    # elif pathname == '/apps/settings':
    #     #app.title='SW: settings'
    #     return layout_settings.layout_settings
    elif pathname == '/apps/screener':
        #app.title='SW: screener'
        return layout_screener.layout_screener
    elif pathname == '/apps/parms':
        #app.title='SW: params'
        return layout_parms.layout_parms
    elif pathname == '/apps/conds':
        #app.title='SW: conditions'
        return layout_conds.layout_conds
    elif pathname == '/apps/at':
        #app.title='SW: all-tables'
        return layout_at.layout_at
    elif pathname == '/apps/at_charts':
        #app.title='SW: charts'
        return layout_at_charts.layout_at_charts
    elif pathname == '/apps/results-1St':
        #app.title='SW: 1St results'
        return layout_results_1St.layout_results_1St 
    elif pathname == '/apps/results-2StPr':
        #app.title='SW: 2StPr results'
        return layout_results_2StPr.layout_results_2StPr  
    elif pathname == '/apps/results-2StVols':
        #app.title='SW: 2St Vols results'
        return layout_results_2StVols.layout_results_2StVols  
    elif pathname == '/apps/results-combined-1-2':
        #app.title='SW: 2St Vols results'
        return layout_results_combined_1_2.layout_results_combined_1_2
    elif pathname == '/apps/results-3jP':
        #app.title='SW: 2St Vols results'
        return layout_results_3jP.layout_results_3jP  
    elif pathname == '/apps/results-3V2d':
        #app.title='SW: 2St Vols results'
        return layout_results_3V2d.layout_results_3V2d  
    elif pathname == '/apps/results-3nH':
        #app.title='SW: 2St Vols results'
        return layout_results_3nH.layout_results_3nH  
    elif pathname == '/apps/ov':
        #app.title='SW: overviews'
        return layout_ov.layout_ov
    elif pathname == '/apps/frt':
        #app.title='SW: 2St Vols results'
        return layout_results_frt.layout_frt  
    else:
        # default page
        #app.title='SW: status'
        return layout_status.layout_status

if __name__ == '__main__':
    try:
        # set at the command line like this 
        # $env:BSB_DEV_TOOLS_UI='True'
        dtui = environ['BSB_DEV_TOOLS_UI']  
        app.run_server(debug=True, dev_tools_ui=(dtui == 'True'),)

    except KeyError:
        app.run_server(debug=True, dev_tools_ui=False)
