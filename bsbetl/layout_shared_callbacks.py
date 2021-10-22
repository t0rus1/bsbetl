import os
from os.path import exists
import re

from dash.dependencies import ALL, MATCH, Input, Output, State

from bsbetl.app import app

''' callbacks here are referenced in more than one layout '''


# @app.callback(
#     Output('local-store', 'data'),
#     Input({'type': 'input-parameter', 'index': ALL}, 'value'),
#     [State({'type': 'input-parameter', 'index': ALL}, 'id'),
#      State('local-store', 'data')
#      ],
#     prevent_initial_call=True
# )
# def filter_parameter_changed(value, id, data):

#     data = data or {'dummy_key': 0}
#     for i, param_dict in enumerate(id):
#         # data[id[0]['index']] = value[0]
#         data[param_dict['index']] = value[i]

#     print(f'filter_parameter_changed. data={data}')
#     return data
