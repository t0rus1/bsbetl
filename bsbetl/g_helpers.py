""" helper functions for use *ONLY* by the globals file g.py """

from bsbetl import g
import json
from json.decoder import JSONDecodeError
from os import environ, listdir
import os
from os.path import exists
from shutil import copyfile


def get_config_settings(settings_fq: str, default_config_settings: dict):

    if exists(settings_fq):
        with open(settings_fq, 'r') as f:
            return json.load(f)

    # user needs to set this, but lets set a default
    return default_config_settings


def establish_container_path():
    ''' look in the environment for default container path and ensure it exists '''

    dcp = ''
    try:
        dcp = environ['BSB_CONTAINER_PATH']
        if not exists(dcp):
            drive = os.getcwd()[0]
            print(
                f'The folder {drive}:{dcp} was not found! Is this a new install? (If not, please investigate!)')
            print(
                f'In order to proceed with a new installation, please create the above {drive}:{dcp} folder after exiting, and then restart this app.')
            input('Press Enter to exit...')
            exit()
    except KeyError as ke:
        print()
        print('Warning: environment variable "BSB_CONTAINER_PATH" is not set')
        print('Under Windows Powershell set it as follows (for example):')
        print("$ $env:BSB_CONTAINER_PATH='\BsbEtl'")
        print()
        exit()

    return dcp

# def make_consumed_path(consumed_path):
#     ''' ensure the folder into which we toss processed TXT files exists '''

#     if not os.path.exists(consumed_path):
#         os.mkdir(consumed_path)


def make_required_path(required_path, container_path: str = '') -> str:
    ''' ensure the folder into which we require, exists '''

    if len(container_path) > 0:
        test_path = container_path + "\\" + required_path
    else:
        test_path = required_path

    if not os.path.exists(test_path):
        os.mkdir(test_path)

    return test_path


def list_sharelists(path: str) -> list:
    """ return a list of sharelist file names (excl '.shl' extension) """

    # this function has to be here in this 'globals' file to ensure we avoid circular references
    # this function is called in evaluation of the SHARELISTS list below
    return [f[:-4] for f in listdir(path) if f.endswith('.shl')]


def load_master_share_dict(master_share_dict_fq: str, base_dir, bsbetl_slug, xtras_folder, share_dictionary_name, sharelists_folder_fq, default_sharelist_name) -> dict:
    """ return the globally usable lookup dict of share_number to (share name,first_date,last_date) tuple """

    # sample_line:
    # '1+1 DRILLISCH AG O.N.          ,554550.ETR  ,DD.MM.YYYY  ,DD.MM.YYYY'
    # DD.MM.YYYY  is the date format in the BSB *.TXT trade data files

    master_dict = {}
    if not exists(master_share_dict_fq):
        print()
        response = input(
            f'Warning: The master share dictionary file ({master_share_dict_fq}) was not found.\n' +
            'It is assumed therefore that this is a new installation and so a presupplied one will be used.\n' +
            'It will be augmented as and when you do processing.\n\n'
            'Please acknowledge by pressing any key... ')
        print()
        # copy one from the extras folder
        master_ex_xtras_fq = base_dir + \
            f'{bsbetl_slug}\{xtras_folder}\\{share_dictionary_name}'
        try:
            copyfile(master_ex_xtras_fq, master_share_dict_fq)
        except IOError as e:
            print(
                f"Error. Unable to copy file {master_ex_xtras_fq} to {master_share_dict_fq}")
            exit(1)
        # while we're about it, grab the install supplied Default.shl as well
        defaultshl_ex_xtras_fq = base_dir + \
            f'{bsbetl_slug}\{xtras_folder}\{default_sharelist_name}'
        defaultshl_fq = sharelists_folder_fq + '\\' + default_sharelist_name
        try:
            copyfile(defaultshl_ex_xtras_fq, defaultshl_fq)
        except IOError as e:
            print(
                f"Error. Unable to copy file {defaultshl_ex_xtras_fq} to {defaultshl_fq}")
            exit(1)

    if exists(master_share_dict_fq):
        with open(master_share_dict_fq) as fp:
            line = fp.readline().strip()
            if line.startswith('share_name'):
                # skip header: share_name              ,number,first_date,last_date
                line = fp.readline().strip()
            else:
                print(
                    f'\nWarning:\n{master_share_dict_fq} file missing its header: "share_name,number,first_date,last_date"\n')
                line = None
            while line:
                fields = line.split(',')
                share_name = fields[0]
                share_num = fields[1]
                first_date = fields[2]
                last_date = fields[3]
                master_dict[share_num] = (share_name, first_date, last_date)
                line = fp.readline().strip()
    else:
        print()
        response = input(
            f'Warning: The master share dictionary file ({master_share_dict_fq}) was not found.\n' +
            'This file will be (re)created when next "process-1" command processes at least one new TXT file.\n\n' +
            'Please acknowledge by pressing any key: ')
        print()

    return master_dict


def load_prepare_params(calc_params_json_fq: str, def_calc_params_list: list) -> dict:
    ''' Load all calculation parameters from json serialized file into params dict 
        If no file found, a new params json file is written.
        Either way, calc_params_dict is returned
    '''

    calc_params_list = []
    create_new_params_file = False
    new_params = 0

    if exists(calc_params_json_fq):
        with open(calc_params_json_fq) as f:
            try:
                calc_params_list = json.load(f)
                # compare loaded params with default params list, looking for new parameters
                # if new ones found, add them and save to disk
                for reqd_parm in def_calc_params_list:
                    reqd_parm_found = False
                    # look thru current params. we must ensure the reqd parm is one of them
                    for cur_parm in calc_params_list:
                        reqd_parm_found = cur_parm['name'] == reqd_parm['name']
                        if reqd_parm_found:
                            break
                    if not reqd_parm_found:
                        calc_params_list.append(reqd_parm)
                        print(
                            f"{reqd_parm['name']} new calculation parameter found...")
                        new_params = new_params+1

            except JSONDecodeError as exc:
                print(
                    f'Malformed or non existent params.json file ({calc_params_json_fq})')
                create_new_params_file = True
    else:
        create_new_params_file = True

    params_list_to_use = calc_params_list

    if new_params > 0:
        # save newly updated calc_params_list to disk
        with open(calc_params_json_fq, 'w') as f:
            #f.write(json.dumps(calc_params_list.sort(key=lambda item: item.get('name')), indent=4))
            f.write(json.dumps(calc_params_list, indent=4))
        print(
            f'calc_params {calc_params_json_fq} updated. {new_params} new parameters added with default values\n\n')

    elif create_new_params_file:
        # no params file found or was malformed, set one up for going forward
        print(
            f'calc_params file NOT found or malformed, creating it using default values...')
        with open(calc_params_json_fq, 'w') as f:
            #f.write(json.dumps(def_calc_params_list.sort(key=lambda item: item.get('name')), indent=4))
            f.write(json.dumps(def_calc_params_list, indent=4))
        print(
            f'calc_params file {calc_params_json_fq} written with default values')
        params_list_to_use = def_calc_params_list

    calc_params_dict = {}
    for p in params_list_to_use:
        calc_params_dict[p['name']] = p

    return calc_params_dict


def load_prepare_1_conditions(_1_cond_json_fq: str, def_cond_list: list) -> dict:
    ''' Load all dp init conditions from json serialized file into dict 
        If no file found, a new json file is written.
        Either way, a dict is returned
    '''

    conditions_list = []
    create_new_conditions_file = False
    new_conditions = 0

    if exists(_1_cond_json_fq):
        with open(_1_cond_json_fq) as f:
            try:
                conditions_list = json.load(f)
                # compare loaded conditions with default list, looking for new conditions
                # if new ones found, add them and save to disk
                for reqd_condition in def_cond_list:
                    reqd_cond_found = False
                    # look thru current conditions. we must ensure the reqd cond is one of them
                    for cur_cond in conditions_list:
                        reqd_cond_found = cur_cond['name'] == reqd_condition['name']
                        if reqd_cond_found:
                            break
                    if not reqd_cond_found:
                        conditions_list.append(reqd_condition)
                        print(
                            f"{reqd_condition['name']} new dp init condition found...")
                        new_conditions = new_conditions+1

            except JSONDecodeError as exc:
                print(
                    f'Malformed or non existent conditions.json file ({_1_cond_json_fq})')
                create_new_conditions_file = True
    else:
        create_new_conditions_file = True

    conditions_list_to_use = conditions_list

    if new_conditions > 0:
        # save newly updated conditions list to disk
        with open(_1_cond_json_fq, 'w') as f:
            # here we assume 'name' is item[0]
            f.write(json.dumps(conditions_list, indent=4)) #.sort(key=lambda item: item.get('name')), indent=4))
        print(
            f'_1_conditions {_1_cond_json_fq} updated. {new_conditions} new conditions added with default values\n\n')

    elif create_new_conditions_file:
        # no params file found or was malformed, set one up for going forward
        print(
            f'_1_conditions file NOT found or malformed, creating it using default values...')
        with open(_1_cond_json_fq, 'w') as f:
            # here we assume 'name' is item[0]
            f.write(json.dumps(def_cond_list, indent=4)) #.sort(key=lambda item: item.get('name')), indent=4))
        print(
            f'_1_conditions file {_1_cond_json_fq} written with default values')
        conditions_list_to_use = def_cond_list

    dp_init_conditions_dict = {}
    for c in conditions_list_to_use:
        dp_init_conditions_dict[c['name']] = c

    #print(dp_init_conditions_dict)
    return dp_init_conditions_dict

def sync_1_conditions_audit_structure(_1St_conditions):
    ''' the 'audit_results' structure in the runtime config is used 
        to provide column heading tips to the results dataframes.
        It is ONLY used for this
        In case the conditions (eg settings, minima, maxima etc) were altered 
        this routine bring this structure into line
    '''    

    audit_dict = {}
    audit_dict['Con_a'] = _1St_conditions['Con_a']

    audit_dict = {}
    audit_dict['Con_b'] = _1St_conditions['Con_b']

    audit_dict = {}
    audit_dict['Con_c'] = _1St_conditions['Con_c']

    audit_dict = {}
    audit_dict['Con_d'] = _1St_conditions['Con_d']




def load_prepare_2StPr_conditions(cond_json_fq: str, def_cond_list: list) -> dict:
    ''' Load all conditions from json serialized file into dict 
        If no file found, a new json file is written.
        Either way, a dict is returned
    '''

    conditions_list = []
    create_new_conditions_file = False
    new_conditions = 0

    if exists(cond_json_fq):
        with open(cond_json_fq) as f:
            try:
                conditions_list = json.load(f)
                # compare loaded conditions with default list, looking for new conditions
                # if new ones found, add them and save to disk
                for reqd_condition in def_cond_list:
                    reqd_cond_found = False
                    # look thru current conditions. we must ensure the reqd cond is one of them
                    for cur_cond in conditions_list:
                        reqd_cond_found = cur_cond['name'] == reqd_condition['name']
                        if reqd_cond_found:
                            break
                    if not reqd_cond_found:
                        conditions_list.append(reqd_condition)
                        print(
                            f"{reqd_condition['name']} new dp init condition found...")
                        new_conditions = new_conditions+1

            except JSONDecodeError as exc:
                print(
                    f'Malformed or non existent conditions.json file ({cond_json_fq})')
                create_new_conditions_file = True
    else:
        create_new_conditions_file = True

    conditions_list_to_use = conditions_list

    if new_conditions > 0:
        # save newly updated conditions list to disk
        with open(cond_json_fq, 'w') as f:
            # here we assume 'name' is item[0]
            f.write(json.dumps(conditions_list, indent=4)) #.sort(key=lambda item: item.get('name')), indent=4))
        print(
            f'_2StPr_conditions {cond_json_fq} updated. {new_conditions} new conditions added with default values\n\n')

    elif create_new_conditions_file:
        # no params file found or was malformed, set one up for going forward
        print(
            f'_2StPr_conditions file NOT found or malformed, creating it using default values...')
        with open(cond_json_fq, 'w') as f:
            # here we assume 'name' is item[0]
            f.write(json.dumps(def_cond_list, indent=4)) #.sort(key=lambda item: item.get('name')), indent=4))
        print(
            f'_2StPr_conditions file {cond_json_fq} written with default values')
        conditions_list_to_use = def_cond_list

    conditions_dict = {}
    for c in conditions_list_to_use:
        conditions_dict[c['name']] = c

    return conditions_dict

def sync_2StPr_audit_structure(_2StPr_conditions):
    ''' the 'audit_results' structure in the runtime config is used 
        to provide column heading tips to the results dataframes.
        It is ONLY used for this
        In case the conditions (eg settings, minima, maxima etc) were altered 
        this routine bring this structure into line
    '''    

    audit_dict = {}
    audit_dict['Con_a1'] = _2StPr_conditions['Con_a1']
    g.CONFIG_RUNTIME['audit_structure_2StPr']['a1'] = audit_dict

    audit_dict = {}
    audit_dict['Con_a2'] = _2StPr_conditions['Con_a2']
    g.CONFIG_RUNTIME['audit_structure_2StPr']['a2'] = audit_dict

    audit_dict = {}
    audit_dict['Con_a3'] = _2StPr_conditions['Con_a3']
    g.CONFIG_RUNTIME['audit_structure_2StPr']['a3'] = audit_dict

    audit_dict = {}
    audit_dict['Con_a1'] = _2StPr_conditions['Con_a1']
    g.CONFIG_RUNTIME['audit_structure_2StPr']['a1'] = audit_dict

    audit_dict = {}
    con_keys = ['Con_b1','Con_b2','Con_b3','Con_b4','Con_b5']
    for con_key in con_keys:
        audit_dict[con_key] = _2StPr_conditions[con_key]  
    g.CONFIG_RUNTIME['audit_structure_2StPr']['b'] = audit_dict

    audit_dict = {}
    con_keys = ['Con_c1','Con_c2','Con_c3','Con_c4','Con_c5']
    for con_key in con_keys:
        audit_dict[con_key] = _2StPr_conditions[con_key]  
    g.CONFIG_RUNTIME['audit_structure_2StPr']['c'] = audit_dict

    audit_dict = {}
    con_keys = ['Con_d1','Con_d2','Con_d3','Con_d4','Con_d5']
    for con_key in con_keys:
        audit_dict[con_key] = _2StPr_conditions[con_key]
    g.CONFIG_RUNTIME['audit_structure_2StPr']['d'] = audit_dict

    audit_dict = {}
    con_keys = ['Con_e1','Con_e2','Con_e3','Con_e4','Con_e5']
    for con_key in con_keys:
        audit_dict[con_key] = _2StPr_conditions[con_key]
    g.CONFIG_RUNTIME['audit_structure_2StPr']['e'] = audit_dict

    audit_dict = {}
    audit_dict['Con_f'] = _2StPr_conditions['Con_f']
    g.CONFIG_RUNTIME['audit_structure_2StPr']['f'] = audit_dict

    audit_dict = {}
    audit_dict['Con_g'] = _2StPr_conditions['Con_g']
    g.CONFIG_RUNTIME['audit_structure_2StPr']['g'] = audit_dict

    audit_dict = {}
    audit_dict['Con_h'] = _2StPr_conditions['Con_h']
    g.CONFIG_RUNTIME['audit_structure_2StPr']['h'] = audit_dict

    audit_dict = {}
    audit_dict['Con_i'] = _2StPr_conditions['Con_i']
    g.CONFIG_RUNTIME['audit_structure_2StPr']['i'] = audit_dict

    audit_dict = {}
    audit_dict['Con_j'] = _2StPr_conditions['Con_j']
    g.CONFIG_RUNTIME['audit_structure_2StPr']['j'] = audit_dict


def load_prepare_2StVols_conditions(cond_json_fq: str, def_cond_list: list) -> dict:
    ''' Load all conditions from json serialized file into dict 
        If no file found, a new json file is written.
        Either way, a dict is returned
    '''

    conditions_list = []
    create_new_conditions_file = False
    new_conditions = 0

    if exists(cond_json_fq):
        with open(cond_json_fq) as f:
            try:
                conditions_list = json.load(f)
                # compare loaded conditions with default list, looking for new conditions
                # if new ones found, add them and save to disk
                for reqd_condition in def_cond_list:
                    reqd_cond_found = False
                    # look thru current conditions. we must ensure the reqd cond is one of them
                    for cur_cond in conditions_list:
                        reqd_cond_found = cur_cond['name'] == reqd_condition['name']
                        if reqd_cond_found:
                            break
                    if not reqd_cond_found:
                        conditions_list.append(reqd_condition)
                        print(
                            f"{reqd_condition['name']} new condition found...")
                        new_conditions = new_conditions+1

            except JSONDecodeError as exc:
                print(
                    f'Malformed or non existent conditions.json file ({cond_json_fq})')
                create_new_conditions_file = True
    else:
        create_new_conditions_file = True

    conditions_list_to_use = conditions_list

    if new_conditions > 0:
        # save newly updated conditions list to disk
        with open(cond_json_fq, 'w') as f:
            # here we assume 'name' is item[0]
            f.write(json.dumps(conditions_list, indent=4)) #.sort(key=lambda item: item.get('name')), indent=4))
        print(
            f'_2StVols_conditions {cond_json_fq} updated. {new_conditions} new conditions added with default values\n\n')

    elif create_new_conditions_file:
        # no params file found or was malformed, set one up for going forward
        print(
            f'_2StVols_conditions file NOT found or malformed, creating it using default values...')
        with open(cond_json_fq, 'w') as f:
            # here we assume 'name' is item[0]
            f.write(json.dumps(def_cond_list, indent=4)) #.sort(key=lambda item: item.get('name')), indent=4))
        print(
            f'_2StVols_conditions file {cond_json_fq} written with default values')
        conditions_list_to_use = def_cond_list

    conditions_dict = {}
    for c in conditions_list_to_use:
        conditions_dict[c['name']] = c

    return conditions_dict

def sync_2stVols_conditions_audit_structure(_2StVols_conditions):
    ''' the 'audit_results' structure in the runtime config is used 
        to provide column heading tips to the results dataframes.
        It is ONLY used for this
        In case the conditions (eg settings, minima, maxima etc) were altered 
        this routine bring this structure into line
    '''    

    audit_dict = {}
    audit_dict['Con_a1'] = _2StVols_conditions['Con_a1']
    g.CONFIG_RUNTIME['audit_structure_2StVols']['a1'] = audit_dict

    audit_dict = {}
    audit_dict['Con_a2'] = _2StVols_conditions['Con_a2']
    g.CONFIG_RUNTIME['audit_structure_2StVols']['a2'] = audit_dict

    audit_dict = {}
    audit_dict['Con_b'] = _2StVols_conditions['Con_b']
    g.CONFIG_RUNTIME['audit_structure_2StVols']['b'] = audit_dict

    audit_dict = {}
    audit_dict['Con_c'] = _2StVols_conditions['Con_c']
    g.CONFIG_RUNTIME['audit_structure_2StVols']['c'] = audit_dict

    audit_dict = {}
    audit_dict['Con_d'] = _2StVols_conditions['Con_d']
    g.CONFIG_RUNTIME['audit_structure_2StVols']['d'] = audit_dict

    audit_dict = {}
    audit_dict['Con_e'] = _2StVols_conditions['Con_e']
    g.CONFIG_RUNTIME['audit_structure_2StVols']['e'] = audit_dict

    audit_dict = {}
    audit_dict['Con_f'] = _2StVols_conditions['Con_f']
    g.CONFIG_RUNTIME['audit_structure_2StVols']['f'] = audit_dict


def load_prepare_3jP_conditions(cond_json_fq: str, def_cond_list: list) -> dict:
    ''' Load all conditions from json serialized file into dict 
        If no file found, a new json file is written.
        Either way, a dict is returned
    '''

    conditions_list = []
    create_new_conditions_file = False
    new_conditions = 0

    if exists(cond_json_fq):
        with open(cond_json_fq) as f:
            try:
                conditions_list = json.load(f)
                # compare loaded conditions with default list, looking for new conditions
                # if new ones found, add them and save to disk
                for reqd_condition in def_cond_list:
                    reqd_cond_found = False
                    # look thru current conditions. we must ensure the reqd cond is one of them
                    for cur_cond in conditions_list:
                        reqd_cond_found = cur_cond['name'] == reqd_condition['name']
                        if reqd_cond_found:
                            break
                    if not reqd_cond_found:
                        conditions_list.append(reqd_condition)
                        print(
                            f"{reqd_condition['name']} new dp init condition found...")
                        new_conditions = new_conditions+1

            except JSONDecodeError as exc:
                print(
                    f'Malformed or non existent conditions.json file ({cond_json_fq})')
                create_new_conditions_file = True
    else:
        create_new_conditions_file = True

    conditions_list_to_use = conditions_list

    if new_conditions > 0:
        # save newly updated conditions list to disk
        with open(cond_json_fq, 'w') as f:
            # here we assume 'name' is item[0]
            f.write(json.dumps(conditions_list, indent=4)) #.sort(key=lambda item: item.get('name')), indent=4))
        print(
            f'_2StPr_conditions {cond_json_fq} updated. {new_conditions} new conditions added with default values\n\n')

    elif create_new_conditions_file:
        # no params file found or was malformed, set one up for going forward
        print(
            f'_3jP_conditions file NOT found or malformed, creating it using default values...')
        with open(cond_json_fq, 'w') as f:
            # here we assume 'name' is item[0]
            f.write(json.dumps(def_cond_list, indent=4)) #.sort(key=lambda item: item.get('name')), indent=4))
        print(
            f'_3jP_conditions file {cond_json_fq} written with default values')
        conditions_list_to_use = def_cond_list

    conditions_dict = {}
    for c in conditions_list_to_use:
        conditions_dict[c['name']] = c

    return conditions_dict
