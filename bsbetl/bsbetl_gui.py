from calendar import month
from datetime import datetime
from tkinter import *
from tkinter import messagebox
from tkinter import simpledialog
from tkinter.messagebox import *
from tkinter.simpledialog import *
from tkinter.ttk import *
from tkcalendar import Calendar
from tkinter.messagebox import askyesno

import winsound
from bsbetl import app
from bsbetl.cli_impl import _impl_results_4st_frt, impl_process_1,impl_process_2, impl_process_3, impl_process_3_topup, impl_results_1, impl_results_2St_Pr, impl_results_2St_Vols, impl_results_3st_jp, impl_results_3st_v2d, impl_results_3st_x3nH
from bsbetl import functions, g, helpers


def process_1_click(ctx):

    impl_process_1(ctx,True)

    print('\nprocess-1 has ENDED... ')
    winsound.Beep(3000,1000)
    #print('Choose another command or Close GUI if done.\n')

def process_2_click(ctx):

    impl_process_2(ctx,'Default',recreate=False)

    print('\nprocess-2 has ENDED... ')
    #winsound.PlaySound('SystemAsterisk', winsound.SND_ALIAS)
    winsound.Beep(3000,1000)
    #print('Choose another command or Close GUI if done.\n')

def process_3_click(ctx):

    #start_date = functions.get_date_for_busdays_back(g.CONFIG_RUNTIME['default_days_back'])
    start_date = ctx.obj['btn_start']['text']
    end_date = ctx.obj['btn_end']['text']

    answer = askyesno(title='Confirm full recalculation date range',message=f'Re-calculate all from {start_date} -> {end_date} ?')
    if answer:
        impl_process_3('Default', '', start_date, end_date, [1,2])
        print('\nprocess-3 has ENDED... ')
        #winsound.PlaySound('SystemAsterisk', winsound.SND_ALIAS)
        winsound.Beep(3000,1000)

def process_3_topup_click(ctx):

    answer = askyesno(title='Confirm Top-up',message=f'Are you sure you want to perform a top-up using newly arrived data?')
    if answer:
        impl_process_3_topup(ctx,'Default', '')
        print('\nprocess-3-topup has ENDED... ')
        #winsound.PlaySound('SystemAsterisk', winsound.SND_ALIAS)
        winsound.Beep(3000,1000)

def results_1_click(ctx):

    impl_results_1(ctx,'Default')

    print('\nresults-1 has ENDED... ')
    ctx.obj['results-1-btn'].config(text='results-1 DONE', state='disabled')
    #winsound.PlaySound('SystemAsterisk', winsound.SND_ALIAS)
    winsound.Beep(3000,1000)
    #print('Choose another command or Close GUI if done.\n')

def results_2st_pr_click(ctx):

    impl_results_2St_Pr(ctx,'Default')

    print('\nresults-2st-pr has ENDED... ')
    ctx.obj['results-2st-pr-btn'].config(text='results-2st-pr DONE', state='disabled')
    #winsound.PlaySound('SystemAsterisk', winsound.SND_ALIAS)
    winsound.Beep(3000,1000)
    #print('Choose another command or Close GUI if done.\n')

def results_2st_vols_click(ctx):

    impl_results_2St_Vols(ctx,'Default')

    print('\nresults-2st-vols has ENDED... ')
    ctx.obj['results-2st-vols-btn'].config(text='results-2st-vols DONE', state='disabled')
    #now we know should how many shares are in the 3jP list - put it in the 3jP button
    ctx.obj['results-3st-jp-btn'].config(text=f"results-3st-jp ({len(g.CONFIG_RUNTIME['_3jP_list'])} shares)")

    #winsound.PlaySound('SystemAsterisk', winsound.SND_ALIAS)
    winsound.Beep(3000,1000)
    #print('Choose another command or Close GUI if done.\n')

def results_3st_jp_click(ctx):

    #start_date=functions.get_date_for_busdays_back(g.CONFIG_RUNTIME['default_days_back'])
    start_date = g.CONFIG_RUNTIME['process-3-last-start']
    end_date = g.CONFIG_RUNTIME['process-3-last-end']

    impl_results_3st_jp(ctx,start_date,end_date,'Default')

    print('\nresults-3st-jp has ENDED... ')
    prior_text = ctx.obj['results-3st-jp-btn']['text']
    ctx.obj['results-3st-jp-btn'].config(text=f"{prior_text} DONE", state='disabled')
    # also update the following button text showing number of shares in the v2d list
    prior_text = ctx.obj['results-3st-v2d-btn']['text']
    ctx.obj['results-3st-v2d-btn'].config(text=f"{prior_text} ({len(g.CONFIG_RUNTIME['_V2d_list'])} shares)")
    #winsound.PlaySound('SystemAsterisk', winsound.SND_ALIAS)
    winsound.Beep(3000,1000)
    #print('Choose another command or Close GUI if done.\n')

def results_3st_v2d_click(ctx):

    #start_date=functions.get_date_for_busdays_back(g.CONFIG_RUNTIME['default_days_back'])
    start_date = g.CONFIG_RUNTIME['process-3-last-start']
    end_date = g.CONFIG_RUNTIME['process-3-last-end']
    impl_results_3st_v2d(ctx,start_date,end_date,'Default')

    print('\nresults-3st-v2d has ENDED... ')
    prior_text = ctx.obj['results-3st-v2d-btn']['text']

    ctx.obj['results-3st-v2d-btn'].config(text=f"{prior_text} DONE", state='disabled')
    # and also update x3nh button with number of shares
    prior_text = ctx.obj['results-3st-x3nh-btn']['text']
    ctx.obj['results-3st-x3nh-btn'].config(text=f"{prior_text} ({len(g.CONFIG_RUNTIME['_3nH_list'])} shares)")

    #winsound.PlaySound('SystemAsterisk', winsound.SND_ALIAS)
    winsound.Beep(3000,1000)
    #print('Choose another command or Close GUI if done.\n')

def results_3st_x3nh_click(ctx):

    #start_date=functions.get_date_for_busdays_back(g.CONFIG_RUNTIME['default_days_back'])
    start_date = g.CONFIG_RUNTIME['process-3-last-start']
    end_date = g.CONFIG_RUNTIME['process-3-last-end']
    impl_results_3st_x3nH(ctx,start_date,end_date,'Default')

    print('\nresults-3st-x3nh has ENDED... ')
    prior_text = ctx.obj['results-3st-x3nh-btn']['text']
    ctx.obj['results-3st-x3nh-btn'].config(text=f"{prior_text} DONE ({len(g.CONFIG_RUNTIME['_3nH_list'])} shares)", state='disabled')
    #winsound.PlaySound('SystemAsterisk', winsound.SND_ALIAS)
    winsound.Beep(3000,1000)
    #print('Choose another command or Close GUI if done.\n')

def results_4st_frt_click(ctx):

    _impl_results_4st_frt(ctx, overwrite=False)

    print('\nresults-4st-frt has ENDED... ')
    prior_text = ctx.obj['results-4st-frt-btn']['text']
    ctx.obj['results-4st-frt-btn'].config(text=f'{prior_text} DONE', state='disabled')
    #winsound.PlaySound('SystemAsterisk', winsound.SND_ALIAS)
    winsound.Beep(3000,1000)
    #print('Choose another command or Close GUI if done.\n')


def set_start(ctx):

    cur_end_date = ctx.obj['btn_end']['text']
    wanted_start_date = ctx.obj['cal'].get_date()
    if wanted_start_date > cur_end_date:
        winsound.Beep(3000,750)
        print(f'Wanted Start date {wanted_start_date} cannot be later than current End date {cur_end_date} !')
    else:
        ctx.obj['btn_start'].config(text=wanted_start_date)
        trading_days = helpers.compute_trading_days(wanted_start_date,cur_end_date)
        ctx.obj['days_label'].config(text=f'{trading_days} trading day(s)')

def set_end(ctx):

    cur_start_date = ctx.obj['btn_start']['text']
    wanted_end_date = ctx.obj['cal'].get_date()
    if wanted_end_date < cur_start_date:
        winsound.Beep(3000,750)
        print(f'Wanted End date {wanted_end_date} cannot be earlier than current Start date {cur_start_date} !')
    else:
        ctx.obj['btn_end'].config(text=wanted_end_date)
        trading_days = helpers.compute_trading_days(cur_start_date,wanted_end_date)
        ctx.obj['days_label'].config(text=f'{trading_days} trading day(s)')

''' main section '''

def ready_the_gui(ctx):

    ctx.obj['gui_buttons'] = []
    
    root = Tk()
    root.title('bsbetl commands GUI')
    root.attributes('-topmost', True)

    style=Style()
    style.configure("W.TButton",background='yellow')

    # days label
    days_label= Label(root,text='1 trading day(s)')
    ctx.obj['days_label'] = days_label
    days_label.pack(pady=1)

    # set calendar to last process3 start date
    try:
        p3_start=g.CONFIG_RUNTIME['process-3-last-start']
        start_parts=p3_start.split('_')
        cal = Calendar(root,selectmode='day',year=int(start_parts[0]), month=int(start_parts[1]),day=int(start_parts[2]), date_pattern='yyyy_mm_dd')
    except KeyError:
        cal = Calendar(root,selectmode='day',year=datetime.now().year, month=datetime.now().month,day=datetime.now().day, date_pattern='yyyy_mm_dd')
    ctx.obj['cal'] = cal
    cal.pack(pady=6)

    #btn_start acts to set start date by altering the text on the face of it to reflect date in calendar
    btn_start = Button(root, text=f'{cal.get_date()}', command=lambda: set_start(ctx), style="W.TButton")
    ctx.obj['btn_start']=btn_start
    btn_start.pack(pady=6)

    to_label = Label(root,text='to')
    to_label.pack(pady=0)

    # try:
    #     p3_end=g.CONFIG_RUNTIME['process-3-last-end']
    #     end_parts=p3_start.split('_')
    #     cal = Calendar(root,selectmode='day',year=int(end_parts[0]), month=int(end_parts[1]),day=int(end_parts[2]), date_pattern='yyyy_mm_dd')
    # except KeyError:
    #     cal = Calendar(root,selectmode='day',year=datetime.now().year, month=datetime.now().month,day=datetime.now().day, date_pattern='yyyy_mm_dd')


    btn_end = Button(root, text=g.CONFIG_RUNTIME['process-3-last-end'], command=lambda: set_end(ctx), style="W.TButton")
    ctx.obj['btn_end']=btn_end
    btn_end.pack(pady=6)

    separator1 = Separator(root, orient='horizontal')
    separator1.pack(fill='x')

    # # This will create style object
    # style = Style()   
    # # This will be adding style, and
    # # naming that style variable as
    # # W.Tbutton
    # #style.configure('TButton', font = ('calibri', 10, 'bold', 'underline'), foreground = 'red')
    # style.configure('TButton', font = ('calibri', 12 ), borderwidth = '4')
    # #style.map('TButton', foreground = [('active', '!disabled', 'green')],  background = [('active', 'black')])
 
    btn = Button(root, text='process-1', command=lambda: process_1_click(ctx),)
    btn.pack(pady = 6)
    ctx.obj['gui_buttons'].append(btn)

    btn = Button(root, text='process-2', command=lambda: process_2_click(ctx))
    btn.pack(pady = 6)
    ctx.obj['gui_buttons'].append(btn)

    btn = Button(root, text='process-3', command=lambda: process_3_click(ctx), style="W.TButton")
    btn.pack(pady = 6)
    ctx.obj['gui_buttons'].append(btn)

    btn = Button(root, text='process-3-topup', command=lambda: process_3_topup_click(ctx))
    btn.pack(pady = 6)
    ctx.obj['gui_buttons'].append(btn)

    separator2 = Separator(root, orient='horizontal')
    separator2.pack(fill='x')

    btn = Button(root, text='results-1', command=lambda: results_1_click(ctx))
    btn.pack(pady = 6)
    ctx.obj['gui_buttons'].append(btn)
    ctx.obj['results-1-btn'] = btn
    

    btn = Button(root, text='results-2st-pr', command=lambda: results_2st_pr_click(ctx))
    btn.pack(pady = 6)
    ctx.obj['gui_buttons'].append(btn)
    ctx.obj['results-2st-pr-btn'] = btn

    btn = Button(root, text='results-2st-vols', command=lambda: results_2st_vols_click(ctx))
    btn.pack(pady = 6)
    ctx.obj['gui_buttons'].append(btn)
    ctx.obj['results-2st-vols-btn'] = btn

    btn = Button(root, text='results-3st-jp', command=lambda: results_3st_jp_click(ctx))
    btn.pack(pady = 6)
    ctx.obj['gui_buttons'].append(btn)
    ctx.obj['results-3st-jp-btn'] = btn

    btn = Button(root, text='results-3st-v2d', command=lambda: results_3st_v2d_click(ctx))
    btn.pack(pady = 6)
    ctx.obj['gui_buttons'].append(btn)
    ctx.obj['results-3st-v2d-btn'] = btn

    btn = Button(root, text='results-3st-x3nh', command=lambda: results_3st_x3nh_click(ctx))
    btn.pack(pady = 6)
    ctx.obj['gui_buttons'].append(btn)
    ctx.obj['results-3st-x3nh-btn'] = btn

    btn = Button(root, text='results-4st-frt', command=lambda: results_4st_frt_click(ctx))
    btn.pack(pady = 6)
    ctx.obj['gui_buttons'].append(btn)
    ctx.obj['results-4st-frt-btn'] = btn

    return root

def gui_entry(ctx):

    print('Launching GUI... close it to re-enable CLI control')

    root = ready_the_gui(ctx)

    root.mainloop()

    print('GUI closed.')

