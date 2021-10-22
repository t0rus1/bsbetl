''' parameters for all-table calculations '''
from bsbetl.g_helpers import load_prepare_params
from json.decoder import JSONDecodeError
import logging
from os.path import exists
import json
from bsbetl import g
from bsbetl.simple_param import SimpleParam

''' 
    NOTE: DEFAULT PARAMETER VALUES ARE SET BELOW
    The user makes changes via the web app ONLY!
'''

# region Daily Average Price  (default DAP parameters)
atp_dap_min_rows_avg_price = SimpleParam(
    name= "atp_dap_min_rows_avg_price",
    calculation= "Daily Average Price",
    min= 5,
    max= 100,
    setting= 60,
    doc_ref= "2 Prices 210521.odt"
)
atp_dap_perc_rows_avg_price = SimpleParam(
    name= "atp_dap_perc_rows_avg_price",
    calculation= "Daily Average Price",
    min= 5,
    max= 100,
    setting= 25,
    doc_ref= "2 Prices 210521.odt"
)
atp_dap_rows_vol_wt_price = SimpleParam(
    name= "atp_dap_rows_vol_wt_price",
    calculation= "Daily Average Price",
    min= 5,
    max= 100,
    setting= 15,
    doc_ref= "2 Prices 210521.odt"
)
# endregion

# region Average of the Daily Average Price Gradient,  "DAPGrAv" and "DAPGrDi":
atp_YshDHPGrAv = SimpleParam(
    name= "atp_YshDHPGrAv",
    calculation= " Find the Average of the Daily High Price Gradient et al",
    min= 0.0,
    max= 1.0,
    setting= 0.7,
    doc_ref= "2 Prices 210521.odt"
)
atp_YmiDHPGrAv = SimpleParam(
    name= "atp_YmiDHPGrAv",
    calculation= " Find the Average of the Daily High Price Gradient et al",
    min= 0.0,
    max= 1.0,
    setting= 0.9,
    doc_ref= ""
)
atp_YloDHPGrAv = SimpleParam(
    name= "atp_YloDHPGrAv",
    calculation= " Find the Average of the Daily High Price Gradient et al",
    min= 0.0,
    max= 1.0,
    setting= 0.98,
    doc_ref= ""
)
# endregion

# region Slow Daily Vols:
# basic slow up
atp_YDVBslu = SimpleParam(
    name= "atp_YDVBslu",
    calculation= "Slow Daily Vol Basic Slow Y param up",
    min= 0.0,
    max= 1.0,
    setting= 0.001,
    doc_ref= "2 Vols 210524.odt"
)
atp_eSDVBslu = SimpleParam(
    name= "atp_eSDVBslu",
    calculation= "Slow Daily Vol Basic Slow exponent up",
    min= 0.0,
    max= 2.0,
    setting= 0.5,
    doc_ref= "2 Vols 210524.odt"
)
# basic slow down
atp_YDVBsld = SimpleParam(
    name= "atp_YDVBsld",
    calculation= "Slow Daily Vol Basic Slow Y param down",
    min= 0.0,
    max= 1.0,
    setting= 0.0005,
    doc_ref= "2 Vols 210524.odt"
)
atp_eSDVBsld = SimpleParam(
    name= "atp_eSDVBsld",
    calculation= "Slow Daily Vol Basic Slow exponent down",
    min= 0.0,
    max= 2.0,
    setting= 0.8,
    doc_ref= "2 Vols 210524.odt"
)

# basic medium up
atp_YDVBmu = SimpleParam(
    name= "atp_YDVBmu",
    calculation= "Slow Daily Vol Basic Medium Y param up",
    min= 0.0,
    max= 1.0,
    setting= 0.005,
    doc_ref= "2 Vols 210524.odt"
)
atp_eSDVBmu = SimpleParam(
    name= "atp_eSDVBmu",
    calculation= "Slow Daily Vol Basic Medium exponent up",
    min= 0.0,
    max= 2.0,
    setting= 0.8,
    doc_ref= "2 Vols 210524.odt"
)
# basic medium down
atp_YDVBmd = SimpleParam(
    name= "atp_YDVBmd",
    calculation= "Slow Daily Vol Basic Medium Y param down",
    min= 0.0,
    max= 1.0,
    setting= 0.007,
    doc_ref= "2 Vols 210524.odt"
)
atp_eSDVBmd = SimpleParam(
    name= "atp_eSDVBmd",
    calculation= "Slow Daily Vol Basic Medium exponent down",
    min= 0.0,
    max= 2.0,
    setting= 0.95,
    doc_ref= "2 Vols 210524.odt"
)


# basic fast up
atp_YDVBfu = SimpleParam(
    name= "atp_YDVBfu",
    calculation= "Slow Daily Vol Basic fast Y param up",
    min= 0.0,
    max= 1.0,
    setting= 0.015,
    doc_ref= "2 Vols 210524.odt"
)
atp_eSDVBfu = SimpleParam(
    name= "atp_eSDVBfu",
    calculation= "Slow Daily Vol Basic fast exponent up",
    min= 0.0,
    max= 2.0,
    setting= 0.9,
    doc_ref= "2 Vols 210524.odt"
)
# basic fast down
atp_YDVBfd = SimpleParam(
    name= "atp_YDVBfd",
    calculation= "Slow Daily Vol Basic fast Y param down",
    min= 0.0,
    max= 1.0,
    setting= 0.02,
    doc_ref= "2 Vols 210524.odt"
)
atp_eSDVBfd = SimpleParam(
    name= "atp_eSDVBfd",
    calculation= "Slow Daily Vol Basic fast exponent down",
    min= 0.0,
    max= 2.0,
    setting= 1,
    doc_ref= "2 Vols 210524.odt"
)

# compare slow up
atp_YDVCslu = SimpleParam(
    name= "atp_YDVCslu",
    calculation= "Slow Daily Vol Compare Slow Y param up",
    min= 0.0,
    max= 1.0,
    setting= 0.005,
    doc_ref= "2 Vols 210524.odt"
)
atp_eSDVCslu = SimpleParam(
    name= "atp_eSDVCslu",
    calculation= "Slow Daily Vol Compare Slow exponent up",
    min= 0.0,
    max= 2.0,
    setting= 0.6,
    doc_ref= "2 Vols 210524.odt"
)
# compare slow down
atp_YDVCsld = SimpleParam(
    name= "atp_YDVCsld",
    calculation= "Slow Daily Vol Compare Slow Y param down",
    min= 0.0,
    max= 1.0,
    setting= 0.006,
    doc_ref= "2 Vols 210524.odt"
)
atp_eSDVCsld = SimpleParam(
    name= "atp_eSDVCsld",
    calculation= "Slow Daily Vol Compare Slow exponent down",
    min= 0.0,
    max= 2.0,
    setting= 0.8,
    doc_ref= "2 Vols 210524.odt"
)

# compare medium up
atp_YDVCmu = SimpleParam(
    name= "atp_YDVCmu",
    calculation= "Slow Daily Vol Compare Medium Y param up",
    min= 0.0,
    max= 1.0,
    setting= 0.05,
    doc_ref= "2 Vols 210524.odt"
)
atp_eSDVCmu = SimpleParam(
    name= "atp_eSDVCmu",
    calculation= "Slow Daily Vol Compare Medium exponent up",
    min= 0.0,
    max= 2.0,
    setting= 0.8,
    doc_ref= "2 Vols 210524.odt"
)
# compare medium down
atp_YDVCmd = SimpleParam(
    name= "atp_YDVCmd",
    calculation= "Slow Daily Vol Compare Medium Y param down",
    min= 0.0,
    max= 1.0,
    setting= 0.07,
    doc_ref= "2 Vols 210524.odt"
)
atp_eSDVCmd = SimpleParam(
    name= "atp_eSDVCmd",
    calculation= "Slow Daily Vol Compare Medium exponent down",
    min= 0.0,
    max= 2.0,
    setting= 0.95,
    doc_ref= "2 Vols 210524.odt"
)

# compare fast1 up
atp_YDVCf1u = SimpleParam(
    name= "atp_YDVCf1u",
    calculation= "Slow Daily Vol Compare fast1 Y param up",
    min= 0.0,
    max= 1.0,
    setting= 0.2,
    doc_ref= "2 Vols 210524.odt"
)
atp_eSDVCf1u = SimpleParam(
    name= "atp_eSDVCf1u",
    calculation= "Slow Daily Vol Compare fast1 exponent up",
    min= 0.0,
    max= 2.0,
    setting= 0.95,
    doc_ref= "2 Vols 210524.odt"
)
# compare medium down
atp_YDVCf1d = SimpleParam(
    name= "atp_YDVCf1d",
    calculation= "Slow Daily Vol Compare fast1 Y param down",
    min= 0.0,
    max= 1.0,
    setting= 0.2,
    doc_ref= "2 Vols 210524.odt"
)
atp_eSDVCf1d = SimpleParam(
    name= "atp_eSDVCf1d",
    calculation= "Slow Daily Vol Compare fast1 exponent down",
    min= 0.0,
    max= 2.0,
    setting= 1,
    doc_ref= "2 Vols 210524.odt"
)

# compare fast2 up
atp_YDVCf2u = SimpleParam(
    name= "atp_YDVCf2u",
    calculation= "Slow Daily Vol Compare fast2 Y param up",
    min= 0.0,
    max= 1.0,
    setting= 0.5,
    doc_ref= "2 Vols 210524.odt"
)
atp_eSDVCf2u = SimpleParam(
    name= "atp_eSDVCf2u",
    calculation= "Slow Daily Vol Compare fast2 exponent up",
    min= 0.0,
    max= 2.0,
    setting= 0.96,
    doc_ref= "2 Vols 210524.odt"
)
# compare medium down
atp_YDVCf2d = SimpleParam(
    name= "atp_YDVCf2d",
    calculation= "Slow Daily Vol Compare fast2 Y param down",
    min= 0.0,
    max= 1.0,
    setting= 0.3,
    doc_ref= "2 Vols 210524.odt"
)
atp_eSDVCf2d = SimpleParam(
    name= "atp_eSDVCf2d",
    calculation= "Slow Daily Vol Compare fast2 exponent down",
    min= 0.0,
    max= 2.0,
    setting= 1,
    doc_ref= "2 Vols 210524.odt"
)
# endregion

# region Modified Daily Vol
atp_ModDV_Z = SimpleParam(
    name= "atp_ModDV_Z",
    calculation= "Modified Daily Vol Z param",
    min= 0.0,
    max= 100.0,
    setting= 10.0,
    doc_ref= "2 Vols 210524.odt"
)
# endregion

# region Slow Minute Prices
atp_SMP_Ymsf = SimpleParam(
    name= "atp_SMP_Ymsf",
    calculation= "Special Slow Minute Prices",
    min= 0.0,
    max= 0.1,
    setting= 0.1,
    doc_ref= ""
)
atp_SMP_Ymsm = SimpleParam(
    name= "atp_SMP_Ymsm",
    calculation= "Special Slow Minute Prices",
    min= 0.0,
    max= 0.1,
    setting= 0.02,
    doc_ref= ""
)
atp_SMP_Ymssl = SimpleParam(
    name= "atp_SMP_Ymssl",
    calculation= "Special Slow Minute Prices",
    min= 0.0,
    max= 0.1,
    setting= 0.003,
    doc_ref= ""
)
#endregion

#region Relative Minutely Volume
atp_RMV_TrRowsGr_threshold = SimpleParam(
    name= "atp_RMV_TrRowsGr_threshold",
    calculation= "Relative Minutely Volume",
    min= 1,
    max= 30,
    setting= 16,
    doc_ref= ""
)
atp_SMPGr_threshold = SimpleParam(
    name= "atp_SMPGr_threshold",
    calculation= "Relative Minutely Volume",
    min= 0.0,
    max= 2.0,
    setting= 1.01,
    doc_ref= ""
)

atp_eMSP_price = SimpleParam(
    name= "atp_eMSP_price",
    calculation= "Relative Minutely Volume",
    min= 0.0,
    max= 2.0,
    setting= 1.0,
    doc_ref= ""
)
atp_eMSP_pr_vol = SimpleParam(
    name= "atp_eMSP_pr_vol",
    calculation= "Relative Minutely Volume",
    min= 0.0,
    max= 2.0,
    setting= 0.8,
    doc_ref= ""
)
atp_eMSP_vol = SimpleParam(
    name= "atp_eMSP_vol",
    calculation= "Relative Minutely Volume",
    min= 0.0,
    max= 2.0,
    setting= 0.5,
    doc_ref= ""
)

atp_eMSV_price = SimpleParam(
    name= "atp_eMSV_price",
    calculation= "Relative Minutely Volume",
    min= 0.0,
    max= 2.0,
    setting= 1.0,
    doc_ref= ""
)
atp_eMSV_pr_vol = SimpleParam(
    name= "atp_eMSV_pr_vol",
    calculation= "Relative Minutely Volume",
    min= 0.0,
    max= 2.0,
    setting= 0.8,
    doc_ref= ""
)
atp_eMSV_vol = SimpleParam(
    name= "atp_eMSV_vol",
    calculation= "Relative Minutely Volume",
    min= 0.0,
    max= 2.0,
    setting= 0.5,
    doc_ref= ""
)

#endregion

''' 
    Place ALL the defaults in this list
    NOTE: this must be called !!
'''

default_at_params = [
    # atp_dap
    atp_dap_min_rows_avg_price,
    atp_dap_perc_rows_avg_price,
    atp_dap_rows_vol_wt_price,

    # atp_srdap
    # atp_srdap_y1RDAPu,
    # atp_srdap_y1RDAPd,
    # atp_srdap_e1RDAPu,
    # atp_srdap_e1RDAPd,

    # atp_srdap_y2RDAPu,
    # atp_srdap_y2RDAPd,
    # atp_srdap_e2RDAPu,
    # atp_srdap_e2RDAPd,

    # atp_srdap_y3RDAPu,
    # atp_srdap_y3RDAPd,
    # atp_srdap_e3RDAPu,
    # atp_srdap_e3RDAPd,

    # atp_srdap_y4RDAPu,
    # atp_srdap_y4RDAPd,
    # atp_srdap_e4RDAPu,
    # atp_srdap_e4RDAPd,

    # atp_srdap_y5RDAPu,
    # atp_srdap_y5RDAPd,
    # atp_srdap_e5RDAPu,
    # atp_srdap_e5RDAPd,

    atp_YshDHPGrAv,
    atp_YmiDHPGrAv,
    atp_YloDHPGrAv,

    # Slow Daily Vol
    atp_YDVBslu,
    atp_eSDVBslu,
    atp_YDVBslu,
    atp_eSDVBslu,
    # basic slow down
    atp_YDVBsld,
    atp_eSDVBsld,
    # basic medium up
    atp_YDVBmu,
    atp_eSDVBmu,
    # basic medium down
    atp_YDVBmd,
    atp_eSDVBmd,
    # basic fast up
    atp_YDVBfu,
    atp_eSDVBfu,
    # basic fast down
    atp_YDVBfd,
    atp_eSDVBfd,
    # compare slow up
    atp_YDVCslu,
    atp_eSDVCslu,
    # compare slow down
    atp_YDVCsld,
    atp_eSDVCsld,
    # compare medium up
    atp_YDVCmu,
    atp_eSDVCmu,
    # compare medium down
    atp_YDVCmd,
    atp_eSDVCmd,
    # compare fast1 up
    atp_YDVCf1u,
    atp_eSDVCf1u,
    # compare medium down
    atp_YDVCf1d,
    atp_eSDVCf1d,
    # compare fast2 up
    atp_YDVCf2u,
    atp_eSDVCf2u,
    # compare medium down
    atp_YDVCf2d,
    atp_eSDVCf2d,
    # modified daily vol
    atp_ModDV_Z,
    # slow minute prices
    atp_SMP_Ymsf,
    atp_SMP_Ymsm,
    atp_SMP_Ymssl,
    # Relative Minutely Volume Module MS 4: Calc the MSMS: 
    atp_RMV_TrRowsGr_threshold,
    atp_SMPGr_threshold,

    atp_RMV_TrRowsGr_threshold,
    atp_SMPGr_threshold,
    atp_eMSP_price,
    atp_eMSP_pr_vol,
    atp_eMSP_vol,
    atp_eMSV_price,
    atp_eMSV_pr_vol,
    atp_eMSV_vol,

]

''' 
    NOTE: here we load the alltable calc params from the at_params.json file, passing in the above defaults 
'''
#effectively a global
at_calc_params = load_prepare_params(g.AT_CALC_PARAMS_FQ, default_at_params)
