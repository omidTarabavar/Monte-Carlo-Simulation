from scipy.stats import norm
from random import random
from tkinter import *
class Activity:
    def __init__(self,name, a, m, b,preds= None):
        self.name = name
        self.a = a
        self.m = m
        self.b = b
        self.mean = self.calc_expectedTime()
        self.sd = self.calc_sd()
        self.preds = preds if preds else []
        self.dur = None
        self.ES = None
        self.EF = None
        self.LS = None
        self.LF = None
    
    def calc_expectedTime(self):
        return (self.a + 4*self.m + self.b) / 6
    
    def calc_sd(self):
        sd = ((self.b - self.a) / 6)
        if(sd == 0):
            sd = 0.0001
        return sd
    
    
    def calc_dur(self):
        temp = norm.ppf(random(), loc = self.mean, scale = self.sd)
        self.dur = round(temp)
        
def cal_ES_EF(activities):
    for activity in activities.values():
        if not activity.preds:
            activity.ES = 0
            activity.EF = activity.dur
        else:
            max_pred_finish = max(activities[p].EF for p in activity.preds)
            activity.ES = max_pred_finish
            activity.EF = max_pred_finish + activity.dur

def cal_LS_LF(activities,projectDur):
    for activity in reversed(list(activities.values())):
        if activity.EF == projectDur:
            activity.LF = projectDur
            activity.LS = projectDur - activity.dur
        else:
            for succ_ac in reversed(list(activities.values())):
                if activity.name in succ_ac.preds:
                    if not activity.LF:
                        activity.LF = succ_ac.LS
                        activity.LS = activity.LF - activity.dur
                    else:
                        activity.LF = min(succ_ac.LS,activity.LF)
                        activity.LS = activity.LF - activity.dur
        if(not activity.LF or not activity.LS):
            activity.LF = activity.EF
            activity.LS = activity.ES
        
def crit_path(activities):
    crits = []
    for act in activities.values():
        if act.EF == act.LF and act.ES == act.LS:
            crits.append(act)
    return crits       
        
def clean_acs(acs):
    for ac in acs.values():
        ac.dur = None
        ac.ES = None
        ac.EF = None
        ac.LS = None
        ac.LF = None
        
def calc_totalTime(activities):
    cal_ES_EF(activities)
    proj_dur = max(activity.EF for activity in activities.values())
    cal_LS_LF(activities,proj_dur)
    projTime = max(activity.LF for activity in activities.values())
    return projTime

# acA = Activity('A',1,1,1)
# acB = Activity('B',3,4,5)
# acC = Activity('C',1,2,3,['A'])
# acD = Activity('D',1,3,5,['A'])
# acE = Activity('E',2,3,4,['B','C'])
# acF = Activity('F',2,2,2,['D'])
# acG = Activity('G',1,3,5,['E','F'])

activities = {}


# Window
window = Tk()
window.title("PM Project: Monte Carlo simulation")
window.geometry("1100x600")
window.resizable(width=False,height=False)

# Labels
Label(window,text="Activity Name:").place(x=470,y=90)
Label(window, text="Optimistic Time:").place(x=470,y=120)
Label(window,text="Average Time:").place(x=670,y=120)
Label(window,text="Pesimistic Time:").place(x=870,y=120)
Label(window,text="Predecessors (split them with space):").place(x=670,y=90)
Label(window,text="Omid Tarabavar [400213016]",foreground='green',font=("Comic Sans MS",10)).place(x=0,y=0)
Label(window,text="Note: Use Python +3.8",foreground='red').place(x=970,y=0)
Label(window,text="N (number of simulations):").place(x=550,y=382)
#Entry Boxes
te_act_name = Entry(window,width=10,bg='white')
te_act_name.place(x=565,y=90)
te_act_optT = Entry(window,width=10,bg='white')
te_act_optT.place(x=565,y=120)
te_act_avgT = Entry(window,width=10,bg='white')
te_act_avgT.place(x=752,y=120)
te_act_pesT = Entry(window,width=10,bg='white')
te_act_pesT.place(x=960,y=120)
te_act_preds = Entry(window,width=24,bg='white')
te_act_preds.place(x=875,y=90)
te_N = Entry(window,width=10,bg='white')
te_N.place(x=700,y=385)

#Funcs
def on_scroll(*args):
    acts.yview(*args)
def add():
    name = te_act_name.get()
    opt = int(te_act_optT.get())
    avg = int(te_act_avgT.get())
    pes = int(te_act_pesT.get())
    preds = te_act_preds.get().split(' ')
    if(not preds[0]):
        preds = None
    activities[name] = Activity(name,opt,avg,pes,preds)
    te_act_name.delete(0,END)
    te_act_optT.delete(0,END)
    te_act_avgT.delete(0,END)
    te_act_pesT.delete(0,END)
    te_act_preds.delete(0,END)
    show_acts()
def show_acts():
    acts.delete('0.0',END)
    for ac in activities.values():
        acts.insert(END,f"Name: {ac.name}\tOpt Time: {ac.a}\tAvg Time: {ac.m}\tPes Time: {ac.b}\t Predesessors: {ac.preds if ac.preds else 'None'}\n")

def calculate():
    result.delete("0.0",END)
    if len(activities.values()) == 0:
        result.insert(END,"There is no activity!")
    else:
        times = []
        n = te_N.get()
        if(n == ''):
            result.insert(END,"Please enter N!")
        else:
            N = int(te_N.get())
            crit_chance = {act:0 for act in activities}
            for i in range(N):
                for activity in activities.values():
                    activity.calc_dur()
                times.append(calc_totalTime(activities))
                crit_acs = crit_path(activities)
                for acs in crit_acs:
                    crit_chance[acs.name] += 1
                clean_acs(activities)
            result.insert(END,"Time\tCount\tProbability\n")
            for i in range(min(times),max(times)+1):
                if(times.count(i) != 0):
                    cnt = times.count(i)
                    result.insert(END,f"{i}\t{cnt}\t{cnt/N * 100:.2f}%\n")
            result.insert(END,"------------------------\n")
            result.insert(END,"Event\tCritifal Chance\n")
            for item in crit_chance:
                result.insert(END,f"{item}\t{crit_chance[item] / N * 100:.2f}%\n")
def del_acts():
    activities.clear()
    acts.delete('0.0',END)  
def del_last_act():
    activities.popitem()
    show_acts()
       
def close_window():
    window.destroy()
    exit()
    
#Buttons
Button(window,text="Add",width=4,command=add).place(x=720,y=160)
Button(window,text="Simulate",width=8,command=calculate).place(x=800,y=380)
Button(window,text="Remove last activity",width=16,command=del_last_act).place(x=470,y=160)
Button(window,text="Remove all activities",width=16, command=del_acts).place(x=900,y=160)
Button(window,text="Exit",width=10,height=3,command=close_window).place(x=1005,y=530)

#Text Boxes
acts = Text(window,width=50,height=10,wrap=WORD,background='white')
acts.place(x=20,y=50)
sb_acts = Scrollbar(window,command=on_scroll,orient=VERTICAL)
sb_acts.place(x=423,y=50,height=163)
acts.config(yscrollcommand=sb_acts.set)
result = Text(window,width=50,height=20,wrap = WORD, background='white')
result.place(x=20,y=250)
sb_res = Scrollbar(window,command=on_scroll,orient=VERTICAL)
sb_res.place(x=423,y=250,height=325)
result.config(yscrollcommand=sb_res.set)


window.mainloop()
        

