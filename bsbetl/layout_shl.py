import os
from os.path import exists
import re
import dash
import random

import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import ALL, MATCH, Input, Output, State
from dash.exceptions import PreventUpdate
from dash_core_components.Checklist import Checklist
from dash_core_components.Dropdown import Dropdown

from bsbetl import app_helpers, g
from bsbetl.alltable_calcs import at_columns, at_params
from bsbetl.app import app
from bsbetl.functions import read_status_report_md, write_status_report_md
from bsbetl.ov_calcs import ov_columns, ov_params
from bsbetl.plots import plot_dashboard_share_chart
from bsbetl.func_helpers import save_and_reload_page_size

########################################################################
layout_shl = [
    dcc.ConfirmDialog(
        id='shl-confirm-newdefault',
        message='Overwrite existing Default sharelist? Are you sure?',
    ),
    html.H3(
        id='dummy-sink-1',
        children=[
            html.Span(f"SHARELISTS (the last process-3 cmd ran with sharelist '{g.CONFIG_RUNTIME['process-3-last-sharelist']}')", className='border-highlight')],
        className='tab-header'
    ),
    html.Div(
        [
            html.Button(
                id='shl-reload-sharelists',
                children='reload sharelists',
                className='link-button',
                title="re-sync the sharelists drop-down list below with the 'Sharelists' folder",
            ),
            html.Button(
                id='shl-overlay-master-btn',
                children="show the current sharelist's shares as selections in the master",
                className='link-button',
                title='use this option when you want to add new shares to an existing one',
                style={
                    'margin-left': '20px',
                },
            ),
            html.Button(
                id='shl-set-default',
                children='Make this sharelist the Default',
                className='link-button',
                title="copy the selected sharelist file to 'Default.shl', thereby changing the working default sharelist",
                style={'float': 'right', 'display': 'none'}
            ),
            dcc.Dropdown(
                id='shl-manage-dropdown',
                options=app_helpers.sharelists_options(
                    mastershares_wanted=True),
                value=g.SHARE_DICTIONARY_NAME,
                placeholder="Select a sharelist",
                className='dropdown',
            ),
            html.Div(
                '...',
                id='shl-rows-msg',
                className='status-msg',
            ),
            html.Div(
                [
                    dcc.Checklist(
                        id='shl-selecteds-only',
                        options=[
                            {'label': 'display selecteds only',
                                'value': 'selecteds_only'}
                        ],
                        style={
                            'display': 'inline',
                        }
                    ),
                    html.Button(
                        id='shl-save-btn',
                        className='link-button-refresh',
                        children='Save selecteds as a named sharelist',
                        title='save shares currently selected as a (new) sharelist',
                        style={
                            'display': 'inline',
                        }
                    ),
                    dcc.Input(
                        id='shl-input-save-name',
                        type='text',
                        size='40',
                        debounce=True,
                        placeholder="new sharelist name ('.shl' will be appended)",
                        style={'display': 'none'}
                    ),
                    # dcc.RadioItems(
                    #     id='shl-bourse-radioitems',
                    #     options=app_helpers.bourses_options(),
                    #     value=g.DEFAULT_BOURSE,
                    #     style={
                    #         'display': 'inline',
                    #         'float': 'right',
                    #     }
                    # ),
                    html.Button(
                        id='btn-pagesize-shl',
                        children='set',
                        className='link-button',
                        title='set page size',
                        style={'float': 'right'},
                    ),
                    dcc.Input(
                        id='shl-page-size-inp',
                        type='number',
                        min=10,
                        max=2000,
                        step=1,
                        value=g.CONFIG_RUNTIME['shl_page_size'],
                        #placeholder=f"{g.CONFIG_RUNTIME['shl_page_size']} rows",
                        style={'float': 'right'},
                    ),
                ]),
            html.Div(
                'Ready...',
                id='shl-status-msg',
                className='status-msg',
            ),
            html.Div(
                html.Button(
                    id='shl-toggle-selections-btn',
                    className='link-button',
                    children='toggle selections'
                ),
            ),
            dash_table.DataTable(
                id='shl-dash-table',
                columns=app_helpers.build_sharelist_datatable_columns(
                    g.MASTER_SHARELIST_COLUMNS_DASH),
                data=None,
                editable=False,
                filter_action='native',
                sort_action='native',
                # column_selectable='single',
                row_selectable='multi',
                # row_deletable=True,
                selected_columns=[],
                selected_rows=[],
                page_action='native',
                page_current=0,
                page_size=50,
                style_table={'overflowX': 'auto'},
                style_data_conditional=[
                    {
                        'if': {
                            'row_index': 'odd',  # number | 'odd' | 'even'
                        },
                        'backgroundColor': 'ghostwhite',
                    },
                ]
            ),
        ]
    ),
]

''' callbacks for layout_shl '''


@ app.callback(
    [Output('shl-dash-table', 'data'),
     Output('shl-dash-table', 'selected_rows'),
     Output('shl-set-default', 'style'),
     Output('shl-dash-table', 'page_current'),
     Output('shl-rows-msg','children'),
     Output('shl-dash-table', 'page_size'),
     ],
    [
     #Input('shl-bourse-radioitems', 'value'),
     Input('shl-manage-dropdown', 'value'),
     Input('shl-selecteds-only', 'value'),
     Input('shl-toggle-selections-btn', 'n_clicks'),
     Input('shl-overlay-master-btn', 'n_clicks'),
     Input('btn-pagesize-shl','n_clicks'),
     ],
    [
        State('shl-dash-table', 'selected_rows'),
        State('shl-dash-table', 'data'),
        State('shl-dash-table', 'page_current'),
        State('shl-page-size-inp', 'value')
    ],
)
def shl_react_change(sharelist, selecteds_only, toggle_clicks, _, set_pagesize_clicks, selected_rows, datatable_data, page_current, page_size_wanted): # bourse
    
    ctx = dash.callback_context
    # app_helpers.print_callback_context(ctx)

    # look thru ctx.triggered to see whether
    # the user perhaps clicked the 'toggle selections' btn
    # or the 'overlay-master' btn

    page_size = save_and_reload_page_size('shl_page_size', page_size_wanted)

    toggle_selections_triggered = False
    selecteds_only_triggered = False
    want_overlay_triggered = False
    page_to_show = page_current  # remain on page
    for entry in ctx.triggered:
        if entry['prop_id'] == 'shl-toggle-selections-btn.n_clicks':
            toggle_selections_triggered = True
        if entry['prop_id'] == 'shl-selecteds-only.value':
            selecteds_only_triggered = True
        if entry['prop_id'] == 'shl-overlay-master-btn.n_clicks':
            want_overlay_triggered = True
            page_to_show = 0  # force first page

    # make visible the 'set as default' link button if selected sharelist is not the Master
    if sharelist.startswith(g.SHARE_DICTIONARY_NAME) or sharelist == g.DEFAULT_SHARELIST_NAME:
        set_def_style = {'display': 'none'}
        page_to_show = 0
    else:
        # a normal sharelist
        set_def_style = {'display': 'inline', 'float': 'right'}
        page_to_show = 0

    # deal with the 'selecteds_only_triggered' situation early on becuase
    # we wont have to reload sharelist from disk
    # get it done and exit early
    selection_shares = []
    selection_ordinals = []
    if selecteds_only_triggered:
        # look thru current datatable_date and build new reduced table
        reduced_data = []
        for i, entry in enumerate(datatable_data):
            if i in selected_rows:
                reduced_data.append(entry)
        return [reduced_data, selection_ordinals, set_def_style, 0, 'selecteds only', page_size]

    # deal with the 'toggle_selections_triggered' situation early on becuase
    # we wont have to reload sharelist from disk
    # get it done and exit early
    if toggle_selections_triggered:
        # look thru current datatable_date and re-select
        reselected_data = []
        if len(selected_rows) > 0:
            for i, entry in enumerate(datatable_data):
                reselected_data.append(entry)
                if not i in selected_rows:
                    selection_ordinals.append(i)
            return [reselected_data, selection_ordinals, set_def_style, 0, 'selections toggled', page_size]
        else:
            # select every row
            for i, entry in enumerate(datatable_data):
                reselected_data.append(entry)
                selection_ordinals.append(i)
            return [reselected_data, selection_ordinals, set_def_style, 0, 'selected all', page_size]

    if True: #bourse == None:
        bourse = g.DEFAULT_BOURSE

    # filter in only memebrs of the sharelist
    filtering_sharelist = sharelist

    # gather up selection shares as per normal
    # if there are selected rows AND selected_only checkbox is set
    # then construct a selection_shares list (share numbers)
    if isinstance(datatable_data, list) and want_overlay_triggered or (isinstance(selecteds_only, list) and len(selecteds_only) > 0):
        new_index = 0
        for i in selected_rows:
            selection_shares.append(datatable_data[i]['number'])
            selection_ordinals.append(new_index)
            new_index = new_index+1
    elif isinstance(datatable_data, list) and (toggle_selections_triggered or want_overlay_triggered):
        # user may want simply to toggle selections. allow if display_selecteds only is not checked
        for i, entry in enumerate(datatable_data):
            if want_overlay_triggered or (toggle_clicks % 2 == 1):
                selection_shares.append(entry['number'])
                selection_ordinals.append(i)

    data_out = app_helpers.get_master_sharelist_dataframe_as_dict(
        g.MASTER_SHARE_DICT_FQ, bourse, filtering_sharelist, selection_shares, want_overlay_triggered)

    # if we had wanted_overlay, the above data_out returned would simply be the master sharelist content
    # therefore we need to re-select the selections which were previously selected
    if want_overlay_triggered:
        selection_ordinals = []
        # iterate thru the datatable we're about to output
        # selecting those rows which were present in the current datatable ie the
        # one about to be replaced
        for i, row in enumerate(data_out):
            row_share_number = row['number']
            if app_helpers.share_in_dashtable(datatable_data, row_share_number):
                selection_ordinals.append(i)

    num_rows = len(data_out)
    return [data_out, selection_ordinals, set_def_style, page_to_show, f'{num_rows} shares', page_size]


@ app.callback(
    Output('shl-confirm-newdefault', 'displayed'),
    Input('shl-set-default', 'n_clicks'),
    State('shl-manage-dropdown', 'value'),
    prevent_initial_call=True
)
def new_default_shl_wanted(n_clicks, sharelist):
    # display the confirm dialog
    return True


@ app.callback(
    Output('shl-confirm-newdefault', 'children'),
    Input('shl-confirm-newdefault', 'submit_n_clicks'),
    State('shl-manage-dropdown', 'value'),
    prevent_initial_call=True
)
def save_new_default_sharelist(submit_n_clicks, sharelist):
    # copy currently selected sharelist file over Default.shl

    def_shl_fq = f'{g.CONTAINER_PATH}\{g.SHARELISTS_FOLDER}\{g.DEFAULT_SHARELIST_NAME}'
    os.remove(def_shl_fq)

    src_shl_fq = f'{g.CONTAINER_PATH}\{g.SHARELISTS_FOLDER}\{sharelist}'
    os.system(f'copy {src_shl_fq} {def_shl_fq}')

    return f'New Default.shl written from {sharelist}'


@ app.callback(
    Output('shl-input-save-name', 'style'),
    Input('shl-save-btn', 'n_clicks'),
    State('shl-dash-table', 'selected_rows'),
    prevent_initial_call=True
)
def save_new_react(n_clicks, selected_rows):
    ''' reveal the input box for user to supply a sharelist name '''

    if isinstance(selected_rows, list) and len(selected_rows) > 0:
        return {'display': 'inline'}
    else:
        # no will do if no shares selected
        return {'display': 'none'}


@ app.callback(
    Output('shl-status-msg', 'children'),
    Output('shl-manage-dropdown', 'options'),
    Input('shl-input-save-name', 'value'),
    Input('shl-reload-sharelists', 'n_clicks'),
    State('shl-dash-table', 'selected_rows'),
    State('shl-dash-table', 'data'),
    prevent_initial_call=True
)
def save_new_sharelist(new_sharelist_name, n_clicks, selected_rows, data):

    # share_name                     number
    # ANHEUSER-BUSCH INBEV           A2ASUV.ETR
    # APPLE INC.                     865985.ETR

    #print(f'selected_rows={selected_rows}')

    selection_shares = ['share_name                     number\n']
    #                    0                              31
    existing_sharelists = app_helpers.sharelists_options(True)

    # despite this callback's name, we also get triggered by the 'reload sharelists' link button
    # if this was the trigger, we want to ONLY re-load the sharelists
    ctx = dash.callback_context
    # look thru ctx.triggered to see whether the user merely clicked the 'reload-sharelists' btn
    reload_triggered = False
    for entry in ctx.triggered:
        if entry['prop_id'] == 'shl-reload-sharelists.n_clicks':
            reload_triggered = True
    if reload_triggered:
        return ['Sharelists reloaded', existing_sharelists]

    if len(selected_rows) > 0:
        for i in selected_rows:
            entry = data[i]['share_name'].ljust(31) + data[i]['number'] + '\n'
            selection_shares.append(entry)

        if len(new_sharelist_name) > 0 and (not new_sharelist_name == g.SHARE_DICTIONARY_NAME):
            sharelist_filename_fq = f"{g.CONTAINER_PATH}\{g.SHARELISTS_FOLDER}\{new_sharelist_name}.shl"
            # do not overwrite an existing sharelist by the same name
            if not exists(sharelist_filename_fq):
                with open(sharelist_filename_fq, 'w') as shlf:
                    shlf.writelines(selection_shares)
                refreshed_sharelists = app_helpers.sharelists_options(True)
                return [f'sharelist {new_sharelist_name} saved as {sharelist_filename_fq}; Please reload sharelists.',
                        refreshed_sharelists,
                        ]
            else:
                return [f'Sharelist {new_sharelist_name} already exists! First delete the existing sharelist file (using File Explorer) if you want to use this name', existing_sharelists]
        else:
            return ['provide a valid sharelist name!', existing_sharelists]
    else:
        return ['No shares are selected!', existing_sharelists]

