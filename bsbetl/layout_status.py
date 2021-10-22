from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html

from bsbetl.app import app
from bsbetl.functions import read_status_report_md, write_status_report_md

layout_status = [
    html.Div(
        children=[
            html.H3(
                children=[
                    html.Span('STATUS', className='border-highlight')],
                className='tab-header'
            ),
            html.Button(
                children='refresh report',
                id='btn-refresh-status',
                className='link-button-refresh',
                title='create an updated status report',
                n_clicks=0,
            ),
            dcc.Link('Shutdown', href='/shutdown', className='dash-link', refresh=True, style={'float': 'right'}),
            dcc.Markdown(
                id='status-markdown',
                className='status-markdown',
                children=read_status_report_md()
            )
        ]
    )
]

''' callbacks for layout_status '''


@app.callback(
    Output('status-markdown', 'children'),
    Input('btn-refresh-status', 'n_clicks'), prevent_initial_call=False
)
def refresh_status(n_clicks):

    try:
        write_status_report_md()
    except KeyError as exc:
        print(f'KeyError \n\n{exc}')
        pass
    return read_status_report_md()
