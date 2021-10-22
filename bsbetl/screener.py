import pandas as pd
from bsbetl.helpers import get_latest_prices_from_last_gen_csv_by_day_run, get_latest_prices_from_share_by_day_folders
import io
import os
from datetime import date

from genericpath import exists

from bsbetl import g
from bsbetl.app_helpers import save_dict_values_as_txt


def create_bsb_lookup_starter(starter_name_fq: str):
    ''' creates bsb code lookup file starter using the master share dictionary '''

    with open(g.MASTER_SHARE_DICT_FQ, 'r') as masterf:
        master_entries = masterf.readlines()
        with open(starter_name_fq, 'w') as codelookupf:
            lookup_header = g.BSB_CODE_LOOKUP_HEADER
            codelookupf.write(f'{lookup_header}\n')
            for master_entry in master_entries:
                master_fields = master_entry.split(',')
                if master_fields[1].endswith(g.BOURSES_LIST[0]):
                    # we need only have regard for one bourse, since BSB have the same share number for each share
                    # backtrack = len(g.BOURSES_LIST[0])+1  # ETR,FFM plus '.'
                    #lookup_entry = f'{master_fields[0].rstrip()},{master_fields[1][0:-backtrack]},,\n'
                    lookup_entry = f'{master_fields[0].rstrip()},{master_fields[1]},,\n'
                    codelookupf.write(lookup_entry)


def refresh_bsb_lookup(bsb_lookup_name_fq: str) -> str:
    ''' refresh bsb code lookup file using the latest master share dictionary 
    NOTE the bsb_price column is not present in the physical csv file
    '''

    results_msg = 'refresh_bsb_lookup done. '
    lookup_codes_to_delete = []
    lookup_codes_to_add = []

    with open(g.MASTER_SHARE_DICT_FQ, 'r') as masterf:
        # open MasterShareDictionary
        master_entries = masterf.readlines()
        with open(bsb_lookup_name_fq, 'r') as bsb_lookupf:
            # open codelookup file
            bsb_lookup_entries = bsb_lookupf.readlines()
            # build a dict to hold the codelookup, keyed on bsb_number
            lookup = {}
            for lookup_entry in bsb_lookup_entries[1:]:  # skip header
                # bsb_name,bsb_number,investing.name,investing.symbol
                lookup_fields = lookup_entry.split(',')
                lookup[lookup_fields[1]] = lookup_entry
            # build a dict to hold master share dictionary, keyed on number
            master = {}
            for master_entry in master_entries[1:]:  # skip header
                #share_name                     ,number,first_date,last_date
                master_fields = master_entry.split(',')
                if master_fields[1].endswith(g.BOURSES_LIST[0]):  # ETR only
                    # [0:6] # stripped of .ETR
                    master_share_num = master_fields[1]
                    master[master_share_num] = master_entry

            # now that we have two dictionaries we can proceed to update the lookup from the master

            # firstly, remove all shares in the lookup not present in the master
            for lookup_code in lookup.keys():
                if not lookup_code in master:
                    lookup_codes_to_delete.append(lookup_code)

            # add new codes found in master but not in lookup
            for master_share_num in master.keys():
                if not master_share_num in lookup.keys():
                    lookup_codes_to_add.append(master_share_num)

            # perform the operations. delete
            for lookup_code in lookup_codes_to_delete:
                lookup.pop(lookup_code)
            # and add
            for new_share_num in lookup_codes_to_add:
                master_fields = master[new_share_num].split(',')
                # bsb_name,bsb_number,investing.name,investing.symbol
                lookup[new_share_num] = f'{master_fields[0]},{new_share_num},added {date.today().strftime("%y_%m_%d")}\n'

    if len(lookup_codes_to_delete) > 0 or len(lookup_codes_to_add) > 0:
        # save updated lookup to disk
        lookup_header = g.BSB_CODE_LOOKUP_HEADER
        save_dict_values_as_txt(
            lookup, bsb_lookup_name_fq, lookup_header) #, with_backup=True)
        results_msg = results_msg + \
            f"{len(lookup_codes_to_delete)} bsb mapping codes deleted, {len(lookup_codes_to_add)} added. Save over the file '{g.BSB_CODE_LOOKUP_NAME}' to commit, then refresh the page to confirm."
    else:
        results_msg = results_msg + \
            f"{len(lookup_codes_to_delete)} bsb mapping codes deleted, {len(lookup_codes_to_add)} added"

    return results_msg

# NOTE keep for possible re-use


def temp_import_share_symbols(bsb_lookup_name_fq: str, msl_import_fq) -> str:
    ''' NOTE once off hack
    add investing.com symbol info from a txt file hacked from the old Shw system's Investing.com.msl file
    '''

    results_msg = 'symbols updated. '
    updates = 0
    with open(msl_import_fq, 'r') as mslf:
        #
        msl_entries = mslf.readlines()
        with open(bsb_lookup_name_fq, 'r') as bsb_lookupf:
            # open codelookup file
            bsb_lookup_entries = bsb_lookupf.readlines()
            # build a dict to hold the codelookup, keyed on bsb_number
            lookup = {}
            for lookup_entry in bsb_lookup_entries[1:]:  # skip header
                # bsb_name,bsb_number,investing_name,investing_symbol
                # eg case when no investing_name or _symbol is known:
                # CARL ZEISS MEDITEC AG,531370.ETR,,
                lookup_fields = lookup_entry.split(',')
                lookup[lookup_fields[1]] = lookup_entry.strip()
            # build a dict to hold symbols, keyed on number
            mslcodes = {}
            for msl_entry in msl_entries:
                msl_entry = msl_entry.rstrip()
                msl_fields = msl_entry.split(',')
                # Apple,Xetra,865985,AAPL
                if len(msl_fields) == 4 and len(msl_fields[2]) == 6:
                    bsb_share_number = msl_fields[2] + '.ETR'
                    if bsb_share_number in lookup:
                        lookup_entry = lookup[bsb_share_number]
                        lookup_fields = lookup_entry.split(',')
                        # update the entry by filling in the  investing.com_name,investing.com_symbol fields
                        # bsb_name,bsb_number,investing_name,investing_symbol
                        lookup[bsb_share_number] = f'{lookup_fields[0]},{bsb_share_number},{msl_fields[0]},{msl_fields[3].rstrip()}'
                        updates = updates+1

    if updates > 0:
        # save updated lookup to disk
        lookup_header = 'bsb_name,bsb_number,investing_name,investing_symbol'
        save_dict_values_as_txt(
            lookup, bsb_lookup_name_fq, lookup_header)

    results_msg = results_msg + f' ({updates})'
    return results_msg


def get_symbols_help():

    help = ""  # "Symbols lookup list\n-------------------\n"
    symbols_help_fq = g.DESIGNATED_SCREENER_FQ
    if exists(symbols_help_fq):
        with open(symbols_help_fq, 'r') as symbolf:
            # open codelookup file
            all_symbols = symbolf.readlines()

        # strip out double quotes, reduce number of fields
        for share_line in all_symbols:
            share_line = share_line.replace('"', '')
            if ',Symbol' in share_line:
                continue  # skip page headers
            # we only need the first 3 fields
            content_pieces = share_line.split(',')[0:3]
            content = ','.join(content_pieces)
            help = help + f'{content}\n'

    return help


def get_bsb_number_help():

    # build dataframe to hold latest prices
    #df_latest = get_latest_prices_from_share_by_day_folders()
    #print(df_latest.loc['A11QW6.ETR', 'bsb_price'])

    # NOTE new way, using the LastPrices.json file which is updated every process-2 run
    g.latest_share_prices = get_latest_prices_from_last_gen_csv_by_day_run()
    df_latest = pd.DataFrame.from_dict(
        g.latest_share_prices, orient='index', columns=['bsb_price'])
    #df_lookup['bsb_price'] = df_latest['bsb_price']

    help_header = "{0} unmapped BSB shares\n============================\n"
    help_content = ""
    num_unmappeds = 0
    help_fq = g.BSB_CODE_LOOKUP_NAME_FQ
    if exists(help_fq):
        with open(help_fq, 'r') as symbolf:
            # open codelookup file
            all_symbols = symbolf.readlines()

        # strip out double quotes, reduce number of fields
        # bsb_name,bsb_number,investing_name,investing_symbol
        for share_line in all_symbols:
            if ',bsb_number' in share_line or len(share_line) < 5:
                continue  # skip page headers
            # we drop investing_name (since its already in our left hand table)
            fields = share_line.split(',')
            # only want bsb shares whose investing_symbol is blank
            if len(fields[3]) <= 1:  # \n
                num_unmappeds = num_unmappeds+1
                bsb_number_incl_bourse = fields[1]
                bsb_number_excl_bourse = bsb_number_incl_bourse[:-4]
                try:
                    latest_bsb_price = df_latest.loc[bsb_number_incl_bourse, 'bsb_price']
                    help_line = f"{fields[0]},{bsb_number_excl_bourse},{latest_bsb_price}\n"
                except KeyError:
                    help_line = f"{fields[0]},{bsb_number_excl_bourse},?\n"
                help_content = help_content + help_line

    return help_header.format(num_unmappeds)+help_content


def update_bsb_code_lookup_from_screener(combined_screener_data: list) -> int:
    ''' 
    Try to locate in the BsbCodeLookup.csv file every bsb_number in the combined screener datatable
    and ensure that its 4th (last) field is given the same Symbol value as found in the screener
    Here is what combined_screener_data looks like - a list of dicts: 
    [{'Name': 'AstraZeneca', 'Symbol': 'AZN', 'Last': '86.28', 'Chg. %': '-0.48%', 'Market Cap': '113.12B', 'Vol.': '49.80K', 'bsb_number': '886455'}, 
     {'Name': 'Morgan Stanley', 'Symbol': 'MWD', 'Last': '61.74', 'Chg. %': '-1.55%', 'Market Cap': '111.83B', 'Vol.': '2.05K', 'bsb_number': '885836'}
     ...
     ...
    ]
    '''

    lookup_updates = 0
    bsb_lookup_fq = g.BSB_CODE_LOOKUP_NAME_FQ
    if exists(bsb_lookup_fq):
        lookup = {}
        with open(bsb_lookup_fq, 'r') as lookupf:
            # open codelookup file
            bsb_shares = lookupf.readlines()[1:]  # skip header
            # transfer to a dict
            for share_entry in bsb_shares:
                # bsb_name,bsb_number,investing_name,investing_symbol
                # 1+1 DRILLISCH AG O.N.,554550.ETR,,
                share_entry = share_entry.rstrip()  # clean off trailing \n
                fields = share_entry.split(',')
                lookup[fields[1]] = share_entry

        # iterate thru combined_screener_data
        # and check EVERY bsb_number
        for screener_entry in combined_screener_data:
            # print(screener_entry)
            if isinstance(screener_entry['bsb_number'], str) and len(screener_entry['bsb_number']) == 6:
                lookup_key = screener_entry['bsb_number'] + '.ETR'
                if lookup_key in lookup:
                    # extract lookup entry and re-build it.
                    # eg here is an entry (DRILLISCH) which has no investing_name or symbol
                    # bsb_name,bsb_number,investing_name,investing_symbol
                    # 1+1 DRILLISCH AG O.N.,554550.ETR,,
                    fields = lookup[lookup_key].split(',')
                    # simply re-assign third and fourth fields
                    fields[2] = screener_entry['Name']
                    fields[3] = screener_entry['Symbol']
                    # and place back in the lookup dict
                    updated_lookup = ','.join(fields)
                    lookup[lookup_key] = updated_lookup
                    lookup_updates = lookup_updates+1
        # finally save the updated lookup back to disk file
        if lookup_updates > 0:
            save_dict_values_as_txt(
                lookup, bsb_lookup_fq, g.BSB_CODE_LOOKUP_HEADER)

    return lookup_updates


def delete_screener_constituents(csv_options) -> int:

    num_removed = 0
    if isinstance(csv_options, list):
        for csv in csv_options:
            csv_fq = g.SCREENER_RESULTS_PATH + "\\" + csv['value']
            if exists(csv_fq):
                os.remove(csv_fq)
                num_removed = num_removed+1

    return f'{num_removed} csv files deleted...'


def create_sharelist_from_screener_df(df_screener: list, sharelist_name_fq: str):

    header = g.SHARELIST_HEADER

    # df_screener is a list of dict
    #
    # [{'Name': 'AstraZeneca', 'Symbol': 'AZN', 'Last': '86.28', 'Chg. %': '-0.48%', 'Market Cap': '113.12B', 'Vol.': '49.80K', 'bsb_number': '886455'},
    # {'Name': 'Morgan Stanley', 'Symbol': 'MWD', 'Last': '61.74', 'Chg. %': '-1.55%', 'Market Cap': '111.83B', 'Vol.': '2.05K', 'bsb_number': '885836'}]

    # take care of backup
    # prior_fq = f'{sharelist_name_fq}.bak'
    # if exists(prior_fq):
    #     os.remove(prior_fq)
    # os.rename(sharelist_name_fq, prior_fq)

    # write out new sharelist
    with io.open(sharelist_name_fq, 'w', encoding='utf-8') as shlf:
        shlf.write(f'{header}\n')  # share_name                     number
        for entry in sorted(df_screener, key=lambda i: i['Name']):
            sh_name = entry['Name']
            # truncate if name longer than 31 chars
            if len(sh_name) > 31:
                sh_name = sh_name[0:31]
            bsb_num = entry['bsb_number']
            if bsb_num is None:
                bsb_num = 'None'
            elif len(bsb_num) > 6:
                bsb_num = bsb_num[0:6]

            out_line = sh_name.ljust(31) + f"{bsb_num.rjust(6,'_')}.ETR"
            shlf.write(f'{out_line}\n')
