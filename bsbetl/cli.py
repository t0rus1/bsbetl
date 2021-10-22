import inspect
import logging
import sys
import winsound
from datetime import datetime

import click

from bsbetl import bsbetl_gui, functions, g, helpers
from bsbetl.cli_impl import (impl_process_1, impl_process_2, impl_process_3,
                             impl_process_3_topup, impl_results_1,
                             impl_results_2St_Pr, impl_results_2St_Vols,
                             impl_results_3st_jp, impl_results_3st_v2d,
                             impl_results_3st_x3nH, _impl_results_4st_frt)
from bsbetl.helpers import (validate_calc_stages, validate_date,
                            validate_share_num)

# logging
LOGGING_LEVEL = logging.DEBUG  # drop to logging.INFO when in production


@click.group(help='Command line utilities to Extract,Transform and Load raw BSB-supplied share trade TXT files')
@click.version_option(version=g.CONFIG_RUNTIME['version'])
# @click.option('--container_path', '-p', envvar='BSB_CONTAINER_PATH', type=click.Path(exists=True), required=False, default=g.DEFAULT_CONTAINER_PATH, show_default=False,
#              help="Top containing folder, MUST be supplied by environment. e.g. $env:BSB_CONTAINER_PATH='\BsbEtl'")
@click.pass_context
def main(ctx):
    """ entry point

    bsbetl = BSB Extract Transform Load
    This method is the entry point of the module.
    It sets up logging and, if startup checking passes,
    it takes module level options and stores them in a context object
    which the below implemented commands may use
    """
    container_path = g.CONTAINER_PATH

    helpers.mandatory_path_check(container_path)

    helpers.setup_logging(container_path, LOGGING_LEVEL)

    # suppress the opening logging mirroring to console if the user is just asking for help
    if not sys.argv[-1] == '--help':
        logging.info('')
        logging.info(
            f'MAIN Start. Parameters: container_path={container_path}')

    if functions.hlp_startup_checks(container_path, g.REQUIRED_SUBFOLDERS):
        logging.info('Script terminates.')
        sys.exit()

    # NOTE important!
    # set up context for commands to use
    ctx.obj['container_path'] = container_path


@ main.command()
@ click.option('--bsb_username', '-u', envvar='BSB_USERNAME', required=True)
@ click.pass_context
def fetch_catalog(ctx, bsb_username: str):
    """ Download latest catalog (Inhalt.txt) from BSB server

    Inhalt.txt is used to request files for download by the 'fetch-txt' command.
    This cmd is rarely needed to be invoked on its own since it gets automatically performed 
    when performimg a 'fetch-txt' cmd, but can be used as a quick connectivity check.

    A username & password will be required.
    For convenience, the environment variable 'BSB_USERNAME', if set, will be used
    and you wont be prompted for a username.
    Set it in Powershell like so e.g. >> $env:BSB_USERNAME="leon" (once only per session)
    """

    logging.info(f'/ Command {inspect.stack()[0][3]} ...Parameters: None')
    startTime = datetime.now()

    catalog_url = g.SHARE_SERVICE_URL + g.SHARE_SERVICE_CATALOG_NAME
    local_catalog_name_fq = f'{g.CONTAINER_PATH}\{g.SHARE_SERVICE_CATALOG_NAME}'

    functions.fetch_txt_catalog(
        catalog_url, bsb_username, local_catalog_name_fq)

    winsound.Beep(3000,1000)
    logging.info(
        f"\ End {inspect.stack()[0][3]} command. Duration: {datetime.now() - startTime}")


@ main.command()
@ click.option('--bsb_username', '-u', envvar='BSB_USERNAME', required=True)
@ click.option('--date', '-d', type=str, callback=validate_date, required=False, default=helpers.latest_TXT_date(), help='YYYY_MM_DD fetch TXT files on or after this date')
@ click.pass_context
def fetch_txt(ctx, bsb_username: str, date: str):
    """ Fetch all TXT files from BSB service dated from 'date' onwards

    NOTE: The command 'fetch-catalog' is automatically run as the first step of the process  !!!

    'date' is determined automatically but can be overriden.

    A username & password will be required.
    For convenience, the environment variable 'BSB_USERNAME', if set, will be used
    and you wont be prompted for a username.
    Set it in Powershell like so e.g. >> $env:BSB_USERNAME="leon" (once only per session)

    TODO: don't allow TXT file of the current day to be retained if its been downloaded before 18:00

    """
    logging.info(
        f'/ Command {inspect.stack()[0][3]} ...Parameters: date={date}')
    startTime = datetime.now()

    catalog_url = g.SHARE_SERVICE_URL + g.SHARE_SERVICE_CATALOG_NAME
    local_catalog_name_fq = f'{g.CONTAINER_PATH}\{g.SHARE_SERVICE_CATALOG_NAME}'
    pwd, _ = functions.fetch_txt_catalog(
        catalog_url, bsb_username, local_catalog_name_fq)

    if pwd == '':
        logging.error(f'login failure')
    else:
        ctx.obj['first_date'] = date
        functions.fetch_txt_files(ctx, bsb_username, pwd)

    winsound.Beep(3000,1000)

    logging.info(
        f"\ End {inspect.stack()[0][3]} command. Duration: {datetime.now() - startTime}")


@ main.command()
@ click.option('--keep/--no-keep', is_flag=True, type=bool, default=True, show_default=False, help="Flag: keep or delete TXT after processing (keeps by default)")
@ click.pass_context
def process_1(ctx, keep: bool):
    """ Generate a CSV 'By Day' file for every daily TXT file on hand

        IMPORTANT: The commands 'fetch-catalog' and 'fetch-txt' are assumed to have been freshly run beforehand !!!

    """

    impl_process_1(ctx, keep=True)



@ main.command()
@ click.option('--sharelist', '-l', type=click.Choice(g.SHARELISTS), default=helpers.suggest_default_sharelist(), show_default=True, required=True)
#@ click.option('--one_share_only', '-n', type=str, default='ignore', show_default=False, required=False, callback=validate_share_num, help='process only this share number (skip the others')
@ click.option('--recreate/--append', is_flag=True, type=bool, default=False, show_default=True, help="Flag: Create all share folders/files from scratch for the current sharelist (The default (False) is to append to existing files)")
@ click.pass_context
def process_2(ctx, sharelist: str, recreate :bool):  #, one_share_only: str):
    """ Prepare CSV 'By Share' files (from the CSV 'By Day' files) for the specified sharelist

        IMPORTANT: The commands 'fetch-catalog', 'fetch-txt' and 'process-1' are assumed to have been freshly run beforehand !!!

        The CSV 'By Share' files are what all the subsequent share analyses depend on.
        If flag --append is provided (this is the default if not provided) new trades get appended to the existing share files.
        If flag --recreate is provided, once this has been run, ALL all-tables and Overviews are 
        effectively deleted, in preparation for a new process-3 run
    """
    # BEHAVIOUR DESCRIBED BELOW NO LONGER THE CASE:
    # Subsequent runs of this command merely append to these files. 
    # If no CSV 'By Share' file yet exists, it will be created and trades from 'earliest_analysis_date' onward
    # in the CSV 'By Day' files will be distributed. 
    # (SW will make an effort to look back to fill even the missing CSV data of the most out of date share)


    # NOTE this is now a setting, and no longer a command line parameter:
    # one effectively cannot do calculations on earlier data than this
    # start_date = g.CONFIG_SETTINGS['analysis_start_date'] <-- setting no longer used

    impl_process_2(ctx,sharelist,recreate)

@main.command()
@click.option('--sharelist', '-l', type=click.Choice(g.SHARELISTS), default=helpers.suggest_default_sharelist(), show_default=True, required=True)
@click.option('--one_share_only', '-n', type=str, default='ignore', required=False, callback=validate_share_num, help='process only this share number (skip the others')
@click.option('--start_date', '-d', type=str, required=True, callback=validate_date, default=functions.get_date_for_busdays_back(g.CONFIG_RUNTIME['default_days_back']), show_default=True, help="start_date must be this form: YYYY_MM_DD")
@click.option('--end_date', '-e', type=str, required=True, callback=validate_date, default=functions.get_date_for_busdays_back(0), show_default=True, help="end_date must be this form: YYYY_MM_DD")
@click.option('--stages', '-s', type=list, default=g.CALC_STAGES, show_default=True, callback=validate_calc_stages, help='stages to calculate. (all are done by default) e.g. -s 2 will do only stage 2 calcs')
@click.confirmation_option(prompt=f"Recalculates EVERYTHING from start_date (default is {g.CONFIG_RUNTIME['default_days_back']} trading days back) to end_date. (Be sure its not a top-up you are wanting) So, are you SURE?")
@click.pass_context
def process_3(ctx, sharelist: str, one_share_only: str, start_date: str, end_date: str, stages: list):
    """ Compute all-table & overview calcs for the specified (or default) sharelist

         NOTE. This is the FULL run. It is meant to lay down the base All-Tables 
         into which Top-Ups takes place!!! So, set the start_date accordingly.
         The default start_date is 100 trading days back from today's date.
         Calculations start at start_date and run until end of data.

         Limit operations to a single share (for testing purposes) with the -n option.
    """

    impl_process_3(sharelist, one_share_only, start_date, end_date, stages)


@main.command()
@click.option('--sharelist', '-l', type=click.Choice(g.SHARELISTS), default=helpers.suggest_default_sharelist(), show_default=True, required=True)
@click.option('--one_share_only', '-n', type=str, default='ignore', required=False, callback=validate_share_num, help='process only this share number (skip the others')
@click.confirmation_option(prompt='Merely add & compute newly available data. Are you SURE?')
@click.pass_context
def process_3_topup(ctx, sharelist: str, one_share_only: str):
    """ Compute all-table & overview level-1 calcs for new By_Share CSV data

         NOTE. This is merely a Top-Up!!!
         Use after process-1 & process-2 has put new CSV files into the CSV By Share folders.
         Existing calculations in the ATs are preserved - just the new dates get calculated.
         Calculations start at last calculation rows and run until end of available new data.

        Limit operations to a single share (for testing purposes) with the -n option.
    """

    impl_process_3_topup(sharelist, one_share_only)


@main.command()
@click.option('--size', '-s', type=int, required=False, default=100, show_default=True, help="For testing purposes, generate a random sharelist. Name will be 'random_n.shl'")
@click.pass_context
def random_sharelist(ctx, size):
    ''' Generate (for subsequent testing purposes) a sharelist file named 'random_{size}.shl' '''

    logging.info(
        f"/ Command {inspect.stack()[0][3]}...  Parameters: ")
    startTime = datetime.now()

    functions.generate_random_sharelist(size)

    logging.info(
        f"\ End {inspect.stack()[0][3]} command. Duration: {datetime.now() - startTime}")
    return

@main.command()
@click.option('--sharelist', '-l', type=click.Choice(g.SHARELISTS), default=helpers.suggest_default_sharelist(), show_default=True, required=True)
@click.confirmation_option(prompt='Confirm you have run process-3 up to date')
@click.pass_context
def results_1(ctx, sharelist):
    """ Applies '1St Conditions' to sharelist members and compiles '1St results'
    """
    impl_results_1(ctx,sharelist)

@main.command()
@click.option('--sharelist', '-l', type=click.Choice(g.SHARELISTS), default=helpers.suggest_default_sharelist(), show_default=True, required=True)
@click.confirmation_option(prompt='Confirm you have run the preceding results-building steps')
@click.pass_context
def results_2St_Pr(ctx, sharelist):
    """ Applies '2StPr Conditions' to sharelist members and compiles '2StPr results'
    """
    impl_results_2St_Pr(ctx,sharelist)


@main.command()
@click.option('--sharelist', '-l', type=click.Choice(g.SHARELISTS), default=helpers.suggest_default_sharelist(), show_default=True, required=True)
@click.confirmation_option(prompt='Confirm you have run the preceding results-building steps')
@click.pass_context
def results_2St_Vols(ctx, sharelist):
    """ Applies '2StVols Conditions' to sharelist members and compiles '2StVols results'
    """
    impl_results_2St_Vols(ctx,sharelist)

@main.command()
@click.option('--sharelist', '-l', type=click.Choice(g.SHARELISTS), default=helpers.suggest_default_sharelist(), show_default=True, required=True)
#@click.option('--start_date', '-d', type=str, required=True, callback=validate_date, default=functions.get_date_for_busdays_back(240), show_default=True, help="start_date must be this form: YYYY_MM_DD")
@click.confirmation_option(prompt='Confirm you have run the preceding results-building steps')
@click.pass_context
def results_3st_jp(ctx, sharelist):
    """ Combines 1St,2StPr,2StVols results, applies additional conditions & creates a '3jP' sharelist
        of qualifying shares. Then re-runs 'process-3' on that reduced sharelist with 
        needed minutely calculations on the reduced list of shares, saving a results_3jP Overview for inspection.
    """

    # get start_date, end_date  from config runtime
    start_date = g.CONFIG_RUNTIME['process-3-last-start']
    end_date = g.CONFIG_RUNTIME['process-3-last-end']

    impl_results_3st_jp(ctx,start_date,end_date, sharelist)

@main.command()
#@click.option('--start_date', '-d', type=str, required=True, callback=validate_date, default=functions.get_date_for_busdays_back(240), show_default=True, help="start_date must be this form: YYYY_MM_DD")
@click.option('--sharelist', '-l', type=click.Choice(g.SHARELISTS), default=helpers.suggest_default_sharelist(), show_default=True, required=True)
@click.confirmation_option(prompt='Confirm you have run the preceding results-building steps')
@click.pass_context
def results_3st_v2d(ctx, sharelist):
    """ Uses 1St,2StPr and 2StVols results & applies additional conditions 
        per document '3 Stage Vol up few days V2d' to produce a V2d shareslist.
        This reduced 'V2d' shares are subjected to a process-3 run 
        which performs additional minutely processing
        The end result is an Overview of the V2d sharelist        
    """
    # get start_date, end_date  from config runtime
    start_date = g.CONFIG_RUNTIME['process-3-last-start']
    end_date = g.CONFIG_RUNTIME['process-3-last-end']

    impl_results_3st_v2d(ctx,start_date,end_date,sharelist)

@main.command()
#@click.option('--start_date', '-d', type=str, required=True, callback=validate_date, default=functions.get_date_for_busdays_back(240), show_default=True, help="start_date must be this form: YYYY_MM_DD")
@click.option('--sharelist', '-l', type=click.Choice(g.SHARELISTS), default=helpers.suggest_default_sharelist(), show_default=True, required=True)
@click.confirmation_option(prompt='Confirm you have run the preceding results-building steps')
@click.pass_context
def results_3st_x3nH(ctx, sharelist):
    """ Per document: 3 new Heights "3nH":
    """
    start_date = g.CONFIG_RUNTIME['process-3-last-start']
    end_date = g.CONFIG_RUNTIME['process-3-last-end']
    impl_results_3st_x3nH(ctx,start_date,end_date,sharelist)

@main.command()
@ click.option('--overwrite/--update', is_flag=True, type=bool, default=False, show_default=True, help="Flag: Overwrite/Update Final Results overview")
@click.confirmation_option(prompt='Confirm you have run the preceding results-building steps')
@click.pass_context
def results_4st_frt(ctx, overwrite):
    """ 
    Per document: 3 The Final Result Table "FRT", overwrites / updates FRT using 'default' sharelist results.
    The flag '--update' causes an update to an existing FRT overview (this is the default action anyway). 
    But you can cause an entirely new FRT to be created by passing flag '--overwrite' on the command line

    """

    #print(f'results_4st_frt: overwrite={overwrite}')

    _impl_results_4st_frt(ctx, overwrite)


@main.command()
@click.option('--sharelist', '-l', type=click.Choice(g.SHARELISTS), default=helpers.suggest_default_sharelist(), show_default=True, required=True)
@click.option('--target', '-t', type=click.Choice(g.HEALTH_REPORT_TARGETS), default=g.HEALTH_REPORT_TARGETS[0], show_default=True, required=True)
@click.pass_context
def report_health(ctx, sharelist: str, target: str):
    """ Write a health check report for chosen target

    """

    logging.info(
        f"/ Command {inspect.stack()[0][3]}...  Parameters: ")
    startTime = datetime.now()

    ctx.obj['sharelist_name'] = sharelist + '.shl'
    ctx.obj['health_target'] = target
    ctx.obj['stage'] = 1  # for now

    functions.write_health_report(ctx)

    logging.info(
        f"\ End {inspect.stack()[0][3]} command. Duration: {datetime.now() - startTime}")

@ main.command()
@ click.option('--echo', '-e', type=bool, is_flag=True, default=True, help="echo to screen also")
@ click.pass_context
def status(ctx, echo: bool):
    """ Append a status report to StatusReport.txt and write a new StatusReport.MD (markdown) version """

    logging.info(
        f'/ Command {inspect.stack()[0][3]} ...Parameters: echo={echo}')
    startTime = datetime.now()

    # first the markdown version
    functions.write_status_report_md()
    # then the text version
    status = functions.write_status_report_txt(ctx)

    logging.info(
        f'\ Done {inspect.stack()[0][3]} command. Duration: {datetime.now() - startTime}')

    if echo:
        click.echo(click.style('\nStatusReport:',
                               reverse=True, fg='bright_magenta'))
        for item in status:
            print(item.rstrip())

@ main.command()
@ click.pass_context
def go_gui(ctx):
    ''' brings up a simple GUI for exercising bsbetl commands (using default paramters)'''

    bsbetl_gui.gui_entry(ctx)


########################################################################

def start():
    main(obj={})


if __name__ == '__main__':
    start()
