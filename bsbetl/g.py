import os
from os import environ
from enum import Enum
import pandas as pd

# the following suppresses the following type of warnings which
# gets issued when ypu try to save to an HD5 store:
# PerformanceWarning:
# your performance may suffer as PyTables will pickle object types that it cannot map
# directly to c-types [inferred_type->mixed,key->block2_values]
import warnings
warnings.filterwarnings("ignore")

from bsbetl.g_helpers import (establish_container_path, get_config_settings,
                              list_sharelists, load_master_share_dict, make_required_path)


''' bsbetl Globals and settings ''' 

# eg "c:\users\user\source\repos\shwpy\my_env\lib\site-packages
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# removing these restrictions to assist with printing dataframes to the console
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

BSBETL_SLUG = '\\BsbEtl'
# BSB_CONTAINER_PATH can be specified on the cmd line, else it MUST be in the environement:
# like so: $env:BSB_CONTAINER_PATH='\BsbEtl' (for Windows PowerShell)
# here we force it for convenience
environ['BSB_CONTAINER_PATH'] = BSBETL_SLUG

CONTAINER_PATH = establish_container_path()

DEFAULT_LOGNAME = 'ETL.log'
PROCESS3_WARNLOG_NAME = 'process3_warnings.log'
PROCESS3_WARNLOG_NAME_FQ = CONTAINER_PATH + '\\' + PROCESS3_WARNLOG_NAME

CSVMAXSIZE_WARNLOG_NAME = 'csv_maxsize_warnings.log'
CSVMAXSIZE_WARNLOG_NAME_FQ = CONTAINER_PATH + '\\' + CSVMAXSIZE_WARNLOG_NAME

# used to validate share numbers - see gen_one_share
BOURSES_LIST = ['ETR', 'FFM']
CALC_STAGES = [1, 2, ] 
DEFAULT_BOURSE = BOURSES_LIST[0]
IMG_FORMAT = '.png'
PASS = '✓'
FAIL = '🗙'
RESMAP = '{0:.5f}' # 5 digits default for results displays
MINIMUM_ANALYSIS_START_DATE = '2017_01_01'
# individual share trades file maximum size. Shares whose CSV trade files are bigger than this get skipped
CSV_TRADES_FILESIZE_MAX = 400*1024*1024 #400M
# all-table related
MINUTES_PER_TRADING_DAY = 516  # 9 am -> 5:36 pm

# paths

TXT_FOLDER = 'IN'
TXT_PATH = make_required_path(TXT_FOLDER, CONTAINER_PATH)

CONSUMED_FOLDER = 'CONSUMED'
CONSUMED_PATH = make_required_path(
    f'{TXT_FOLDER}\{CONSUMED_FOLDER}', CONTAINER_PATH)

OUT_FOLDER = 'OUT'
OUT_PATH = make_required_path(OUT_FOLDER, CONTAINER_PATH)

CSV_BY_DAY_FOLDER = 'OUT\\By_Day'
CSV_BY_DAY_PATH = make_required_path(CSV_BY_DAY_FOLDER, CONTAINER_PATH)

CSV_BY_SHARE_FOLDER = 'OUT\\By_Share'
CSV_BY_SHARE_PATH = make_required_path(CSV_BY_SHARE_FOLDER, CONTAINER_PATH)

SHARELISTS_FOLDER = 'Sharelists'
SHARELISTS_PATH = make_required_path(SHARELISTS_FOLDER, CONTAINER_PATH)

REPORTS_FOLDER = 'Reports'
REPORTS_PATH = make_required_path(REPORTS_FOLDER, CONTAINER_PATH)

SCREENER_FOLDER = 'Screeners'
SCREENER_PATH = make_required_path(SCREENER_FOLDER, CONTAINER_PATH)

SCREENER_RESULTS_FOLDER = 'Screener Results'
SCREENER_RESULTS_PATH = make_required_path(
    SCREENER_RESULTS_FOLDER, SCREENER_PATH)

DESIGNATED_SCREENER_FQ = SCREENER_PATH + "\\Designated_Combined_Screener.csv"

OV_QUERY_FILTERS_FOLDER = 'Query_Filters_Ov'
OV_QUERY_FILTERS_PATH = make_required_path(
    OV_QUERY_FILTERS_FOLDER, CONTAINER_PATH)

PARAMS_FOLDER = 'Parameters'
PARAMS_PATH = make_required_path(PARAMS_FOLDER, CONTAINER_PATH)

REQUIRED_SUBFOLDERS = [TXT_FOLDER, CSV_BY_DAY_FOLDER, CSV_BY_SHARE_FOLDER, SHARELISTS_FOLDER, REPORTS_FOLDER, OV_QUERY_FILTERS_FOLDER, PARAMS_FOLDER]

# these folders are assumed present in the source tree
ASSETS_FOLDER = 'assets'
XTRAS_FOLDER = 'xtras'

SHARE_STORE_FQ = CONTAINER_PATH + '\\' + CSV_BY_SHARE_FOLDER + '\\SHARES_{0}.h5'

OVERVIEW_STORE_FQ = CONTAINER_PATH + '\\' + CSV_BY_SHARE_FOLDER + '\\OVERVIEWS_{0}.h5' # {stage} is the param
HDFSTORE_OV_KEY = '{0}_{1}' # eg 'default_2' for default sharelist, stage 2

#_1St results
_1ST_RESULTS_STORE_FQ = OUT_PATH + '\\_1ST_RESULTS.h5'
HDFSTORE_1ST_RESULTS_KEY = '{0}'
# _2StPr results
_2STPR_RESULTS_STORE_FQ = OUT_PATH + '\\_2STPR_RESULTS.h5'
HDFSTORE_2STPR_RESULTS_KEY = '{0}'
#_2StVols results
_2STVOLS_RESULTS_STORE_FQ = OUT_PATH + '\\_2STVOLS_RESULTS.h5'
HDFSTORE_2STVOLS_RESULTS_KEY = '{0}'
# _Combined_1_2 results
_COMBINED_1_2_RESULTS_STORE_FQ = OUT_PATH + '\\_COMBINED_1_2_RESULTS.h5'
HDFSTORE_COMBINED_1_2_RESULTS_KEY = '{0}'

#_3jP results part1 (holds seelctions made at the start of 3jP run)
_3JP_RESULTS_PART1_STORE_FQ = OUT_PATH + '\\_3JP_RESULTS_PART1.h5'
HDFSTORE_3JP_RESULTS_PART1_KEY = '{0}'

_3JP_RESULTS_PART2_STORE_FQ = OUT_PATH + '\\_3JP_RESULTS_PART2.h5'
HDFSTORE_3JP_RESULTS_PART2_KEY = '{0}'

#_3jP results (final)
_3JP_RESULTS_FINAL_STORE_FQ = OUT_PATH + '\\_3JP_RESULTS_FINAL.h5'
HDFSTORE_3JP_RESULTS_FINAL_KEY = '{0}'

# 3v2D results
_3V2D_RESULTS_STORE_FQ = OUT_PATH + '\\_3V2D_RESULTS.h5'
HDFSTORE_3V2D_RESULTS_KEY = '{0}'
# 3nH results
_3NH_RESULTS_STORE_FQ = OUT_PATH + '\\_3NH_RESULTS.h5'
HDFSTORE_3NH_RESULTS_KEY = '{0}'

# Final Results 
_FRT_RESULTS_STORE_FQ = OUT_PATH + '\\_FRT_RESULTS.h5'
HDFSTORE_FRT_RESULTS_KEY = '{0}'

# json config settings files
# calculations will not be allowed to start earlier than CONFIG_SETTINGS
# set this to be congruent with the local data available
DEFAULT_CONFIG_SETTINGS = {"analysis_start_date": "2019_01_01"}
# NOTE this should not ever get loaded, since config_runtime.json is distributed in the bsbetl package
DEFAULT_CONFIG_RUNTIME = {
    "version": "not known",
    "last_calculations_start_date": "",
    "last_processed_sharelist": "Default",
    "last_process_3_date": "",
    "last_calculations_level": 1,
    "last_process_3_topup_date": "",
    "at_page_size": 516,
    "ov_page_size": 50,
    "1St_page_size": 50,
    "2StPr_page_size": 50,
    "2StVols_page_size": 50,
    "3nH_page_size": 50,
    "Combined_1_2_page_size": 50,
    "3jP_page_size": 50,
    "FRT_page_size": 50,
    "_3jP_list": [],
    "_V2d_list": [],
    "_3jP_list": [],
    "ov_at_plot_columns": [],
    "setting_chart_start": "",
    "setting_chart_end": "",
    "graph_height": 800,
    "graph_width": 1600,
}

# this one for read only settings
CONFIG_SETTINGS_FQ = BASE_DIR + f'{BSBETL_SLUG}\\config_settings.json'
CONFIG_SETTINGS = get_config_settings(
    CONFIG_SETTINGS_FQ, DEFAULT_CONFIG_SETTINGS)

# this one may be written to at run time. load it here so we know what was last saved
CONFIG_RUNTIME_FQ = BASE_DIR + f'{BSBETL_SLUG}\\config_runtime.json'
CONFIG_RUNTIME = get_config_settings(
    CONFIG_RUNTIME_FQ, DEFAULT_CONFIG_RUNTIME)

AT_CALC_PARAMS_FQ = PARAMS_PATH + '\\at_params.json'
OV_CALC_PARAMS_FQ = PARAMS_PATH + '\\ov_params.json'

_1_CONDITIONS_FQ = PARAMS_PATH + '\\_1_conditions.json'
_2STPR_CONDITIONS_FQ = PARAMS_PATH + '\\_2StPr_conditions.json'
_2STVOLS_CONDITIONS_FQ = PARAMS_PATH + '\\_2StVols_conditions.json'
_3JP_CONDITIONS_FQ = PARAMS_PATH + '\\_3jP_conditions.json'

# DP_INIT_CONDITIONS_FQ = PARAMS_PATH + '\\dp_init_conditions.json'
# DV_INIT_CONDITIONS_FQ = PARAMS_PATH + '\\dv_init_conditions.json'
# DP_STAGE2_CONDITIONS_FQ = PARAMS_PATH + '\\dp_stage2_conditions.json'


# load global sharelists list - has to be done early:
# the '\\BsbEtl' is a hardcoding fudge and will need to be changed
# if a container_path other than g.DEFAULT_CONTANER_PATH is desired
SHARELISTS_FOLDER_FQ = CONTAINER_PATH + '\\' + SHARELISTS_FOLDER
SHARELISTS = list_sharelists(SHARELISTS_FOLDER_FQ)

# main share list name
SHARE_DICTIONARY_NAME = 'MasterShareDictionary.csv'
DEFAULT_SHARELIST_NAME = 'Default.shl'
BSB_CODE_LOOKUP_NAME = 'BsbCodeLookup.csv'
BSB_CODE_LOOKUP_NAME_FQ = f"{CONTAINER_PATH}\{SCREENER_FOLDER}\{BSB_CODE_LOOKUP_NAME}"

# build a global master share dictionary - has to be done early:
# the '\\BsbEtl' is a hardcoding fudge and will need to be changed
# if a container_path other than g.DEFAULT_CONTANER_PATH is desired
MASTER_SHARE_DICT_FQ = CONTAINER_PATH + '\\' + SHARE_DICTIONARY_NAME
MASTER_SHARE_DICT = load_master_share_dict(
    MASTER_SHARE_DICT_FQ, BASE_DIR, BSBETL_SLUG, XTRAS_FOLDER, SHARE_DICTIONARY_NAME, SHARELISTS_FOLDER_FQ, DEFAULT_SHARELIST_NAME)
# share names starting like these entries dont get written to the master share dictionary
MASTER_SHARE_DICT_BLACKLIST = ['I.', 'IN.', 'INAV ']

STATUS_REPORT_NAME = 'StatusReport.txt'

# www.bsb-software.de maintains a text catalog of files on hand
SHARE_SERVICE_URL = "http://www.bsb-software.de/rese/"
# TODO: Maybe get user / password from environment variables ??
# SHARE_SERVICE_USER = "Rese"
SHARE_SERVICE_CATALOG_NAME = 'Inhalt.txt'

SHARELIST_HEADER = 'share_name                     number'
SHARE_CSV_HEADER = 'date_time,price,volume,vol_cum\n'

# ensure the other required query filters folders exist
for stage in range(1, 6):
    make_required_path(
        f'{OV_QUERY_FILTERS_FOLDER}\\stage{stage}', CONTAINER_PATH)

HEALTH_REPORT_TARGETS = ['Stored-AllTables', 'By-Share-CSVs']

# plots
PLOT_WIDTH = 24
PLOT_HEIGHT = 12

FIRST_BUS_HOUR_SLOT = 9
FIRST_BUS_MIN_SLOT = 0
LAST_BUS_HOUR_SLOT = 17
LAST_BUS_MIN_SLOT = 35

# this figure follows from resampling a datafram
# into 5 minute bands between 09:00 -> 17:55 inclusive
# (See csv_to_bus_hrs)
# NUM_ROWS_BUSDAY = 104
# although we accept any passed in start_date
# we dont pass dataframes through the calculation
# pipeline which go back more than 900 trading days
CALCS_MAX_BUSDAYS = 900
CALCS_NUM_BUSDAYS = 100

# master sharelist
MASTER_SHARELIST_COLUMNS = [
    'share_name',
    'number',
    'first_date',
    'last_date',
]

MASTER_SHARELIST_COLUMNS_DASH = [
    'share_name',
    'number',
    'first_date',
    'last_date',
]

BSB_CODE_LOOKUP_COLS = [
    'bsb_name',
    'bsb_number',
    # 'investing_name',
    'investing_symbol',
]

BSB_CODE_LOOKUP_COLS_TIPS = {
    'bsb_name': 'name of share (per BSB)',
    'bsb_number': 'number of share (per BSB)',
    # 'investing_name': 'name of share (per Investing.com, can be left blank)',
    'investing_symbol': 'share symbol (per Investing.com, must be filled)',
}

BSB_CODE_LOOKUP_HEADER = 'bsb_name,bsb_number,investing_name,investing_symbol'


class ScreenerDropdownOptions(Enum):
    OPTIONS = 1
    VALUES = 2


INVESTING_COM_SCREENER_COLS = [
    "Name", "Symbol", "Last", "Chg. %", "Market Cap", "Vol."
]

INVESTING_COM_USABLE_SCREENER_COLS = [
    "Name", "Symbol", "Last", "bsb_number"
]

DEFAULT_PLOTLY_COLORS=['rgb(31, 119, 180)', 'rgb(255, 127, 14)',
                       'rgb(44, 160, 44)', 'rgb(214, 39, 40)',
                       'rgb(148, 103, 189)', 'rgb(140, 86, 75)',
                       'rgb(227, 119, 194)', 'rgb(127, 127, 127)',
                       'rgb(188, 189, 34)', 'rgb(23, 190, 207)']


# these convenient to be global
df_ov = pd.DataFrame()

# global variables relating the Last Chart plotted
at_plot_figure = None
at_plot_df_datetime_col = None  # holds a dataframe 'date_time' column
at_plot_share_name_num = ''
at_plot_stage_cols=[]
at_plot_stage = 0
at_plot_data_source=''

latest_share_prices = {}
