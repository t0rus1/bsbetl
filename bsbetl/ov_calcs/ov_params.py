''' parameters for overview calculations '''
from bsbetl.g_helpers import load_prepare_params
import logging
from os.path import exists
import json
from bsbetl import g
from bsbetl.simple_param import SimpleParam

# DEFAULT all-table calc parmaters here
ovp_example_param = SimpleParam(
    name='ovp_example_param',
    calculation='none',
    min=100, max=1000_000, setting=4_000,
    doc_ref=''
)

# lazy
ovp_lazy_turnover = SimpleParam(
    name='ovp_lazy_turnover',
    calculation='laziness',
    min=100, max=1000_000, setting=4_000,
    doc_ref=''
)

ovp_lazy_zerovol_rows = SimpleParam(
    name='ovp_lazy_zerovol_rows',
    calculation='laziness',
    min=0, max=998, setting=50,
    doc_ref=''
)

# # dummyDaysAbovePriceSMA
# ovp_dummyAboveSMA = SimpleParam(
#     name='ovp_dummyAboveSMA',
#     calculation='dummyAboveSMA',
#     min=1, max=600, setting=200
# )

# transfer to a list
default_ov_params = [
    ovp_example_param,
    ovp_lazy_turnover,
    ovp_lazy_zerovol_rows,
]

# build the at_calc_params dict
ov_calc_params = load_prepare_params(
    g.OV_CALC_PARAMS_FQ, default_ov_params)
