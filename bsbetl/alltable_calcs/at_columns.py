''' ALL-TABLES calculation list and column defintions '''

from bsbetl.alltable_calcs import M_DailyHighPrice
from bsbetl.alltable_calcs.M_RelativeMinutelyVolume import M_RelativeMinutelyVolume
from bsbetl.alltable_calcs.D_BackwardsSlowDailyVol import D_BackwardsSlowDailyVol
from bsbetl.alltable_calcs.M_ParticularSumOfMV import M_ParticularSumOfMV
from bsbetl.alltable_calcs._1St_DailyPrices import _1St_DailyPrices
from bsbetl.alltable_calcs._2StPr_HundredDaysBroadness import _2StPr_HundredDaysBroadness
from bsbetl.alltable_calcs._2StPr_PriceHighestSince import _2StPr_PriceHighestSince
#from bsbetl.alltable_calcs._2StPr_AvgOfDailyAvgPriceGradient import _2StPr_AvgOfDailyAveragePriceGradient
from bsbetl.alltable_calcs._2StPr_AvgOfDailyHighPriceGradient import _2StPr_AvgOfDailyHighPriceGradient
from bsbetl.alltable_calcs._2StPr_SlowDailyLowerOCPriceGradient import _2StPr_SlowDailyLowerOCPriceGradient
from bsbetl.alltable_calcs._2StPr_SlowBroadness import _2StPr_SlowBroadness

# these will be slowly replaced
from bsbetl.alltable_calcs._2StVols_SlowDailyVols import _2StVols_SlowDailyVols
from bsbetl.alltable_calcs._2StVols_ModifiedDailyVol import _2StVols_ModifiedDailyVol
#from bsbetl.alltable_calcs.M_DailyAveragePrice import M_DailyAveragePrice
from bsbetl.alltable_calcs.M_DailyHighPrice import M_DailyHighPrice
from bsbetl.alltable_calcs.M_SpecialSlowMinutePrices import M_SpecialSlowMinutePrices

# NOTE maintain these so that the calculations may be offered 
# in the drop downs in the all-table view!
at_calcs_stage_1_list = [
    # 'TO', 'AvMV','ODV','SDT','DT','DT1','DHP', 'DLP', 'DMP', 'DCP', 'DHOCP', 'DLOCP', 'DOP', 'DHPbig', 'DLPsmall', 
    M_DailyHighPrice(), 
    # 'PSMV','CV1','RCV1','MVm','AvMVdec' 
    M_ParticularSumOfMV(), 
    # 'SMVms','RMVms','SMPGrmsbig', 'MSmp', 'MSmpv', 'MSmv',
    M_RelativeMinutelyVolume(), 
    # 'SMPmsf','SMPmsm','SMPmssl','SMPmsb', 'SMPGrmsf', 'SMPGrmsm', 'SMPGrmssl', 'SMPGrmsb'
    M_SpecialSlowMinutePrices(), 
]

at_calcs_stage_2_list = [
    #'SDHP1sh','SDHP1m','SDHP1lo', 'SDHPGr1sh','SDHPGr1m','SDHPGr1lo','SDT1f', 'SDT1sl', 'DTF'
    _1St_DailyPrices(), 
    _2StPr_HundredDaysBroadness(), # 'HBF'
    _2StPr_PriceHighestSince(), #'DHPbig'
    # 'DHPGr', 'DHPGrAvSh', 'DHPGrAvMi', 'DHPGrAvLo', 'DHPGrDiSl', 'DHPGrDiF'
    _2StPr_AvgOfDailyHighPriceGradient(), 
    
    # these 3 are in day_by_day_calcs:
    # 'DaysDVup', 'SDVBsl', 'SDVBm', 'SDVBf', 'SDVCsl', 'SDVCm', 'SDVCf1', 'SDVCf2', 'DVFDf', 'DVFf1', 'DVFf2', 'DVFm', 'DVFsl'
    _2StVols_SlowDailyVols(), 
    # 'DV', 'DVv'
    _2StVols_ModifiedDailyVol(),
    # 'SDLOCPsl','SDLOCPGrsl','DLOCup'
    _2StPr_SlowDailyLowerOCPriceGradient(),

    # 'SDLOCPBr','SDHP','SBr'
    _2StPr_SlowBroadness(),
    # 'bSDV','RbSDV'
    D_BackwardsSlowDailyVol(),
]

# globally holds the last alltable viewed in layout_at dash datatable
share_dict = []

AT_COLS = [
    'price',
    'volume',
    'TO',
    'DOP',
    'DLP',
    'DMP',
    'DHP',

    'AvMV',
    'MVm',
    'AvMVdec',
    'PSMV',

    'CV1',
    'RCV1',
    
    'SDHP1sh', # see _1St_DailyPrices.py
    'SDHP1m',
    'SDHP1lo', 
    'SDHPGr1sh',
    'SDHPGr1m',
    'SDHPGr1lo', 
    'SDT1f', # slow daily turnovers fast and slow
    'SDT1sl', 

    'DCP',
    'DHOCP',
    'DLOCP',
    'DHPbig',
    'DLPsmall',
    'ODV',
    'DT',
    'DT1',
    'SDT', # simplified daily turnover

    'DHPGr',
    'HBF',
    'RDHP', 'SDHP',
    'SRDHP1', 'SRDHP2', 'SRDHP3', 'SRDHP4', 'SRDHP5',
    'SRDHPGr1', 'SRDHPGr2', 'SRDHPGr3', 'SRDHPGr4', 'SRDHPGr5',
    'DHPGrAvSh', 'DHPGrAvMi', 'DHPGrAvLo',
    'DHPGrDiSl', 'DHPGrDiF',
    'DV', 
    'bSDV',
    'RbSDV',
    'DVv',
    'DaysDVup',
    'SDVBsl', 
    'SDVBm', 
    'SDVBf', 
    'SDVCsl', 
    'SDVCm', 
    'SDVCf1', 
    'SDVCf2',
    'DTF',
    'SDLOCPsl',
    'SDLOCPGrsl',
    'DLOCup',

    'SDLOCPBr',
    'SDHP',
    'SBr',
    
    # special Slow Minute Prices
    'SMPmsf', 
    'SMPmsm',
    'SMPmssl',
    # backwards Slow Minute Price
    'SMPmsb',

    # SMP Gradients, SMPGr: 
    'SMPGrmsf', 
    'SMPGrmsm', 
    'SMPGrmssl', 
    'SMPGrmsb',

    #Slow and Relative Minutely Volume
    'SMVms',
    'RMVms',

    #'SMPGrmsc0',
    'SMPGrmsbig',

    'MSmp',
    'MSmpv',
    'MSmv',

    #'DVFdf',
    'DVFf1',
    'DVFf2',
    'DVFf3',
    'DVFm',
    'DVFsl',

]

PRICE_AFFINITY = ['price', 'DHP', 'SDHP1sh', 'SDHP1m', 'SDHP1lo', 'DLP', 'DMP', 
                  'DCP', 'DHOCP', 'DLOCP', 'DOP', 'DHPbig', 'DLPsmall', 
                  'SDHP', 'MA-5', 'MA-20', 'MA-200','SDLOCPsl','DLOCup'
                  'SDHP','SMPmsf','SMPmsm','SMPmssl','SMPmsb', 
                  ]
RELATIVISED_AFFINITY = ['RDHP', 'SRDHP1',
                        'SRDHP2', 'SRDHP3', 'SRDHP4', 'SRDHP5', ] 
VOLUME_AFFINITY = ['volume', 'AvMV', 'PSMV', 'CV1', 'RCV1', 'ODV', 'DV', 'bSDV','DVv', 'SDVBsl', 'SDVBm',
                   'SDVBf', 'SDVCsl', 'SDVCm', 'SDVCf1', 'SDVCf2', 'SMVms', 'RMVms', 'MVm','AvMVdec',
                   ]
FACTOR_AFFINITY = ['DHPGr', 'HBF', 'SRDHPGr1', 'SRDHPGr2',
                   'SRDHPGr3', 'SRDHPGr4', 'SRDHPGr5',
                   'DHPGrAvSh', 'DHPGrAvMi', 'DHPGrAvLo',
                   'SDHPGr1sh','SDHPGr1m','SDHPGr1lo', 'SDLOCPGrsl','SDLOCPBr','SBr',
                   'RbSDV',    'SMPGrmsf', 'SMPGrmsm', 'SMPGrmssl', 'SMPGrmsb','SMPGrmsbig',
                   'MSmp', 'MSmpv', 'MSmv',
                   'DVFf1', 'DVFf2', 'DVFf3', 'DVFm', 'DVFsl', #'DVFdf', 
                   ]
#DAYCOUNTS_AFFINITY = [],
#DUMMY_AFFINITY = ['dummyRandom', 'dummyVolChangePerc', 'dummyTurnover']
TURNOVER_AFFINITY = ['TO', 'DT', 'DT1', 'SDT','SDT1f', 'SDT1sl','DTF',]
DISTANCE_AFFINITY = ['DHPGrDiSl', 'DHPGrDiF', ]
DAYS_AFFINITY = ['DaysDVup']


AT_COLS_AFFINITY = {
    'price': PRICE_AFFINITY,
    'volume': VOLUME_AFFINITY,
    'TO': TURNOVER_AFFINITY,
    'DHP': PRICE_AFFINITY,
    'AvMV': VOLUME_AFFINITY,
    'MVm': VOLUME_AFFINITY,
    'AvMVdec': VOLUME_AFFINITY,
    'PSMV': VOLUME_AFFINITY,
    'CV1': VOLUME_AFFINITY,
    'RCV1': VOLUME_AFFINITY,
    'SDHP1sh': PRICE_AFFINITY,
    'SDHP1m': PRICE_AFFINITY,
    'SDHP1lo': PRICE_AFFINITY,    
    'SDHPGr1sh': FACTOR_AFFINITY,
    'SDHPGr1m': FACTOR_AFFINITY,
    'SDHPGr1lo': FACTOR_AFFINITY,
    'DLP': PRICE_AFFINITY,
    'DMP': PRICE_AFFINITY,
    'DCP': PRICE_AFFINITY,
    'DHOCP': PRICE_AFFINITY,
    'DLOCP': PRICE_AFFINITY,
    'DOP': PRICE_AFFINITY,
    'DHPbig': PRICE_AFFINITY,
    'DLPsmall': PRICE_AFFINITY,
    'ODV': VOLUME_AFFINITY,
    'DT': TURNOVER_AFFINITY,
    'DT1': TURNOVER_AFFINITY,
    'SDT': TURNOVER_AFFINITY,
    'SDT1f': TURNOVER_AFFINITY,
    'SDT1sl': TURNOVER_AFFINITY,
    'DTF': TURNOVER_AFFINITY,
    'DHPGr': FACTOR_AFFINITY,
    'HBF': FACTOR_AFFINITY,
    'RDHP': RELATIVISED_AFFINITY,
    'SDHP': PRICE_AFFINITY,
    'SRDHP1': RELATIVISED_AFFINITY,
    'SRDHP2': RELATIVISED_AFFINITY,
    'SRDHP3': RELATIVISED_AFFINITY,
    'SRDHP4': RELATIVISED_AFFINITY,
    'SRDHP5': RELATIVISED_AFFINITY,
    'SRDHPGr1': FACTOR_AFFINITY,
    'SRDHPGr2': FACTOR_AFFINITY,
    'SRDHPGr3': FACTOR_AFFINITY,
    'SRDHPGr4': FACTOR_AFFINITY,
    'SRDHPGr5': FACTOR_AFFINITY,
    'DHPGrAvSh': FACTOR_AFFINITY,
    'DHPGrAvMi': FACTOR_AFFINITY,
    'DHPGrAvLo': FACTOR_AFFINITY,
    'DHPGrDiSl': DISTANCE_AFFINITY,
    'DHPGrDiF': DISTANCE_AFFINITY,
    'DV': VOLUME_AFFINITY,
    'bSDV': VOLUME_AFFINITY,
    'RbSDV': FACTOR_AFFINITY,
    'DVv': VOLUME_AFFINITY,
    'DaysDVup': DAYS_AFFINITY,
    'SDVBsl': VOLUME_AFFINITY,
    'SDVBm': VOLUME_AFFINITY,
    'SDVBf': VOLUME_AFFINITY,
    'SDVCsl': VOLUME_AFFINITY,
    'SDVCm': VOLUME_AFFINITY,
    'SDVCf1': VOLUME_AFFINITY,
    'SDVCf2': VOLUME_AFFINITY,
    # virtual cols from here on
    'MA-5': PRICE_AFFINITY,
    'MA-20': PRICE_AFFINITY,
    'MA-200': PRICE_AFFINITY,
    'SDLOCPsl': PRICE_AFFINITY,
    'SDLOCPGrsl': FACTOR_AFFINITY,
    'DLOCup': PRICE_AFFINITY,

    'SDLOCPBr': FACTOR_AFFINITY,
    'SDHP': PRICE_AFFINITY,
    'SBr': FACTOR_AFFINITY,

    'SMPmsf': PRICE_AFFINITY, 
    'SMPmsm': PRICE_AFFINITY,
    'SMPmssl': PRICE_AFFINITY,
    'SMPmsb': PRICE_AFFINITY, 
    'SMPGrmsf': FACTOR_AFFINITY, 
    'SMPGrmsm': FACTOR_AFFINITY, 
    'SMPGrmssl': FACTOR_AFFINITY, 
    'SMPGrmsb': FACTOR_AFFINITY,

    'SMVms': VOLUME_AFFINITY,
    'RMVms': VOLUME_AFFINITY,

    'SMPGrmsbig': FACTOR_AFFINITY,
    'MSmp': FACTOR_AFFINITY,
    'MSmpv': FACTOR_AFFINITY,
    'MSmv': FACTOR_AFFINITY,

    #'DVFdf': FACTOR_AFFINITY,
    'DVFf1': FACTOR_AFFINITY,
    'DVFf2': FACTOR_AFFINITY,
    'DVFf3': FACTOR_AFFINITY,
    'DVFm': FACTOR_AFFINITY,
    'DVFsl': FACTOR_AFFINITY,
}

AT_COLS_DIGITS = {
    'price': 3,
    'volume': 0,
    'TO': 0,
    'DHP': 3,
    'AvMV': 1,
    'MVm': 1,
    'AvMVdec': 2,
    'CV1': 1,
    'RCV1': 3,

    'SDHP1sh': 3, 
    'SDHP1m': 3, 
    'SDHP1lo': 3,
    'SDHPGr1sh': 4,
    'SDHPGr1m': 4,
    'SDHPGr1lo': 4,
    'SDT1f': 1, 
    'SDT1sl': 1,
    'DTF': 3,
    'DLP': 3,
    'DMP': 3,
    'DCP': 3,
    'DHOCP': 3,
    'DLOCP': 3,
    'DOP': 3,
    'DHPbig': 3,
    'DLPsmall': 3,
    'ODV': 0,
    'DT': 3,
    'DT1': 3,
    'SDT': 0,
    'DHPGr': 4,
    'HBF': 2,
    'RDHP': 3,
    'SDHP': 3,
    'SRDHP1': 3,
    'SRDHP2': 3,
    'SRDHP3': 3,
    'SRDHP4': 3,
    'SRDHP5': 3,
    'SRDHPGr1': 4,
    'SRDHPGr2': 4,
    'SRDHPGr3': 4,
    'SRDHPGr4': 4,
    'SRDHPGr5': 4,
    'DHPGrAvSh': 4,
    'DHPGrAvMi': 4,
    'DHPGrAvLo': 4,
    'DHPGrDiSl': 4,
    'DHPGrDiF': 4,
    'DV': 0,
    'bSDV': 3,
    'RbSDV': 3,
    'DVv': 0,
    'DaysDVup': 0,
    'SDVBsl': 3,
    'SDVBm': 3,
    'SDVBf': 3,
    'SDVCsl': 3,
    'SDVCm': 3,
    'SDVCf1': 3,
    'SDVCf2': 3,
    # virtual cols from here on
    'MA-5': 1,
    'MA-20': 1,
    'MA-200': 1,
    'SDLOCPsl': 3,
    'SDLOCPGrsl': 3,
    'DLOCup': 3,

    'SDLOCPBr':3,
    'SDHP':3,
    'SBr':3,

    'SMPmsf': 3, 
    'SMPmsm': 3,
    'SMPmssl': 3,
    'SMPmsb': 3, 
    'SMPGrmsf':4, 
    'SMPGrmsm':4, 
    'SMPGrmssl':4, 
    'SMPGrmsb':4,

    'SMVms': 3,
    'RMVms': 3,

    'SMPGrmsbig': 3,
    'MSmp': 3,
    'MSmpv': 3,
    'MSmv': 3,
    
    #'DVFdf': 3,
    'DVFf1': 3,
    'DVFf2': 3,
    'DVFf3': 3,
    'DVFm': 3,
    'DVFsl': 3,

}

# SHARES ALL-TABLES PER DASH
AT_COLS_DASH = [col for col in AT_COLS]
AT_COLS_DASH.insert(0, 'date_time')

# SHARES ALL-TABLES PER DASH INITIALLY CHECKED
AT_COLS_DASH_INITIAL = [
    'date_time',  # this col comes from the index being co-opted for Dash Datatable
    'price',
    'volume',
    'AvMV',
    'TO',
    'DHP',
    'ODV'
    'DT',
    'DT1',
]

# lookup structures
AT_INDICES = [i for i in range(len(AT_COLS))]
# CALCS column -> index lookup
AT_COL2INDEX = dict(zip(AT_COLS, AT_INDICES))

#AT_IMPORTED_COLUMNS = ['date','time','price','volume']

# those columns computed in minutes granularity, at the first stage
AT_MINUTELY_COMPUTEDS = M_DailyHighPrice().at_computeds + \
                        M_ParticularSumOfMV().at_computeds + \
                        M_SpecialSlowMinutePrices().at_computeds + \
                        M_RelativeMinutelyVolume().at_computeds
# these values computed by various successive calculations during stage 2
AT_DAILY_COMPUTEDS = ['HBF', 'DHPlast20hi', 'RDHP', 'SDHP', 
                       'SRDHP1', 'SRDHP2', 'SRDHP3', 'SRDHP4', 'SRDHP5', 
                       'SRDHPGr1', 'SRDHPGr2', 'SRDHPGr3', 'SRDHPGr4', 
                       'SRDHPGr5', 'DHPGr', 'DHPGrAvSh', 'DHPGrAvMi', 
                       'DHPGrAvLo', 'DHPGrDiSl', 'DHPGrDiF', 'ODV', 'DV','bSDV','RbSDV','CV1', 'RCV1',
                       'DVv', 'SDVBsl', 'SDVBm', 'SDVBf', 'SDVCsl', 'SDVCm', 
                       'SDVCf1', 'SDVCf2', 'DaysDVup', 'SDHP1sh', 'SDHP1m', 
                       'SDHP1lo','SDHPGr1sh', 'SDHPGr1m','SDHPGr1lo','SDT1f', 
                       'SDT1sl','DTF','SDLOCPsl','SDLOCPGrsl','DLOCup', 
                       'SDLOCPBr','SDHP','SBr',
                       'DVFf1', 'DVFf2', 'DVFf3', 'DVFm', 'DVFsl', #'DVFdf',
                       ]

# those values needed as daily values in stage 2, 
# but since known in stage1, grabbed from the last minute value of each day 
# see init_stage2_at_from_stage1 in at_ryun_all.py
AT_STAGE1_CARRY_FORWARDS = M_DailyHighPrice().at_computeds + \
                           M_ParticularSumOfMV().at_computeds + \
                           M_SpecialSlowMinutePrices().at_computeds

# consult this to know which columns pair with which stage
AT_STAGE_TO_COLS = {
    1: ['date_time', 'price', 'volume'] + AT_MINUTELY_COMPUTEDS,
    2: ['date_time', 'price', 'volume'] + AT_MINUTELY_COMPUTEDS + AT_DAILY_COMPUTEDS,
    3: [],
    4: [],
}

# filter syntax examples
date_time_filter_syntax = '''
    2020;
    2020-01;
    2020-01-01;
    2020-01-01 04:01;
    2020-01-01 04:01:10;
    datestartswith 2020;
    datestartswith 2020-01;
    datestartswith 2020-01-01;
    datestartswith 2020-01-01 04:01;
    datestartswith 2020-01-01 04:01:10;
    > 2020-01;
    > 2020-01-20;
    >= 2020-01;
    >= 2020-01-20;
    < 2020-01;
    < 2020-01-20;
    <= 2020-01;
    <= 2020-01-20;
'''

# explain whats in each column here
AT_COLS_TIPS = {
    'date_time': f'Datetime filtering examples: {date_time_filter_syntax}',
    'price': 'Price of share (imported)',
    'volume': 'Volume of trades (imported)',
    'TO': 'Turnover ie Price x Volume',
    'DHP': 'Daily Highest Price',
    'AvMV': 'Average Minute Volume',
    'MVm': 'Used for declining minute volumes',
    'AvMVdec': 'Average of the (declined) MVm values',
    'PSMV': 'Particular Sum of Minute Volume',
    'CV1': 'Cluster Volume of the Day',
    'RCV1': 'Relative Cluster Volume',
    'SDHP1sh': 'Slow Daily High Prices - short term', 
    'SDHP1m': 'Slow Daily High Prices - middle term', 
    'SDHP1lo': 'Slow Daily High Prices - long term',    
    'SDHPGr1sh': 'Slow Daily High Prices Gradient - short term',
    'SDHPGr1m': 'Slow Daily High Prices Gradient - middle term',
    'SDHPGr1lo': 'Slow Daily High Prices Gradient - long term',
    'DLP': 'Daily Lowest Price',
    'DMP': 'Daily middle Price',
    'DCP': 'Daily Closing Price',
    'DHPbig': 'Daily High Price of the last 100 days',
    'DLPsmall': 'smallest Daily Lowest Price of these last 100 days',
    'DHOCP': 'Daily High Open-Close Price: The first (Open) or the last (Close) price, whichever is higher',
    'DLOCP': 'Daily Low Open-Close Price: The first (Open) or the last (Close) price, whichever is lower',
    'DOP': 'Daily Open Price',
    'ODV': 'Total volume for the day (imported)',
    'DT': 'Total turnover for the day',
    'DT1': 'Daily Turnover for the 1. Stage on day D: DTD = ODVD * DHPD',
    'SDT': "Simplified turnover: closing price * day's volume",
    'SDT1f': "Slow Daily Turnover (fast)", 
    'SDT1sl': "Slow Daily Turnover (slow)",
    'DHPGr': 'Daily High Price Gradient',
    'HBF': 'Hundred Day Broadness figure',
    'SDHP': 'slow DHP',
    'RDHP': 'Relativised Daily High Price (10000*DHP/SDHP)',
    'SRDHP1': 'Slow RDHP1',
    'SRDHP2': 'Slow RDHP2',
    'SRDHP3': 'Slow RDHP3',
    'SRDHP4': 'Slow RDHP4',
    'SRDHP5': 'Slow RDHP5',
    'SRDHPGr1': 'Slow RDHP1 Gradient',
    'SRDHPGr2': 'Slow RDHP2 Gradient',
    'SRDHPGr3': 'Slow RDHP3 Gradient',
    'SRDHPGr4': 'Slow RDHP4 Gradient',
    'SRDHPGr5': 'Slow RDHP5 Gradient',
    'DHPGrAvSh': 'Daily High Price Gradient Short Term',
    'DHPGrAvMi': 'Daily High Price Gradient Middle Term',
    'DHPGrAvLo': 'Daily High Price Gradient Long Term',
    'DHPGrDiSl': 'Distance from Slow DailyHigh Price Gradient',
    'DHPGrDiF': 'Distance from Fast DailyHigh Price Gradient',
    'DV': 'modified Daily Volume',
    'bSDV': 'backwards Slow Daily Volume',
    'RbSDV': 'relation ...xxx',
    'DVv': 'Virtual Daily Volume',
    'DaysDVup': 'number of days in a row SDVBsl increased.',
    'SDVBsl': 'Slow Daily Vol Basic slow',
    'SDVBm': 'Slow Daily Vol Basic medium',
    'SDVBf': 'Slow Daily Vol Basic fast',
    'SDVCsl': 'Slow Daily Vol Compare slow',
    'SDVCm': 'Slow Daily Vol Compare medium',
    'SDVCf1': 'Slow Daily Vol Compare fast1',
    'SDVCf2': 'Slow Daily Vol Compare (very) fast2',
    'DTF': 'Daily Turnover Figure',
    'SDLOCPsl': 'Slow Daily Lower Open Close Price',
    'SDLOCPGrsl': 'Slow Daily Lower Open Close Price Gradient',
    'DLOCup': 'Number of days since when SDLOCPsa was < 1',

    'SDLOCPBr': 'Slow DLOCP Broadness',
    'SDHP': 'Slow DHP',
    'SBr': 'Slow Broadness',

    'SMPmsf': 'Slow Minute Price (fast)', 
    'SMPmsm': 'Slow Minute Price (medium)',
    'SMPmssl': 'Slow Minute Price (slow)',
    'SMPmsb': 'Slow Minute Price (backwards)', 
    'SMPGrmsf': 'Slow Minute Price (fast) Gradient', 
    'SMPGrmsm': 'Slow Minute Price (medium) Gradient', 
    'SMPGrmssl': 'Slow Minute Price (slow) Gradient', 
    'SMPGrmsb': 'Slow Minute Price (backwards) Gradient', 

    'SMVms': 'Slow Minutely Volume',
    'RMVms': 'Relative Minutely Volume',
    'SMPGrmsbig': "Slow Minutely Gradient biggest of 'SMPGrmsf', 'SMPGrmsm', 'SMPGrmssl'",
    'MSmp': 'Minutely Sight to view more the change of price',
    'MSmpv': 'Minutely Sight to view change of price and vol equally',
    'MSmv': 'Minutely Sight to view more the change of vol',

    #'DVFdf': '?',
    'DVFf1': 'Daily Volume Figure, a relation between (Slow) DV and slower SDV.  DVFf1 D = SDVCf1 D / SDVBf D-3',
    'DVFf2': 'Daily Volume Figure, a relation between (Slow) DV and slower SDV.  DVFf2 D = SDVCf2 D / SDVBf D-2',
    'DVFf3': 'Daily Volume Figure, a relation between (Slow) DV and slower SDV.  DVFf3 D = DVD / SDVBf D-1',
    'DVFm': 'Daily Volume Figure, a relation between (Slow) DV and slower SDV.  DVFm D = SDVCm D / SDVBm D-4',
    'DVFsl': 'Daily Volume Figure, a relation between (Slow) DV and slower SDV. DVFsl D = SDVCsl D / SDVBsl D',

}
