from bsbetl.func_helpers import save_runtime_config
import json
import os
from os.path import exists
from shutil import copyfile
from tkinter import Checkbutton
import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from dash.dependencies import ALL, MATCH, Input, Output, State
from dash.exceptions import PreventUpdate
from dash_html_components.Label import Label
from dash_table.DataTable import DataTable

from bsbetl import app_helpers, g
from bsbetl import screener
from bsbetl.app import app
# temp_import_share_symbols)
from bsbetl.screener import (
    create_bsb_lookup_starter, create_sharelist_from_screener_df, delete_screener_constituents, refresh_bsb_lookup)

############################################################

layout_screener = html.Div(children=[
    html.H3(
        children=[
            html.Span('Investing.com SCREENERS (XETRA only at this stage)', className='border-highlight')],
        className='tab-header'
    ),
    # NOTE: keep for possible re-use
    # html.Button(id='bsb-lookup-import-btn', children='import hack'),
    html.Div(
        children='Ready...',
        id='screener-status-msg',
        className='status-msg',
    ),
    dcc.Tabs(
        id='tabs-screener',
        value='tab-bsb-lookup',
        parent_className='custom-tabs',
        children=[
            dcc.Tab(id='t1', label='Master BSB -> Investing.com share mapping',
                    value='tab-bsb-lookup', className='custom-tab', selected_className='custom-tab--selected',
                    children=[
                        html.Div(
                            children="A mapping between BSB 'Share Number' and Investing.com 'Symbol' is required to in order to be able to use Investing.com screener results files" +
                            "The left hand 2 columns come from the MasterShareDictionary.csv file (which is maintained by SW). However, the corresponding assigments of the right hand Symbol " +
                            "column must be *manually maintained*. Shares without such symbols will not be allowed to be included in sharelists you create in this sub-system.",
                            className='sw-muted-label',
                        ),
                        html.Div(
                            id='tabs-screener-content',
                            children=[
                                html.Button(
                                    id='bsb-lookup-create-new-btn',
                                    children="create a 'starter' mapping from Master Sharelist",
                                    disabled=True,
                                    className='link-button-refresh',
                                    title='enabled only when no mapping file yet exists',
                                ),
                                html.Div(
                                    id='bsb-lookup-feedback-div',
                                    children='',
                                    className='status-msg',
                                ),
                                html.Button(
                                    id='bsb-lookup-refresh-btn',
                                    children="Update mapping from latest Master Sharelist",
                                    disabled=True,
                                    className='link-button-refresh',
                                    title="add new shares, delete idle ones... enabled only when a mapping file already exists",
                                ),
                            ]
                        ),
                        html.Div(
                            children=[
                                html.Button(
                                    id='bsb-lookup-save-btn',
                                    children="Save",
                                    # disabled=True,
                                    className='link-button-refresh',
                                    style={'margin-top': '5px'}
                                ),
                                html.Label(
                                    id='bsb-lookup-saved-label',
                                    children='',
                                    style={'margin-left': '5px'},
                                    className='sw-muted-label',
                                )
                            ]
                        ),
                        html.Div(children=[
                            DataTable(
                                id='bsb-lookup-datatable',
                                columns=app_helpers.get_bsb_lookup_columns(),
                                page_size=100,
                                data=None,
                                editable=True,
                                row_deletable=True,
                                # export_format='csv',
                                # export_columns='all',
                                # export_headers='ids',
                                filter_query='',
                                sort_action='native',
                                filter_action='native',
                                tooltip_duration=None,
                                # column_selectable='multi',
                                selected_columns=[],
                                # style_as_list_view=True,
                                style_header={
                                    'backgroundColor': 'white',
                                    'fontWeight': 'bold',
                                    'border': '1px solid black',
                                },
                                style_table={
                                    'overflowX': 'auto', 'float': 'left', 'width': '68%'},
                                style_data={
                                    'height': 'auto',
                                    'lineHeight': '12px'
                                },
                                style_data_conditional=[
                                    {
                                        'if': {
                                            'column_id': 'bsb_name',
                                        },
                                        # 'backgroundColor': 'dodgerblue',
                                        'width': '140px',
                                    },
                                    {
                                        'if': {
                                            'column_id': 'bsb_number',
                                        },
                                        # 'backgroundColor': 'dodgerblue',
                                        'color': 'blue',
                                        'fontWeight': 'bold',
                                        # 'width': '100px',
                                    },
                                    {
                                        'if': {
                                            'column_id': 'investing.name',
                                        },
                                        # 'backgroundColor': 'dodgerblue',
                                        'width': '80px',
                                    },
                                    {
                                        'if': {
                                            'column_id': 'investing.symbol',
                                        },
                                        # 'backgroundColor': 'dodgerblue',
                                        'color': 'blue',
                                        'fontWeight': 'bold',
                                        # 'width': '130px',
                                    },
                                    {
                                        'if': {
                                            'row_index': 'odd',  # number | 'odd' | 'even'
                                            # 'column_id': 'date_time'
                                        },
                                        'backgroundColor': 'ghostwhite',
                                        # 'color': 'white'
                                    },
                                ],
                            ),
                            html.Button(
                                id='bsb-lookup-refresh-symbols',
                                children='Symbols lookup (Ctrl-F to search)',
                                className='link-button',
                                title='A recent combined screener file, designated on tab 3. Click to refresh'
                            ),
                            html.Plaintext(
                                id='bsb-lookup-symbols-text',
                                children=screener.get_symbols_help(),
                                style={'float': 'right', 'width': '30%', }
                            )
                        ])
                    ]
                    ),
            dcc.Tab(id='t2', label='Combine Screener results files into a single Screener file',
                    value='tab-screener-build', className='custom-tab', selected_className='custom-tab--selected',
                    children=[
                        html.Div(
                            children="Screener files (Screener Results*.csv) downloaded from Investing.com are assumed placed in the 'Screener Results' folder. " +
                            "Unless your criteria were very narrow, you likely had to download a number of separate pages of individual Screener Results files. " +
                            "These need first to be combined into one, and it can be done here. On hand (in the Screener Results folder) are the files below:",
                            className='sw-muted-label',
                        ),
                        html.Div([
                            dcc.Dropdown(
                                id='new-screener-file-dd',
                                # options=app_helpers.new_screener_contributor_options(g.ScreenerDropdownOptions.OPTIONS),
                                # value=app_helpers.new_screener_contributor_options(g.ScreenerDropdownOptions.VALUES),
                                multi=True,
                                persistence=False,
                                persistence_type='memory',
                                placeholder="Select Investing.com downloaded 'Screener Results*.csv' files to combine...",
                            )
                        ]),
                        html.Div(
                            children="Deselect what is not wanted and click the 'Combine' button to combine the remaining files into a single file - " +
                            "the name will be auto-assigned, based on the current date, so: Combined_YYYY_MM_DD.csv " +
                            "You will see this newly created screener file in the table below, once only. Thereafter you can work with this specific screener file on the third tab (even rename it)",
                            className='sw-muted-label',
                        ),
                        html.Button(
                            id='screener-combine-btn',
                            children='Combine into a single Screener',
                            className='link-button-refresh'
                        ),
                        dcc.Checklist(
                            id='screener-delete-once-combined-chk',
                            options=[{'label': 'delete the constituent files once combined',
                                      'value': 'yes'}],
                            value=['yes'],
                            style={'margin-left': '5px'}
                        ),
                        html.Label(
                            id='screener-delete-constituents-feedback-lbl',
                            children='',
                            className='sw-muted-label',
                        ),
                        DataTable(
                            id='bsb-combined-datatable',
                            columns=[{"name": i, "id": i}
                                     for i in g.INVESTING_COM_SCREENER_COLS],
                            page_size=100,
                            data=None,
                            editable=True,
                            row_deletable=True,
                            # export_format='csv',
                            # export_columns='all',
                            # export_headers='ids',
                            filter_query='',
                            sort_action='native',
                            filter_action='native',
                            tooltip_duration=None,
                            # column_selectable='multi',
                            selected_columns=[],
                            # style_as_list_view=True,
                            style_header={
                                'backgroundColor': 'white',
                                'fontWeight': 'bold',
                                'border': '1px solid black',
                            },
                            style_table={'overflowX': 'auto'},
                        ),
                    ]),
            dcc.Tab(id='t3', label='Combined Screeners',
                    value='tab-screener-use', className='custom-tab', selected_className='custom-tab--selected',
                    children=[
                        html.Div(
                            children=[
                                dcc.Dropdown(
                                    id='select-combined-dd',
                                    options=app_helpers.build_screener_files_options(
                                        g.ScreenerDropdownOptions.OPTIONS),
                                    placeholder="select a 'combined' screener file...",
                                    persistence_type='memory',
                                    style={'width': '280px', 'float': 'left'}
                                ),
                                html.Button(
                                    children="<== Use as 'Symbols lookup' on tab 1",
                                    id='screener-designate-btn',
                                    className='link-button',
                                    title='click to use this combined screener as the help reference for Symbols lookup list. (Previous list will be overwritten) (see tab 1)',
                                    style={'margin': '12px'}
                                ),
                                html.Label(
                                    id='symbols-lookup-feedback-label',
                                    children='',
                                    className='sw-muted-label',
                                    style={'margin': '12px'}
                                )
                            ],
                            style={'display': 'block'}
                        ),
                        html.Div(
                            children=[
                                dcc.Input(
                                    id='rename-screener-name-input',
                                    type='text',
                                    size='60',
                                    placeholder='new_screener_name_here',
                                    style={'width': '240px', 'float': 'left'},
                                ),
                                html.Button(
                                    id='rename-screener-btn',
                                    children='rename',
                                    className='link-button-refresh',
                                    style={'margin-left': '5px'},
                                    title="Optionally give the combined screener (selected above) a meaningful name. ('Screener_' gets prepended automatically, and '.csv' appended). Also renames any derived sharelist (if applicable)"
                                ),
                                html.Label(
                                    id='rename-screener-feedback-label',
                                    children='',
                                    style={'margin-left': '5px'},
                                    className='sw-muted-label',
                                )
                            ],
                            style={'clear': 'both'},
                        ),
                        html.Div(
                            children="Fill in the blank bsb_numbers here (or on tab 1), else the relevant share gets excluded from any sharelist you derive from the screener! " +
                            "NOTE. If you edit the bsb_number column here, don't forget to 'Save mapping edits'. This will update the Master BSB lookup table on tab 1 and thereby improve overall share mapping. " +
                            "When trying to fill empty bsb_number cells, use the lookup panel on the right: (Ctrl-F is helpful; a '?' indicates unknown last bsb price)",
                            className='sw-muted-label',
                            style={'clear': 'both'}
                        ),
                        html.Div(
                            children=[
                                html.Button(
                                    id='screener-use-save-btn',
                                    children="Save mapping edits",
                                    # disabled=True,
                                    className='link-button-refresh',
                                    title='save edits made in the bsb_number (virtual) column to the master BSB mapping file (see tab 1)',
                                    style={'margin-top': '5px'}
                                ),
                                html.Label(
                                    id='screener-use-saved-label',
                                    children='...',
                                    style={'margin-left': '5px'},
                                    className='sw-muted-label',
                                ),
                                html.Button(
                                    id='screener-use-deploy-btn',
                                    children="Deploy as sharelist",
                                    className='link-button-refresh',
                                    title='create|update a sharelist from this screener',
                                    style={'margin-top': '5px'}
                                ),
                                html.Label(
                                    id='screener-use-deploy-label',
                                    children='...',
                                    style={'margin-left': '5px'},
                                    className='sw-muted-label',
                                ),
                            ]
                        ),
                        html.Div(children=[
                            DataTable(
                                id='screener-use-datatable',
                                # columns=[{"name": i, "id": i} for i in g.INVESTING_COM_USABLE_SCREENER_COLS],
                                columns=app_helpers.get_use_screener_columns(),
                                page_size=100,
                                data=None,
                                editable=True,
                                row_deletable=True,
                                # export_format='csv',
                                # export_columns='all',
                                # export_headers='ids',
                                filter_query='',
                                sort_action='native',
                                filter_action='native',
                                tooltip_duration=None,
                                # column_selectable='multi',
                                selected_columns=[],
                                # style_as_list_view=True,
                                style_header={
                                    'backgroundColor': 'white',
                                    'fontWeight': 'bold',
                                    'border': '1px solid black',
                                },
                                style_table={
                                    'overflowX': 'auto', 'float': 'left', 'width': '68%'},
                                style_data={
                                    'height': 'auto',
                                    'lineHeight': '12px'
                                },
                                style_data_conditional=[
                                    {
                                        'if': {
                                            'column_id': 'bsb_number',
                                            'filter_query': "{bsb_number} is blank",
                                        },
                                        'backgroundColor': 'tomato'
                                    }
                                ]
                            ),
                            html.Plaintext(
                                children=screener.get_bsb_number_help(),
                                style={'float': 'right', 'width': '30%', }
                            )
                        ])

                    ]
                    ),
        ],
        style={'height': '36px'},
    ),
])


@ app.callback(
    [Output('bsb-lookup-datatable', 'data'),
     Output('bsb-lookup-datatable', 'tooltip_header'),
     Output('screener-status-msg', 'children'),
     Output('bsb-lookup-create-new-btn', 'disabled'),
     Output('bsb-lookup-refresh-btn', 'disabled'),
     Output('new-screener-file-dd', 'options'),  # on tab2
     Output('new-screener-file-dd', 'value'),
     Output('select-combined-dd', 'options'),  # on tab3
     ],
    Input('tabs-screener', 'value')
)
def render_lookup_content(tab):

    tooltips = app_helpers.build_bsb_lookup_col_tooltips()
    if tab == 'tab-bsb-lookup':
        if exists(g.BSB_CODE_LOOKUP_NAME_FQ):
            dict_lu, num_uncodeds = app_helpers.get_bsb_lookup_dataframe_as_dict(
                g.BSB_CODE_LOOKUP_NAME_FQ)
            return [dict_lu, tooltips, f'Lookup mapping has {len(dict_lu)} rows, 100 rows per page. {num_uncodeds} still requiring symbols',  True, False, [], None, []]
        else:
            dict_lu = []
            return [dict_lu, tooltips, f'BSBCode lookup file {g.BSB_CODE_LOOKUP_NAME_FQ} not found',  False, True, [], None, []]
    elif tab == 'tab-screener-build':
        dict_scr = []
        tooltips = {}
        notes = f'Build a new screener from downloaded Screener Results files (from Investing.com)'
        contributor_options = app_helpers.new_screener_contributor_options(
            g.ScreenerDropdownOptions.OPTIONS)
        contributor_value = app_helpers.new_screener_contributor_options(
            g.ScreenerDropdownOptions.VALUES)
        return [dict_scr, tooltips, notes, True, True, contributor_options, contributor_value, []]
    elif tab == 'tab-screener-use':
        dict_scr = []
        tooltips = {}
        notes = "A Screener file can be deployed as a sharelist. Below is shown the chosen downloaded, combined screener (with unimportant columns hidden). The last 'virtual' column shows a looked up bsb_number, flagged if not mapped"
        # refresh the combined screener options
        file_options = app_helpers.build_screener_files_options(
            g.ScreenerDropdownOptions.OPTIONS)
        return [dict_scr, tooltips, notes,  True, True, [], None, file_options]


@ app.callback(
    Output('bsb-lookup-feedback-div', 'children'),
    Input('bsb-lookup-create-new-btn', 'n_clicks'),
    Input('bsb-lookup-refresh-btn', 'n_clicks'),
    prevent_initial_call=True
)
def create_starter_or_refresh_lookup(n_clicks_new, n_clicks_refresh):

    ctx = dash.callback_context
    # for reference purposes:
    # ctx_msg = json.dumps({
    #     'states': ctx.states,
    #     'triggered': ctx.triggered,
    #     'inputs': ctx.inputs
    # }, indent=2)

    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    # just to be safe
    if button_id == 'bsb-lookup-create-new-btn' and not exists(g.BSB_CODE_LOOKUP_NAME_FQ):
        # create a bsb mapping file (and its dataframe) from scratch
        create_bsb_lookup_starter(g.BSB_CODE_LOOKUP_NAME_FQ)
        return f'BSBCode lookup file {g.BSB_CODE_LOOKUP_NAME_FQ} created. Please refresh the page.'
    elif button_id == 'bsb-lookup-create-new-btn' and exists(g.BSB_CODE_LOOKUP_NAME_FQ):
        # this should not occur, since the button to get us here should not have been enabled
        return f'BSBCode lookup file {g.BSB_CODE_LOOKUP_NAME_FQ} already present'
    elif button_id == 'bsb-lookup-refresh-btn' and exists(g.BSB_CODE_LOOKUP_NAME_FQ):
        # update add new shares (if any) and delete old ones by referencing current MastherShareDictionary.csv
        results_msg = refresh_bsb_lookup(g.BSB_CODE_LOOKUP_NAME_FQ)
        return results_msg
    else:
        ctx_msg = json.dumps({
            'states': ctx.states,
            'triggered': ctx.triggered,
            'inputs': ctx.inputs
        }, indent=2)
        print('callback create_starter_or_refresh_lookup. please investigate')
        print(ctx_msg)
        return 'not understood. see console'

# NOTE keep for possible re-use


@app.callback(
    Output('bsb-lookup-import-btn', 'children'),
    Input('bsb-lookup-import-btn', 'n_clicks'),
    prevent_initial_call=True,
)
def import_codes(n_clicks):
    ''' once off special means of importing from the old Shw system's Investing.com.msl.txt file (special hack) '''

    msl_codes_file_fq = "\BsbEtl\Screeners\Investing.com.msl.txt"
    if exists(msl_codes_file_fq):
        results_msg = screener.temp_import_share_symbols(
            g.BSB_CODE_LOOKUP_NAME_FQ, msl_codes_file_fq)
        return results_msg


@ app.callback(
    [Output('bsb-combined-datatable', 'data'),
     Output('screener-combine-btn', 'disabled'),
     Output('screener-delete-constituents-feedback-lbl', 'children'),
     ],
    Input('screener-combine-btn', 'n_clicks'),
    State('new-screener-file-dd', 'value'),
    State('screener-delete-once-combined-chk', 'value'),
    State('new-screener-file-dd', 'options'),
    prevent_initial_call=True,
)
def combine_screener_results(n_clicks: int, files_to_combine: list, delete_once_combined, csv_options):

    # print(delete_once_combined)
    # print(files_to_combine)
    #none_feedback = '{0} Screener Results*.csv files deleted'
    some_feedback = '{0} files combined into a single screener file'
    num_csvs_deleted = 0
    if isinstance(files_to_combine, list) and len(files_to_combine) > 0:
        df_dict = app_helpers.get_combined_screeners_as_dict(files_to_combine)
        if len(df_dict) > 0 and len(delete_once_combined) > 0:
            num_csvs_deleted = delete_screener_constituents(csv_options)
            return [df_dict, True, some_feedback.format(num_csvs_deleted)]
        else:
            return [df_dict, True, some_feedback.format(num_csvs_deleted)]
    else:
        return [None, False, some_feedback.format(num_csvs_deleted)]


@ app.callback(
    Output('screener-use-datatable', 'data'),
    Input('select-combined-dd', 'value'),
    prevent_initial_call=True
)
def screener_to_use_chosen(screener_file: str):

    # print(screener_file)
    if isinstance(screener_file, str) and exists(screener_file):
        dict_lu, _ = app_helpers.get_screener_dataframe_as_dict(screener_file)
        return dict_lu

    raise PreventUpdate()


@ app.callback(
    Output('bsb-lookup-saved-label', 'children'),
    Input('bsb-lookup-save-btn', 'n_clicks'),
    State('bsb-lookup-datatable', 'data'),
    prevent_initial_call=True
)
def save_bsb_lookup_datatable(n_clicks, data):

    app_helpers.save_dataframe_as_text(
        data, g.BSB_CODE_LOOKUP_NAME_FQ, g.BSB_CODE_LOOKUP_HEADER)

    return f'Table saved as {g.BSB_CODE_LOOKUP_NAME_FQ} ...'


@app.callback(
    Output('screener-use-saved-label', 'children'),
    Input('screener-use-save-btn', 'n_clicks'),
    State('screener-use-datatable', 'data'),
    prevent_initial_call=True
)
def save_mapping_edits(n_clicks, screener_data):
    ''' save the bsb_number column '''

    # try to locate in the BsbCodeLookup.csv file every bsb_number in the combined screener datatable
    # and ensure that its 4th (last) field is given the same Symbol value as found in the screener

    # print(screener_data[0:2])
    num_shares_saved = screener.update_bsb_code_lookup_from_screener(
        screener_data)

    result_msg = f'{num_shares_saved} saved'

    return result_msg


@app.callback(
    Output('symbols-lookup-feedback-label', 'children'),
    Input('screener-designate-btn', 'n_clicks'),
    State('select-combined-dd', 'value'),
    prevent_initial_call=True
)
def use_as_symbols_lookup_list(n_clicks, combine_fq):

    if isinstance(combine_fq, str):
        try:
            copyfile(combine_fq, g.DESIGNATED_SCREENER_FQ)
            return 'Done!'
        except IOError as e:
            print(
                f"Error. Unable to copy file {combine_fq} to {g.DESIGNATED_SCREENER_FQ}")
            return 'Error, failed!'
    else:
        return 'Select file first!'


@app.callback(
    Output('bsb-lookup-symbols-text', 'children'),
    Input('bsb-lookup-refresh-symbols', 'n_clicks'),
    prevent_initial_call=True
)
def refresh_symbols_lookup(n_clicks):

    text = screener.get_symbols_help()
    return text


@app.callback(
    [Output('rename-screener-feedback-label', 'children'),
     Output('screener-use-deploy-btn', 'children')],
    Input('rename-screener-btn', 'n_clicks'),
    State('select-combined-dd', 'value'),
    State('rename-screener-name-input', 'value'),
    State('screener-use-deploy-btn', 'children'),
    prevent_initial_call=True
)
def rename_screener_file(n_clicks, cur_name_fq, new_name, cur_deploy_btn_label):

    # cur_name_fq is already fully qualified

    if isinstance(cur_name_fq, str) and len(cur_name_fq) > 0 and exists(cur_name_fq):
        if isinstance(new_name, str) and len(new_name) > 0:
            new_name_fq = g.SCREENER_PATH + f'\\Screener_{new_name}.csv'
            os.rename(cur_name_fq, new_name_fq)
            return [f'{cur_name_fq} renamed to Screener_{new_name}.csv', f"Deploy as sharelist: '{new_name}'"]
        else:
            return [f'{new_name} not valid', cur_deploy_btn_label]
    return [f'{cur_name_fq} not valid', cur_deploy_btn_label]


@app.callback(
    Output('screener-use-deploy-label', 'children'),
    Input('screener-use-deploy-btn', 'n_clicks'),
    State('screener-use-deploy-btn', 'children'),
    State('select-combined-dd', 'value'),
    State('screener-use-datatable', 'data'),
    prevent_initial_call=True
)
def deploy_screener_as_sharelist(n_clicks, cur_deploy_btn_label, screener_name_fq, screener_data):
    ''' create|update a sharelist from current screener '''

    # to determine name to use we need to look at the button text
    # in case the screener was renamed to a different name from that of the dd list
    sharelist_name_fq = ''
    if ':' in cur_deploy_btn_label:
        # get the name from the button label
        name_start = cur_deploy_btn_label.find(':')
        name = cur_deploy_btn_label[name_start+2:]
        name = name.replace("'", "")
        sharelist_name_fq = g.SHARELISTS_FOLDER_FQ + f'\\Screener_{name}.shl'
    else:
        if isinstance(screener_name_fq, str) and screener_name_fq.endswith('.csv'):
            sharelist_name_fq = screener_name_fq.replace(
                g.SCREENER_FOLDER, g.SHARELISTS_FOLDER)
            sharelist_name_fq = sharelist_name_fq.replace('.csv', '.shl')

    if len(sharelist_name_fq) > 0:
        # print(sharelist_name_fq)
        create_sharelist_from_screener_df(screener_data, sharelist_name_fq)

    return f'Done. Deployed to {sharelist_name_fq}'
