#@(#)$Id: GuiLib.py,v 1.1 1999/11/11 21:23:04 tlevshin Exp $
#@(#)$Author: tlevshin $
#@(#)$Log: GuiLib.py,v $
#@(#)Revision 1.1  1999/11/11 21:23:04  tlevshin
#@(#)rename GuiBase to GuiLib
#@(#)
#***********************************************
#*   Farms Batch Gui                           *
#*   Base Classes                              *
#***********************************************    
from Tkinter import *
from ScrolledText import  ScrolledText
import tkMessageBox
import tkFileDialog
#***********************************************   
import string
import os
CLUSTER=""
def setCluster(name):
    global CLUSTER
    CLUSTER="("+name+")"
def getCluster():
    return CLUSTER

#***********************************************   
# Left justification for the fields 
#***********************************************   
def infoFormat(info,label):
    if len(info):
        lenL=len(info[0])
    elif len(label):
        lenL=len(label)
    else:
        return [],""
    maxL=[]
    reply=[]
    for i in range(0,lenL):
        maxL.append(0)
    for tup in [label]+info:
        i=0
        for item in tup:
            if len(item)>=maxL[i]:
                maxL[i]=len(item)
            i=i+1
    format=""
    for i in range(0,lenL):
        format=format+"%-"+repr(maxL[i])+"s "
    label=format % label
    for tup in info:
         reply.append(format % tup)

    return reply,label

def strFormat(str):
    l=string.split(str)
    s=""
    for field in l:
	if len(field)>15:
		field=field[0:14]
	s=s+string.ljust(field,15)+" "
    return s
#************************************
# BASE TK CLASSES:                  *
#         MenubuttonBase            *
#         ButtonBase                *
#         ButtonCancel              *
#         ButtonQuit                *
#         ButtonMonitor             *
#         ButtonPrint               *
#         ButtonCheck               *
#         ButtonPref                *
#         DisplayTmp                *
#         List                      *
#         Screen                    *
#         Preference                *
#************************************

#*************************************************************                           
class MenubuttonBase:
    def __init__(self,frame,title):
	self.menubutton=Menubutton(frame,text=title,foreground='red',background='grey',\
				   relief=RAISED,underline=0)
	self.menubutton.pack(side=LEFT)
	self.menu=Menu(self.menubutton)
	self.menubutton['menu']=self.menu
#*************************************************************

#*************************************************************
class ButtonBase:
    def __init__(self,frame,name,side="left",anchor='nw',fill='x',\
		 foreground='red',background='grey'):
	Button(frame,text=name,foreground=foreground,background=background,
	       command=self.action).pack(side=side,anchor=anchor,fill=fill)

    def action(self):
	    pass
#*************************************************************


#*************************************************************     
class ButtonMonitor(ButtonBase):
    def __init__(self,frame,top,name):
	ButtonBase.__init__(self,frame,name)
	self.top=top

    def action(self):
	self.top.hostlist()

#*************************************************************

#*************************************************************   
class ButtonPrint(ButtonBase):
    def __init__(self,frame,top,name):
	ButtonBase.__init__(self,frame,name)
	self.top=top

    def action(self):
	self.top.print_window()
#*************************************************************

#*************************************************************
class ButtonSave(ButtonBase):
    def __init__(self,frame,top,name):
        ButtonBase.__init__(self,frame,name)
        self.top=top

    def action(self):
        self.top.save()
#*************************************************************


#*************************************************************
class ButtonQuit(ButtonBase):
    def __init__(self,frame,top,name,side="left",anchor='nw',fill='x'):
	ButtonBase.__init__(self,frame,name,side,anchor,fill)
	self.top=top

    def action(self):
	self.top.updt=1
	self.top.destroy()
#******************************************************************	

#******************************************************************
class ButtonDestroy(ButtonBase):
    def __init__(self,frame,top,name,monitor,side="left",anchor='nw',fill='x'):
        ButtonBase.__init__(self,frame,name,side,anchor,fill)
        self.top=top
	self.monitor=monitor

    def action(self):
	self.monitor.killChild()
        self.top.updt=1
        self.top.destroy()
#****************************************************************

#****************************************************************
class ButtonPref(ButtonBase):
    def __init__(self,frame,top,name):
	ButtonBase.__init__(self,frame,name)
	self.top=top

    def action(self):
	self.top.prefer()
#****************************************************************

#**************************************************************
class ButtonChngColor(ButtonBase):
    def __init__(self,frame,top,what,name):
	Button(frame,text=name,foreground='red',background='grey',
	       command=self.action).grid(row=0,column=what,columnspan=1,sticky=NW+SE)
        self.top=top
        self.what=what

    def action(self):
        self.top.chngColor(self.what)

#**************************************************************

#****************************************************************
class ButtonCheck1:
    def __init__(self,frame,myself,act,name,row=40):
	Button(frame,text=name,foreground='red',background='grey',
	       command=self.action).grid(row=row,column=act,columnspan=1)
        self.top=frame
        self.myself=myself
        self.act=act

    def action(self):
        if self.act:
            self.myself.cancel=0
            self.myself.top.destroy()
            return
        if self.myself.check():
            return
        self.myself.top.destroy()
#***************************************************************


#****************************************************************	
class ButtonCheck(ButtonBase):
    def __init__(self,frame,myself,act,name,side):
	ButtonBase.__init__(self,frame,name,side=side)
	self.top=frame
	self.myself=myself
	self.act=act

    def action(self):
	if self.act:
	    self.myself.cancel=0
	    self.top.destroy()
	    return
	if self.myself.check():
	    return
	self.top.destroy()
#***************************************************************

#***************************************************************	
class ButtonCancel(ButtonBase):
    def __init__(self,frame,top,name,side="right"):
	ButtonBase.__init__(self,frame,name,side)
	self.top=top
	self.frame=frame

    def action(self):
	self.top.cancel()
	self.frame.destroy()
#***************************************************************

#***************************************************************
class Monitor:
    def __init__(self):
	self.child=[]
    def startChild(self,host):
	pid = os.fork()
        if pid==0 :#child
          path=os.environ['PYTHON_DIR']+"/bin/python"
	  arg=os.environ['FARMS_DIR']+"/bin/GuiRstat.py"
          try:
                os.execve(path,[path,arg]+host,os.environ)
                sys.exit (0)
          except:
		return 1
        elif pid <0:
		return 1
        else:	
		self.child.append(pid)
		return 0
    def checkChild(self):
	if len(self.child):
	   try:
		pid, sts = os.waitpid(-1, os.WNOHANG)
              	if pid:
                       self.child.remove(pid)
	   except:
		pass

    def killChild(self):
	childlist=[]
	for item in self.child:
	    childlist.append(item)
	for id in childlist:
	    try:
		os.system("kill "+repr(id))
		os.waitpid(id,0)
		self.child.remove(id)
	    except:
		pass
#***************************************************************

#***************************************************************
class List:
    def __init__(self,frame,file=''):
	self.frame=frame
	self.fl=Frame(self.frame)
	self.fl.pack(expand=YES,fill=BOTH)
	self.reply=None

    def select(self,event):                   
	index=self.listbox.curselection()
 	self.reply=[]
	for ind in index:
	    self.reply.append(self.listbox.get(string.atoi(ind)))
    def displayList(self,infolist,title,font="10x20",bg='grey',fg='black'):
	self.font=font
	scrollx=Scrollbar(self.fl)
	scrolly=Scrollbar(self.fl)
	list=Listbox(self.fl,font=font,background=bg,foreground=fg,exportselection=0)
	list.config(yscrollcommand=scrolly.set,xscrollcommand=scrollx.set,\
		relief=SUNKEN,width=50)
       	scrolly.config(command=list.yview,relief=SUNKEN)
	scrollx.config(command=list.xview,orient='horizontal',relief=SUNKEN)
	self.label=Label(self.fl,text=title,foreground='black',font=font)
	self.label.pack(side=TOP,anchor=W,expand=NO)
	scrolly.pack(side=RIGHT,fill=BOTH)
	scrollx.pack(side=BOTTOM,fill=BOTH)
	list.pack(side=BOTTOM,expand=YES,fill=BOTH)
	try:
	    lenInfo=len(infolist)
	except:
	    lenInfo=0
	for i in range(lenInfo):
	    list.insert(i,infolist[i]) 
	list.config(selectmode=EXTENDED,setgrid=1)
	list.bind("<ButtonRelease-1>",self.select)
	self.listbox=list
	self.LineCnt=lenInfo
	self.listbox.selection_set(0)
	self.reply=[]
	self.reply.append(self.listbox.get(0))
    def updateList(self,infolist,label):
	try:
	    for i in range(0,self.LineCnt):
		self.listbox.delete(self.LineCnt-i-1)
	    self.label.destroy()
	    self.label=Label(self.fl,text=label,foreground='black',font=self.font)
	    self.label.pack(side=TOP,anchor=W,expand=NO) 

	    for i in range(0,len(infolist)):
		self.listbox.insert(i,infolist[i])
	    self.LineCnt=len(infolist)
	    self.listbox.selection_set(0)
	    self.reply=[]
	    self.reply.append(self.listbox.get(0))	    
	except:
	    pass

#******************************************************************

#******************************************************************
class Screen:
    def __init__(self,master=None,title="",info=[],label="",side='bottom',pref=None):
	import pwd
	self.user=pwd.getpwuid(os.getuid())[0]
       	self.top = Toplevel(master,cursor='watch')
	self.top.protocol("WM_DELETE_WINDOW", self.destroyAll)
	self.title=title
	self.top.title(self.title+CLUSTER)
	self.top.updt=0
	self.redraw=0
	self.info=info
	self.label=label
	self.list=None
	self.side=side
	if pref==None:
	    self.preferFile()
	else:
	    self.pref=Preference(self.top,pref.userL,pref.timer,pref.font,pref.numJob,pref.fg,pref.bg)
	self.frame=Frame(self.top)
	self.frame.pack(side=self.side,expand=YES,fill=BOTH)
	self.menubar()
	try:
	    self.top.wait_visibility()
	except:
	    pass
	self.top.config(cursor='arrow')
	self.update()

    def destroyAll(self):
	self.top.destroy() 

    def update(self):  #update if timer is set
	if self.top.updt:
	    return
	self.get_info()
	if self.redraw:
	    self.list.updateList(self.info,self.label)
	else :
	    self.display()
	if self.pref.timer:
	    self.top.after(self.pref.timer*1000,self.update)
	else:
	    self.top.after(100000000,self.update)

    def updateStat(self): # static update - "update" button
	self.get_info()
	self.redisplay()     

    def redisplay(self):
	if self.info==None:
	    self.get_info()
	if self.list:
	    if self.redraw:
		self.list.updateList(self.info,self.label)
		return
	self.display()

    def display(self):
	if self.list:
	    self.list.fl.destroy()
	self.list=List(self.frame)
	self.list.displayList(self.info,self.label,self.pref.font,self.pref.bg,self.pref.fg)
	self.redraw=1

    def preferFile(self):
	try:
	    if not user:
		user=self.user
	    if not timer:
		timer=5
	    if not font:
		try:
		    font=os.environ['FARMS_FONT']
                except:
		    font="10x20"
            indx=string.find(font,"-p-")
            if indx >=0:
	    	tkMessageBox.showwarning('Bad Font'+CLUSTER,'Your default font '+\
			       'belongs to variable-width spacing font class')
	    if not bg:
		bg='grey'
	    if not fg:
		fg='black'
	except:
	    num=15
            try:
		font=os.environ['FARMS_FONT']
            except:
                font="10x20"
	    timer=25
	    bg='grey'
	    fg='black'
	
	self.pref=Preference(self.top,self.user,timer,font,num,fg,bg)

    def prefer(self):
	self.pref.cancel=1
	oldFont=self.pref.font
	oldTimer=self.pref.timer
	self.pref.getPref()
	self.redraw=0
	if self.pref.timer!=oldTimer:
		if oldTimer==0:
			self.update()
	else:
		self.updateStat()

    def get_info(self):
	pass

    def menubar(self):
	pass

    def save(self):
	import time
	date=time.ctime(time.time())
	fileName=tkFileDialog.asksaveasfilename(defaultextension=["*"],\
						filetypes=[("postscript","*.ps")],parent=self.top)
	if not len(fileName):
	    tkMessageBox.showwarning('Fail to save the file'+CLUSTER,\
				     "No File Name provided, will not save")
	    return
	message="Window "+self.title+" has been saved into file "+fileName
        if os.uname()[0]=='Linux':
	    cmd="/usr/bin/X11/xwd -name "+repr(self.title)+\
		 "|convert -comment "+repr(self.title)+\
		 " - ps:"+fileName
	else:
	    cmd="/usr/bin/X11/xwd -name "+repr(self.title)+\
		 "| /usr/bin/X11/xpr -device ps -gray 3 -header "+repr(self.title)+\
		 " -trailer "+repr(date)+"  > "+fileName
	retVal=os.system(cmd)
        if not retVal:	
	    tkMessageBox.showinfo('Saving the file'+CLUSTER,message)
	else:
	    tkMessageBox.showwarning('Fail to save the file'+CLUSTER,"Failed to save "+fileName)


    def print_window(self):
	import time
	date=time.ctime(time.time())
	queue=None
	message=""
	try:
	    l=open(os.environ["HOME"]+'/.flprrc','r').readlines()
	    for line in l:
		idx=string.find(line,'queue')
		if idx >= 0:
		    s=string.split(line[:-1])
		    queue=s[1]
		    message="print request for above sent to "+queue
		    break
	except:
	    message="User printer default file .flprrc doesn't exist.\n"+\
		     "Do you want to save the window into the file?"
	    if tkMessageBox.askokcancel('Saving the file'+CLUSTER,message):
		self.save()
	    return
	if os.uname()[0]=='Linux':
	    cmd="/usr/bin/X11/xwd -name "+repr(self.title)+\
                 "| convert -comment "+repr(self.title)+\
                 " - ps:- |flpr -q"+queue+">/dev/null 2>&1"
	else:
	    cmd="/usr/bin/X11/xwd -name "+repr(self.title)+\
		 "| /usr/bin/X11/xpr -device ps -gray 3 -header "+repr(self.title)+\
		 " -trailer "+repr(date)+" |flpr -q"+queue+">/dev/null 2>&1"
	retVal=os.system(cmd)
	if not retVal:
	    tkMessageBox.showinfo('Printing the file'+CLUSTER,message)
	else:
	    tkMessageBox.showwarning('Fail to print'+CLUSTER,"Failed to print "+self.title)
		
#******************************************************************


#******************************************************************
class Preference:
    def __init__(self,master,user,timer=25,font="10x20",num=15,fg='black',bg='grey'):
	self.master=master
	self.cancel=1
	if user=='root':
	    self.userL='all'
	else:
	    self.userL=user
	self.timer=timer
	self.numJob=num
	self.font=font
	self.fg=fg
	self.bg=bg

    def getPref(self):
	global s1,s2,s3
	s1,s2,s3=StringVar(),StringVar(),StringVar()
	s1.set(self.userL)
	s2.set(repr(self.timer))
	s3.set(self.numJob)
	oldfont=self.font
	self.setPref(s1,s2,s3)
	if self.cancel:
	    self.userL=s1.get()
	    self.timer=string.atoi(s2.get())
	    self.numJob=string.atoi(s3.get())
        else:
	   self.font=oldfont		

    def displayFont(self):
        scrollx=Scrollbar(self.frame)
        scrolly=Scrollbar(self.frame)
        list=Listbox(self.frame)
        list.config(yscrollcommand=scrolly.set,xscrollcommand=scrollx.set,\
                relief=SUNKEN)
        scrolly.config(command=list.yview,relief=SUNKEN)
        scrollx.config(command=list.xview,orient='horizontal',relief=SUNKEN)
        scrolly.grid(row=3,column=20,columnspan=1,sticky=N+S)
        scrollx.grid(row=21,column=0,columnspan=20,sticky=E+W)
        list.grid(row=3,column=0,columnspan=20,sticky=NW+SE)
        for i in range(len(self.info)):
            list.insert(i,self.info[i])
        list.config(selectmode=SINGLE)
        list.bind("<ButtonRelease-1>",self.select)
        self.listbox=list
        self.listbox.selection_set(0)
        self.reply=self.listbox.get(0)
        self.disp=Label(self.frame,relief=SUNKEN,\
        text="Those are the font,foreground and background you have chosen",\
	foreground=self.fg,background=self.bg)
        self.disp.grid(row=22,column=0,columnspan=20,sticky=E+W)

    def select(self,event=None):
	if event:
        	index=self.listbox.curselection()
        	self.reply=self.listbox.get(index)
		self.font=self.reply
        self.disp.destroy()
        self.disp=Label(self.frame,text="Those are the font,foreground and background you have chosen",\
	relief=SUNKEN, background=self.bg,\
        font=self.reply,width=60,foreground=self.fg)
        self.disp.grid(row=22,column=0,columnspan=20,sticky=E+W)

    def chngColor(self,what):
        import tkColorChooser
        cl=tkColorChooser.askcolor()[1]
        if cl:
                if what:
                        self.fg=cl
                else:
                        self.bg=cl
        self.select()




    def setPref(self,user,timer,numJob):
	self.top = Toplevel(self.master)
	self.top.title('Display Preference'+CLUSTER)
	self.frame=Frame(self.top)
	self.frame.grid(row=0,column=0,rowspan=45,columnspan=22,sticky=NW+SE)
	ButtonChngColor(self.frame,self,0,'BgColor')
        ButtonChngColor(self.frame,self,1,'FgColor')
	self.info=[]
        for line in os.popen('xlsfonts').readlines():
            	indx=string.find(line,"-p-")
		if indx <0 :
                	self.info.append(line[:-1])
	l=Label(self.frame,text='Font & Colors',background='white',foreground='black')
	l.grid(row=2,columnspan=20,sticky=E+W)
	self.displayFont()	
		
	Label(self.frame,text='User name?',relief=RIDGE,width=25,background='white',foreground='black').\
	grid(row=27,column=0,sticky=W)
	e1=Entry(self.frame,textvariable=user, relief=SUNKEN, background='pink',width=20)
	e1.grid(row=27,column=1,sticky=W)
	Label(self.frame,text='Update time(in sec)?',relief=RIDGE,width=25,background='white',foreground='black').grid(row=28,column=0,sticky=W)
	e2=Entry(self.frame,textvariable=timer,relief=SUNKEN,background='pink',width=20)
	e2.grid(row=28,column=1,sticky=W)
	#Label(self.frame,text='Number of jobs ?',relief=RIDGE,width=25,background='white',foreground='black').grid(row=29,column=0,sticky=W)
	#e3=Entry(self.frame,textvariable=numJob,relief=SUNKEN,width=5,background='pink')
	#e3.grid(row=29,column=1,sticky=W)
	ButtonCheck1(self.frame,self,0,'  OK  ')
        ButtonCheck1(self.frame,self,1,'Cancel')    
	e1['textvariable']=user
	e2['textvariable']=timer
	#e3['textvariable']=numJob
	self.top.grab_set()
	self.top.focus_set()
	self.top.wait_window()

    def check(self):
	users=s1.get()
	if users != 'all' and users!="None":
	    passwd=os.popen("ypcat -k passwd.byname|awk '{print $1}'").readlines()
	    for name in string.split(users):
		if name+'\n' not in passwd:
		    tkMessageBox.showwarning('Unkown user'+CLUSTER,'User '+name+' is not valid')
		    return 1
	timer=s2.get()
	try:
	    if string.atoi(timer) < 5 and string.atoi(timer)>0:
		tkMessageBox.showwarning('High Load'+CLUSTER,'Update in '+timer+\
			       ' sec is not allowed')
		return 1
	except:
	    tkMessageBox.showwarning('Wrong entry'+CLUSTER,'Update value should be time in seconds')
	    return 1
	num=s3.get()
	if num=="None":
	    return 0
	try:
	    string.atoi(num)
	except:
	    tkMessageBox.showwarning('Wrong entry'+CLUSTER,'Invalid value for number of lines to display')
	    return 1    
	return 0
#******************************************************************


#******************************************************************
class DisplayTmp(Screen):
    def __init__(self,label,info,title,master=None,pref=None):
        Screen.__init__(self,master,title,info,label,'top',pref)
    def menubar(self):
        f1=Frame(self.top)
        f1.pack(side=BOTTOM,fill=X)        
	ButtonQuit(f1,self.top,'OK','bottom','center','y')
#*****************************************************************
