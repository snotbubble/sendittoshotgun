import os
import getpass
from datetime import datetime
import platform
import imp
import sys
import subprocess
import shutil
import glob

def padz(s,p,l) : 
	dif = (l - len(s)) + 1
	o = ''
	for i in range(1,dif) : o = o + p
	o = o + s
	return o

dn = datetime.now()
dstr = (str(dn.year)[-2:] + padz(str(dn.month),'0',2) + padz(str(dn.day),'0',2))

locsg = "/path/to/sg"

def sendittoshotgun(project, sequence, shot, task, user, render, version, comment, fps, ffmpeg, water, wfont):
	if project != '' and shot != '' and sequence != '' and task != '' and user != '' :
		pyx = locsg + "python/python"
		sgpy = locsg + "sendittoshotgun.py"
		qo = "\""
		cmd = qo + sgpy + qo + ' ' + qo + project  + qo + ' ' + qo + sequence + qo + ' ' + qo + shot + qo + ' ' + qo + task + qo + ' ' + qo + version + qo + ' ' + qo + user + qo + ' ' + qo + render + qo + ' ' + qo + comment + qo + ' ' + qo + fps + qo + ' ' + qo + ffmpeg + qo + ' ' + qo + water + qo + ' ' + qo + wfont + qo
		return [pyx,cmd]    
	

hdir = hou.hipFile.path()
hname = hou.hipFile.basename()
hp = hdir.split('/')

print('hdir='+hdir)

# quick test of hipfile location:
if len(hp) > 3 :

# vars for this scene    
	
		pn = hp[2]
		qn = hp[3]
		sn = hp[4]
		tn = hp[5]
		thisdir = os.path.dirname(hdir).split('/')[-1]
		thisfile = hou.hipFile.name().split('.')[0].split('/')[-1]
		un=getpass.getuser()
 
		print("project== "+pn)
		print("sequence= "+qn)
		print("shot===== "+sn)
		print("task===== "+tn)
		print("thisdir== "+thisdir)
		print("thisfile= "+thisfile)
		print("user===== "+un)             
		
		r = ''
		version = ''
		comment = ''

		ops = hou.selectedNodes()
		
# loop through each node:  

		for i in ops:
			otn = i.type().name()
			if otn == 'file' :
				version = (dstr + '_' + thisdir + '_' + thisfile + '_' + i.name())
				r = i.parm('filename1').eval()
				comment = (dstr + ': another great update from ' + un + ' via Houdini')
				print("r======== "+r)  
				print("version== "+version)  
				print("comment== "+comment)  
				print('\n')
				fps = str(hou.fps())
#send it:
				sgcmds = sendittoshotgun(pn, qn, sn, tn, un, r, version, comment, fps, "", "", "")
				print "shotgun command: %s" % sgcmds
				sgcmd = (sgcmds[0] + ' ' + sgcmds[1])
				subprocess.call(sgcmd, shell = True)              
		
		
		
