#@(#)$Id: GuiFipc.py,v 1.10 1999/12/10 16:35:54 tlevshin Exp $
#@(#)$Author: tlevshin $
#@(#)$Log: GuiFipc.py,v $
#@(#)Revision 1.10  1999/12/10 16:35:54  tlevshin
#@(#)catch the exception from pwd.
#@(#)
#@(#)Revision 1.9  1999/12/03 21:30:26  tlevshin
#@(#)fix checkProt (before I assumed that protection has three fields owner,group
#@(#),others)
#@(#)
#@(#)Revision 1.8  1999/12/03 18:15:41  tlevshin
#@(#)fix permission problem
#@(#)
#@(#)Revision 1.7  1999/11/11 22:31:17  tlevshin
#@(#)add display to List
#@(#)
#@(#)Revision 1.6  1999/11/11 21:46:14  tlevshin
#@(#)change Base to Lib
#@(#)
#@(#)Revision 1.5  1999/11/11 21:20:48  tlevshin
#@(#)added List
#@(#)
#@(#)Revision 1.4  1999/11/10 21:51:28  tlevshin
#@(#)fix multiple selection
#@(#)
#@(#)Revision 1.3  1999/11/09 22:08:52  tlevshin
#@(#)add SetValue for Flag and Variable
#@(#)Clean,CleanAll etc
#@(#)
#@(#)Revision 1.2  1999/11/09 17:06:38  tlevshin
#@(#)do not dipslay error if trying to select from empty screen
#@(#)
#@(#)Revision 1.1  1999/11/08 17:34:44  tlevshin
#@(#)Gui for FIPC (GuiBase - FBS common widgets)
#@(#)

from GuiLib import *

import fipc_api 
import pwd
import grp
import string

#****************************************
class ButtonHelp(ButtonBase):
    def __init__(self,frame,name):
	ButtonBase.__init__(self,frame,name)
	self.frame=frame
    def action(self):
	Help(self.frame,self.frame.pref)
#****************************************

#****************************************
class ButtonExit(ButtonBase):
    def __init__(self,frame,name):
	ButtonBase.__init__(self,frame,name)
	self.frame=frame
    def action(self):
	self.frame.destroyAll()	
#****************************************
class ButtonGlobPref(ButtonBase):
    def __init__(self,frame,name):
	ButtonBase.__init__(self,frame,name)
	self.frame=frame
    def action(self):
	self.frame.pref.getPref()
#****************************************

#****************************************

class ButtonMod(ButtonBase):
    def __init__(self,frame,top,name,command):
	ButtonBase.__init__(self,frame,name)
	self.top=top
	self.cmd=command

    def action(self):
	self.top.modify(self.cmd)
#****************************************
class ButtonCreate(ButtonBase):
    def __init__(self,frame,top,name):
	ButtonBase.__init__(self,frame,name)
	self.top=top
    def action(self):
	self.top.create()
#****************************************

class ButtonDisp(ButtonBase):
    def __init__(self,frame,top,name):
	ButtonBase.__init__(self,frame,name)
	self.top=top
    def action(self):
	self.top.detail()
#****************************************

class Object(Screen):
    def __init__(self,master,fc,title,type,pref):
	self.user=pwd.getpwuid(os.getuid())[0]
	self.fc=fc
	self.title=title
	self.type=type
	Screen.__init__(self,master,self.title,None,None,'bottom',pref)
	
    def menubar(self):
	fr=Frame(self.top)
	fr.pack(side=BOTTOM,fill=X)
	if self.type in [fipc_api.FIPC_TYPE_LOCK,fipc_api.FIPC_TYPE_QUEUE,\
			 fipc_api.FIPC_TYPE_GATE,fipc_api.FIPC_TYPE_LIST]:
	    ButtonMod(fr,self,'Display','display')
	ButtonCreate(fr,self,'Create')
	if  self.type in [fipc_api.FIPC_TYPE_FLAG,fipc_api.FIPC_TYPE_VARIABLE]:
	    ButtonMod(fr,self,"SetValue",'setVal')
	if  self.type in [fipc_api.FIPC_TYPE_LIST]:
	    ButtonMod(fr,self,"AddItem",'setVal')
	ButtonMod(fr,self,'Destroy','destroy')
	if self.type in [fipc_api.FIPC_TYPE_LIST]:
	    ButtonMod(fr,self,"RmvFirstItem",'remF')
	    ButtonMod(fr,self,"RmvLastItem",'remL')
	    ButtonMod(fr,self,'Clean','clean')
	if self.type in [fipc_api.FIPC_TYPE_LOCK,fipc_api.FIPC_TYPE_QUEUE,\
			 fipc_api.FIPC_TYPE_GATE]:
	    ButtonMod(fr,self,'Clean','clean')
	    ButtonMod(fr,self,'CleanAll','cleanall')
	ButtonPref(fr,self,'Preference')
	ButtonPrint(fr,self,'Print')
	ButtonSave(fr,self,'Save')
	ButtonQuit(fr,self.top,'Quit')	
    def create(self):
	title="Create "+self.title[:-1]
	CreateObject(self.frame,title,self.fc,self.type,self.pref)
    def modify(self,cmd):
	if self.list.reply==None:
	    tkMessageBox.showinfo('Not selected'+getCluster(),"You did not select the line")
	    return	    
	for reply in self.list.reply:
	    if not len(reply):
		continue
	    info=[]
	    path=string.split(reply)[0]
	    try:
	    	ob=self.fc.objects(path=path,types=self.type)[0]
	    except:
		return
	    idL=[]
	    l=ob.get()
	    if type(l)==type(idL):
		idL=l
	    else:
		if l!='_':
		    idL.append(l)	    
	    
	    if cmd == 'display':
	        if self.checkProt(ob,'r'):
		    continue
	        label=("Name","Status")
	        forInfo=[]
		if self.type==fipc_api.FIPC_TYPE_LIST:
			label=("Name","")
		for id in idL:
		    	status=" "
			if self.type !=fipc_api.FIPC_TYPE_LIST:
		    		if id=="_":
					id="empty"
		    		else:
		    			if self.fc.isAlive(id):
						status="Alive"
					else:
						status="Dead"
		    	info.append((id,status))
		if not len(info):
		    forInfo.append("The "+self.title[:-1]+" is empty")
		    label=""
		else:
		    forInfo,label=infoFormat(info,label)
		DisplayTmp(label,forInfo,self.title[:-1]+" Info:"+ob.Path ,self.top,self.pref)  
		continue
	    if self.checkProt(ob,'x'):
		continue
	    if cmd=='setVal':
		title="SetValue "+self.title[:-1]
		SetVal(self.frame,title,ob,self.type,self.pref)
	    elif cmd=='remF':
		ob.remFirst()
	    elif  cmd=='remL':
		ob.remLast()
	    elif cmd=='clean':
		print ob.clean()
	    elif cmd=='cleanall':
		aL=[]
		if len(idL):
		    for id in idL:
			if self.fc.isAlive(id):
			    aL.append(id)
		    if len(aL):
			if not tkMessageBox.askokcancel('Clean the '+self.title[:-1]+getCluster(),\
				   "Do you really want to clean the "+self.title[:-1]+repr(aL)):
			    return
		    print ob.clean(force=1)
	    elif cmd=='destroy':
		if self.type in [fipc_api.FIPC_TYPE_LOCK,fipc_api.FIPC_TYPE_QUEUE,\
			 fipc_api.FIPC_TYPE_GATE]:
			aL=[]
			if len(idL):
		    		for id in idL:
					if self.fc.isAlive(id):
			    			aL.append(id)
		    	if len(aL):
				if not tkMessageBox.askokcancel('Not empty'+getCluster(),\
				   "The FIPC object is not " +self.title[:-1]+" empty:"+repr(aL)+\
						       "Do you want to remove it?"):
			    		return
		ob.destroy()
    def checkProt(self,ob,p):
	if ob.Uid!=os.getuid():
		if ob.Prot[1]=='x':
			return 0
        	if ob.Prot[1]!=p:
		    tkMessageBox.showwarning('Protection vialation',\
				       'You do not have permission to perform this action!')
		    return 1
	return 0

    def  get_info(self):
	userL=self.getUser()
	obL=self.fc.objects(path="",types=self.type)
	self.info=[]
	info=[]
	label=""
	for ob in obL:
	    if self.type in [fipc_api.FIPC_TYPE_VARIABLE,fipc_api.FIPC_TYPE_FLAG,\
			 fipc_api.FIPC_TYPE_LOCK]:
		val=ob.get()
		if type(val)!=type(""):
			val=repr(val)
		label=("Name","Owner","Group","Protection","Value")
		tup=(val,)
	    elif self.type in [fipc_api.FIPC_TYPE_GATE]:
		label=("Name","Owner","Group","Protection","Room_Size","Free")
		idL=ob.get()
		free=0
		for id in idL:
			if id=="_":
				free=free+1
		tup=(repr(len(idL)),repr(free))
	    elif  self.type in [fipc_api.FIPC_TYPE_QUEUE] :
		label=("Name","Owner","Group","Protection","#Clients")
	    	tup=(repr(len(ob.get())),)
	    elif self.type in [fipc_api.FIPC_TYPE_LIST]:
		label=("Name","Owner","Group","Protection","#Items")
		tup=(repr(len(ob.get())),)
	        	
	    try:
		    user=pwd.getpwuid(ob.Uid)[0]
	    except:
		    user=repr(ob.Uid)	
	    if ob.Reason:
		tmp=""
		for i in range(0,len(ob.Reason)):
			if ob.Reason[i]==" ":ch="_"
			else: ch=ob.Reason[i]
			tmp=tmp+ch
		ob.Reason=tmp
	    else:
		ob.Reason=None
	    if ob.Reason:
		label=label+("Reason")
		tup=tup+(repr(ob.Reason),)
	     
	    if user in userL or "all" in userL:
		tup=(ob.Path,pwd.getpwuid(ob.Uid)[0],grp.getgrgid(ob.Gid)[0],ob.Prot)+tup
	    	info.append(tup)
	self.info,self.label=infoFormat(info,label)

    def getUser(self):
	if self.pref==None:
	    if self.user=='root':
		user=['all']
	    else:
		user=[self.user]
	else:	
	    if self.pref.userL=='all':
		user=['all']
	    else:	
		user=string.split(self.pref.userL)
	return user
class SetVal:
    def __init__(self,master,title,ob,type,pref):
	self.master=master
	self.title=title
	self.type=type
	self.cancel=1
	self.val=ob.get()
	self.place=None
	if self.type==fipc_api.FIPC_TYPE_LIST:
	    self.place="append"
	    self.val=""
	self.ob=ob
	self.getObject()
    def getObject(self):
	global s1,s2
	s1=StringVar()
	s1.set(self.val)
	s2=StringVar()
	s2.set(self.place)
	self.setObject(s1,s2)
	if not self.cancel:
	    return
	self.val=s1.get()
	if self.type==fipc_api.FIPC_TYPE_VARIABLE:
	    self.ob.set(self.val)
	elif self.type==fipc_api.FIPC_TYPE_FLAG:
	    self.ob.set(setop = "=", setarg =string.atoi(self.val))
	elif self.type==fipc_api.FIPC_TYPE_LIST:
	    self.place=s2.get()
	    if self.place=='append':
		self.ob.append(self.val)
	    else:
		self.ob.prepend(self.val)
    def setObject(self,val,place):
	self.top = Toplevel(self.master)
	self.top.title(self.title)
	self.frame=Frame(self.top)
	self.frame.pack(side='left',expand=YES,fill=BOTH)
	f1=Frame(self.top)
	f1.pack(anchor=E,expand=YES,fill=X)
	txt="Value"
	Label(f1,text=txt,background='white',foreground='black').pack\
					(side=TOP,anchor=W)
	e2=Entry(f1,textvariable=val, relief=SUNKEN,background='pink',width=20)
	e2.pack(side=RIGHT,expand=YES,fill=X)
	e2['textvariable']=val
	if self.type==fipc_api.FIPC_TYPE_LIST:
	    f2=Frame(self.top)
	    f2.pack(anchor=E,expand=YES,fill=X)
	    Label(f2,text='AddItem',background='white',foreground='black').pack\
			    (side=TOP,anchor=W)	
	    r1=Radiobutton(f2,text="append",variable=place,value="append",
		       anchor=W)
	    r1.pack(fill=X)
	    r2=Radiobutton(f2,text="prepend",variable=place,\
		       value="prepend",anchor=W)
	    r2.pack(fill=X)
	ButtonCheck(self.top,self,0,'OK','left')
	ButtonCheck(self.top,self,1,'Cancel','right')
	self.top.grab_set()
	self.top.focus_set()
	self.top.wait_window()
    def check(self):
	val=s1.get()
	if self.type==fipc_api.FIPC_TYPE_FLAG:
	    try:
                             in_val=string.atoi(val)
	    except:
		tkMessageBox.showwarning('Wrong type','Initial value should be an integer')
		return 1
	return 0





class CreateObject:
    def __init__(self,master,title,fc,type,pref):
	self.fc=fc
	self.master=master
	self.title=title
	self.type=type
	self.cancel=1
	self.path=""
	self.protO="r"
	self.protG="x"
	self.extra=""
	self.getObject()
    def setObject(self,path,protO,protG,extra):
	self.top = Toplevel(self.master)
	self.top.title(self.title)
	self.frame=Frame(self.top)
	self.frame.pack(side='left',expand=YES,fill=BOTH)
	f1=Frame(self.top)
	f1.pack(anchor=E,expand=YES,fill=X)
	Label(f1,text='Name',background='white',foreground='black').pack\
			    (side=TOP,anchor=W)
	e1=Entry(f1,textvariable=path, relief=SUNKEN,
		 background='pink',width=20)
	e1.pack(side=RIGHT,expand=YES,fill=X)

	f2=Frame(self.top)
	f2.pack(anchor=E,expand=YES,fill=X)
	Label(f2,text=self.title+' Protection',background='white',foreground='black').pack\
			    (side=TOP,anchor=W)
	Label(f2,text='Group',background='white',foreground='black').pack\
			    (side=TOP,anchor=W)	
	r1=Radiobutton(f2,text="no access",variable=protO,value="-",
		       anchor=W)
	r1.pack(fill=X)
	r2=Radiobutton(f2,text="read only",variable=protO,\
		       value="r",anchor=W)
	r2.pack(fill=X)
	r3=Radiobutton(f2,text="read,modify,delete",variable=protO,\
		       value="x",anchor=W)
	r3.pack(fill=X)	
	
	Label(f2,text='Other',background='white',foreground='black').pack\
			    (side=TOP,anchor=W)	
	r4=Radiobutton(f2,text="no access",variable=protG,value="-",
		       anchor=W)
	r4.pack(fill=X)
	r5=Radiobutton(f2,text="read only",variable=protG,\
		       value="r",anchor=W)
	r5.pack(fill=X)
	r6=Radiobutton(f2,text="read,modify,delete",variable=protG,\
		       value="x",anchor=W)
	r6.pack(fill=X)
	e1['textvariable']=path
	if self.type in [fipc_api.FIPC_TYPE_GATE,fipc_api.FIPC_TYPE_VARIABLE,\
			 fipc_api.FIPC_TYPE_FLAG,fipc_api.FIPC_TYPE_LIST]:
	    f3=Frame(self.top)
	    f3.pack(anchor=E,expand=YES,fill=X)
	    txt="Initial Value"
	    if self.type==fipc_api.FIPC_TYPE_GATE: txt='Room'
	    Label(f3,text=txt,background='white',foreground='black').pack\
				      (side=TOP,anchor=W)
	    e2=Entry(f3,textvariable=extra, relief=SUNKEN,
		 background='pink',width=20)
	    e2.pack(side=RIGHT,expand=YES,fill=X)
	    e2['textvariable']=extra
	ButtonCheck(self.top,self,0,'OK','left')
	ButtonCheck(self.top,self,1,'Cancel','right')    


	self.top.grab_set()
	self.top.focus_set()
	self.top.wait_window()

    def getObject(self):
	global s1,s2,s3,s4
	s1,s2,s3,s4=StringVar(),StringVar(),StringVar(),StringVar()
	s1.set(self.path)
	s2.set(self.protG)
	s3.set(self.protO)
	s4.set(self.extra)
	self.setObject(s1,s2,s3,s4)
	if not self.cancel:
	    return
	self.path=s1.get()
	self.protG=s2.get()
	self.protO=s3.get()	  
	self.extra=s4.get()
	if self.type==fipc_api.FIPC_TYPE_QUEUE:
	    ob=fipc_api.Queue(self.fc,path=self.path,prot=self.protG+self.protO)
	elif self.type==fipc_api.FIPC_TYPE_LOCK:
	    ob=fipc_api.Lock(self.fc,path=self.path,prot=self.protG+self.protO)
	elif self.type==fipc_api.FIPC_TYPE_GATE:
	    ob=fipc_api.Gate(self.fc,path=self.path,room=string.atoi(self.extra),\
			     prot=self.protG+self.protO)
	elif self.type==fipc_api.FIPC_TYPE_VARIABLE:
	    ob=fipc_api.StringVar(self.fc,path=self.path,init_val=self.extra,\
				  prot=self.protG+self.protO)
	elif self.type==fipc_api.FIPC_TYPE_FLAG:
	    ob=fipc_api.IntFlag(self.fc,path=self.path,init_val=string.atoi(self.extra),\
				prot=self.protG+self.protO)
	elif self.type==fipc_api.FIPC_TYPE_LIST:
	    ob=fipc_api.List(self.fc,path=self.path,init=string.splitfields(self.extra,','),\
			     prot=self.protG+self.protO)
    def check(self):
	path=s1.get()
	extra=s4.get()
	if self.type==fipc_api.FIPC_TYPE_GATE:
	    if extra=="":
		tkMessageBox.showwarning('Undefined parameter','Please, enter # of rooms per gate')
		return 1
	    try:
		string.atoi(extra)
	    except:
		tkMessageBox.showwarning('Wrong type','# of rooms per gate should be an integer')
		return 1
	if self.type==fipc_api.FIPC_TYPE_FLAG:
		try:
			in_val=string.atoi(extra)
		except:
			tkMessageBox.showwarning('Wrong type','Initial value should be an integer')	
			return 1
	if self.type==fipc_api.FIPC_TYPE_LIST:
		try:
			init=string.splitfields(extra,'.')
		except:
			tkMessageBox.showwarning('Wrong type','Initial Item should be separated by comma')	
			return 1
	if not len(path):
		tkMessageBox.showwarning('No name','Please, enter '+self.title[:-1]+'  name')
		return 0

	return 0
#********************************************	
class Help(Screen):
    def __init__(self,master,pref):
	self.dir=os.environ["FIPC_DIR"]+"/man/cat1/"
	Screen.__init__(self,master,"HELP",None,None,'bottom',pref)

    def menubar(self):
	f1=Frame(self.top)
	f1.pack(side=TOP,fill=X)
	ButtonDisp(f1,self,'Display')
	ButtonPref(f1,self,'Preference')
	ButtonPrint(f1,self,'Print')
	ButtonSave(f1,self,'Save')
	ButtonQuit(f1,self.top,'Quit')

    def get_info(self):
	try:
		line=open(self.dir+'index','r').readlines()
	except:
		line=[]
	self.label="            Index              "
	self.info=[]
	for text in line:
		self.info.append(text[:-1])

    def detail(self):
	info=[]
	if self.list.reply==None:
	    tkMessageBox.showinfo('Not selected'+getCluster(),"You did not select the line")
	    return
	for reply in self.list.reply:
	    helpid=string.strip(reply)
	    try:
		open(self.dir+helpid+'.1')
	    except:
		tkMessageBox.showinfo('Not ready'+getCluster(),\
				      "Sorry, man pages are not ready for "+helpid)
		return
	    cmd='xterm -T  '+helpid+' -fn '+repr(self.pref.font)+' -e less '+self.dir+helpid+'.1'
	    os.system(cmd)


#****************************************#****************************************

class MainMenu(Frame):
    def __init__(self,master):
	import pwd
	Frame.__init__(self,master)
	self.root=master
	self.obDict={"Queues":fipc_api.FIPC_TYPE_QUEUE,"Locks":fipc_api.FIPC_TYPE_LOCK,\
		     "Gates":fipc_api.FIPC_TYPE_GATE,"Flags":fipc_api.FIPC_TYPE_FLAG,\
		     "Variable":fipc_api.FIPC_TYPE_VARIABLE,"Lists":fipc_api.FIPC_TYPE_LIST}
	self.pack()
	self.winfo_toplevel().title("FIPC "+getCluster())
	self.pref=Preference(self,pwd.getpwuid(os.getuid())[0])
	self.fc=fipc_api.FIPCClient()
	self.dropmenu()
	self.root.protocol("WM_DELETE_WINDOW", self.destroyAll) 
	# delete all the Monitor windows if
                   #delete window "x" button is pressed
    def destroyAll(self):
	self.root.destroy()

    def dropmenu(self):
	f=MenubuttonBase(self,'FIPC OBJECTS')
	i=0
	for name in self.obDict.keys():
		f.menu.add_command(label=name,command=(lambda self=self,x=i:\
						       self.fipcOb(x)))
		i=i+1
	ButtonHelp(self,'HELP')
	ButtonGlobPref(self,'GLOBAL PREF')
	ButtonExit(self,'EXIT')
    def fipcOb(self,i):
	key=self.obDict.keys()[i]
	type=self.obDict[key]
	Object(self,self.fc,key,type,self.pref)
	

if __name__=="__main__": 
    root=Tk()
    mainMenu=MainMenu(root)  	
    root.mainloop()

