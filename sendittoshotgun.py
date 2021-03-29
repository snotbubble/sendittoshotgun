# direct shotgun publish script
# by c.p.brown 2014~2018
#
# shotgun should NOT be installed, just grab its 'api' (directory of scripts)
# 
# dependencies - download/make these in a dir called 'sg'
# ./sendittoshotgun.py			: this script
# ./res/python/shotgun_api3		: shotgun api (as of 2018)
# ./res/ffmpeg/bin			: ffmpeg binaries and resources (can be overridden)
# ./res/icons/your_48x48_watermark.png	: watermark for lower right of movies (can be overridden)
# ./res/fonts/EnvyCode-R.ttf		: font for overlay (can be overridden)
# 
# usage
# python sendittoshotgun.py "projectname" "sequencename" "shotname" "taskname" "versionname" "username" "fullimagepath" "comment" "fps"
#
# build this command in a nuke or houdini shelftool, select read-nodes or file-cops, hit the button, keep working...
# a sample shelftool should be where you found this script
#
# minimal dir compliance 
# /skullet/GX1/intro/2/anim/then/whatever/the/hell/you/like
#           |     |  |   |
#           |     |  |   +--- taskname
#           |     |  +------- shotname
#           |     +---------- sequencename
#           +---------------- projectname
#
# arg sources - there should be ZERO data entry - its the whole point of this excercise
# [01] # projectname.............. get from path of file
# [02] # username................. get from OS, must match shotgun username!
# [03] # sequencename............. get from path of file
# [04] # shotname................. get from path of file
# [05] # taskname................. get from path of file
# [06] # versionname.............. required, can be anything, build automatically, dont' ask user
# [07] # versioncomment (optional) can be anything, build automatically, don't ask user by default; make a special shelftool for special people
# [08] # 1stframeofrender......... get from 1st frame of sequence
# [09] # pathtoshotgunapi......... from shotgun_api3 import shotgun
# [10] # pathtoffmpeg............. optional ffmpeg override, eg: /server/tools/ffmpeg/bin/
# [11] # pathtowatermark.......... optional watermark override, must be a .png with alpha
# [12] # pathtofont............... optional watermark font override, must be ttf, used for shot info overlay strip
#
# the srcipt and dependencies are encapsulated within one dir, so it can be copied and used offsite
# to save xfer size, have offsite peeps install python and ffmpeg locally, however this may introduce errors, especially with ffmpeg
#
# NOTE:
# this script is probably incompatible with the latest ffmpeg and shotgun_api
# use for reference only
# also probably won't work on windows.

import os
import sys
import subprocess
import shutil
import glob
import platform
from datetime import datetime


pn = sys.argv[1] # project name
qn = sys.argv[2] # sequence name
sn = sys.argv[3] # shot name
tn = sys.argv[4] # task name
vn = sys.argv[5] # version name
un = sys.argv[6] # user name
r = sys.argv[7]  # 1st frame of render
vc = sys.argv[8] # version comment (required, but can be blank)
fs = sys.argv[9] # fps
# sys.argv[10] is an optional ffmpeg override
# sys.argv[11] is an optional watermark override
# sys.argv[12] is an optional watermark font override

def padz(s,p,l) : 
	dif = (l - len(s)) + 1
	o = ''
	for i in range(1,dif) : o = o + p
	o = o + s
	return o

dn = datetime.now()
dstr = (str(dn.year)[-2:] + padz(str(dn.month),'0',2) + padz(str(dn.day),'0',2))

# this probably won't work in windows... sucks you to be on windows
locsg = "./res/"

# import shotgun api :
pyp = locsg + "python"
sys.path.append(pyp)
from shotgun_api3 import Shotgun

# check it
print 'sys.argv[0] = %s' % sys.argv[0]
print 'sys.argv[1] = %s' % sys.argv[1]
print 'sys.argv[2] = %s' % sys.argv[2]
print 'sys.argv[3] = %s' % sys.argv[3]
print 'sys.argv[4] = %s' % sys.argv[4]
print 'sys.argv[5] = %s' % sys.argv[5]
print 'sys.argv[6] = %s' % sys.argv[6]
print 'sys.argv[7] = %s' % sys.argv[7]
print 'sys.argv[8] = %s' % sys.argv[8]
print 'sys.argv[9] = %s' % sys.argv[9]

# default to 24fps if its missing
if fs == '' : fs = '24'

fexe = locsg + "ffmpeg/bin/ffmpeg.exe"
fpro = locsg + "ffmpeg/bin/ffprobe.exe"

if platform.system() == 'Linux' :
	fexe = locsg + "ffmpeg/bin/ffmpeg"
	fpro = locsg + "ffmpeg/bin/ffprobe"

if len(sys.argv) > 10 :
	if os.path.exists(sys.argv[10]) :
		print "ffmpeg override supplied"
		fexe = sys.argv[10]
		fpro = os.path.dirname(sys.argv[10]) + '/ffprobe.exe'
		if platform.system() == 'Linux' :
			fpro = os.path.dirname(sys.argv[10]) + '/ffprobe'
		print '\tsys.argv[10] = %s' % sys.argv[10]
	

wm = locsg + "icons/your_48x48_watermark.png"

if len(sys.argv) > 11 :
	if os.path.exists(sys.argv[11]) :
		print "watermark override supplied"
		wm = sys.argv[11]
		print '\tsys.argv[11] = %s' % sys.argv[11]

wmfont = locsg + "fonts/EnvyCode-R.ttf"

if len(sys.argv) > 12 :
	if os.path.exists(sys.argv[12]) :
		print "watermark font supplied"
		wmfont = sys.argv[12]
		print '\tsys.argv[12] = %s' % sys.argv[12]
	else :
		print "watermark font not supplied, using default"

wmfont = wmfont.replace("\\","/")
wmfont = wmfont.replace(":","\\:")

# [TODO] opt-out of watermarking
watermarkit = 1

# python scripts have zero security, so not even bothering to hide this info
# use NDAs, change api keys frequently

SERVER_PATH = "https://yourdomain.shotgunstudio.com"
SCRIPT_NAME = 'myfistyourface'
SCRIPT_KEY = 'this_scripts_api_key'
sg = Shotgun(SERVER_PATH, SCRIPT_NAME, SCRIPT_KEY)
#sg = 1

if sg != None :
#make the mp4:
	rparts = r.split('.')
	#print "r = %s" % r
	# is it a sequence: path/name.####.ext ?
	if len(rparts) == 3 :
		rnums = rparts[len(rparts)-2]
		print "getting 1st frame num..."
		globie = rparts[0] + '*' + rparts[2]
		sq = glob.glob(globie)
		#sq.sort
		sq.sort(key=lambda x: x.lower())
		sqp = sq[0].split('.')
		sqnums = sqp[len(sqp)-2]
		startnum = int(sqnums)
		print "1st frame num = %s" % startnum       
		rs = rparts[0] + ('.'+'%0'+str(len(rnums))+'d.') + rparts[2]
		rvid = rparts[0] + '.mp4'
		
# get optional lut files from version comments
		vfcubes = ""
		if vc != "" :
			vct = ""
			vcln = vc.decode("string_escape").splitlines()
			print "vcln = %s" % vcln
			for vl in vcln :
				vlt = vl
				print "\t\tchecking comment line for lookup path: %s" % vl
				vp = vl.split('.cube')
				if len(vp) > 1 :
					if os.path.exists(vl) :
						wvl = vl.replace('\\','/')
						wvl = wvl.replace(':','\\:')
						vfcubes = vfcubes + 'lut3d=\'' + wvl + '\', '
						vlt = ''
				vct = vct + vlt + '\n'
			vc = vct
		#vfcubes = vfcubes.strip(', ')
				
		fcmd = "\"" + fexe + "\" -r " + fs + " -thread_queue_size 512 -start_number " + str(startnum) + " -i \"" + rs + "\" -filter_complex \"" + vfcubes + "scale=trunc(in_w/2)*2:trunc(in_h/2)*2\" -pix_fmt yuv420p -vcodec h264 -g 30 -b:v 2000k -vprofile high -bf 0 -y \""+ rvid + "\""
		if watermarkit == 1 : 
			imgn = os.path.basename(sys.argv[7]).split('.')[0]
			probe = fpro + " -i " + r + " -v error -of flat=s=_ -select_streams v:0 -show_entries stream=width,height"
			print "probing the image : %s" % probe
			ffs = "18"

			fpret = subprocess.Popen(probe, stdout=subprocess.PIPE, shell=True)
			probed = fpret.communicate()[0]
			print "probe returns : %s" % probed
			if '=' in probed :
				wmtxt = dstr + " | " + pn + " | SEQ=" + qn + " | SHOT=" + sn + " | " + imgn + " | "
				wmtxtlen = len(wmtxt) + 6
				tiw = wmtxtlen * 10
				print "estimated text width : %s" % tiw
				iw = int(probed.split('\n')[0].split('=')[1].strip())
				#iw = max(iw,int(tiw))
				iwf = int((iw / max(1000.0,float(tiw))) * 18)
				ffs = str(iwf)
				fbh = int(25.0 * (iwf / 18.0)) + 20
				ih = str(int(probed.split('\n')[1].split('=')[1].strip())-fbh)
				probe = fpro + " -i " + r + " -v error -of flat=s=_ -select_streams v:0 -show_entries stream=sample_aspect_ratio"
				print "probing it again : %s" % probe
				fpret = subprocess.Popen(probe, stdout=subprocess.PIPE, shell=True)
				probed = fpret.communicate()[0]
				print "probe returns : %s" % probed
				forcesar = '[0:v]'
				if '=' in probed :
					ia = probed.split('\n')[0].split('=')[1].strip()
					print "found sample aspect : %s" % ia
					if ia != '' and len(ia.split(':')) > 1 :
						forcesar = ('setsar=' + ia + ', ')
				fcmd = "\"" + fexe + "\" -r " + fs + " -thread_queue_size 512 -start_number " + str(startnum) + " -i \"" + rs + "\" -i \"" + wm + "\" -filter_complex \"[0:v]" + forcesar + vfcubes + "scale=trunc(in_w/2)*2:trunc(in_h/2)*2[scale];[scale][1:v]overlay=x=(main_w-overlay_w)-20:y=(main_h-overlay_h)-(" + str(fbh) + "+15),drawbox=y=" + ih + ":color=black@0.3:width=" + str(iw) + ":height=" + str(fbh) + ":t=max,drawtext=fontfile='" + wmfont + "': text=\'" + dstr + " | " + pn + " | SEQ=" + qn + " | SHOT=" + sn + " | " + imgn + " | " + "f %{eif\\:n+1\\:d}\': fontcolor=white@0.5: fontsize=" + ffs + ": x=10: y=(main_h-text_h)-10\" -pix_fmt yuv420p -vcodec h264 -g 30 -b:v 2000k -vprofile high -bf 0 -y \""+ rvid + "\""
		#print '\n'
		print "fcmd = %s" % fcmd
		fret = subprocess.call(fcmd, shell = True)
		fret = 1
		if fret == 0 :
# shotgun...
# override username for offsite testing:
			#un = "cpb"
			filters = [ ['name','is',pn], ]
			p = sg.find_one('Project',filters)
			if p != None :
				pid = p['id']
				#print "local login user is %s" % un
				filters = [ ['name','is', un], ]
				u = sg.find_one('HumanUser',filters)
				if u != None :
					uid = u['id']
					#print "user = %s, sg_humanuser = %s, sg_uid = %s" % (un, u, uid)
					filters = [ ['project','is', {'type':'Project','id':pid}],['code', 'is', qn] ]
					q = sg.find_one('Sequence',filters)
					if q != None :
						filters = [ ['project','is', {'type':'Project','id':pid}],['code', 'is', sn] ]
						s = sg.find_one('Shot',filters)
						if s != None :
							sid = s['id']
							filters = [ ['project','is', {'type':'Project','id':pid}],['entity','is',{'type':'Shot','id':sid}],['content','is',tn] ]
							t = sg.find_one('Task',filters)
							if t != None :
								tid = t['id']
								data = { 'project': {'type':'Project','id':pid},'code': (sn+'_'+tn+'_'+vn),'description': vc,'created_by': {'type':'HumanUser', 'id':uid},'sg_path_to_frames': os.path.dirname(r),'sg_status_list': 'rev','entity': {'type':'Shot', 'id':sid},'sg_task': {'type':'Task', 'id':tid},'user': {'type':'HumanUser', 'id':uid} }
								v = sg.create('Version', data)
								if v != None :
									vid = v['id']
									rps = r.split('/')
									# ---------- drive -------- shotgun ------ project ------ scene -------- shot --------- task --------- review
									reviewpath = rps[0] + '/' + rps[1] + '/' + rps[2] + '/' + rps[3] + '/' + rps[4] + '/' + rps[5] + '/' + "review" + '/'
									if not os.path.exists(reviewpath) :
										os.mkdir(reviewpath)
									reviewvid = reviewpath + os.path.basename(rvid)
									shutil.copy2(rvid,reviewvid)
									sg.upload_thumbnail("Version", vid, r)
									sg.upload("Version", vid,reviewvid,'sg_uploaded_movie')
								else : print "error: couldn't create new version: %s" % vn
							else : print "error: can't find task: %s" % tn
						else : print "error: can't find shot: %s" % sn
					else : print "error: can't find sequence: %s" % qn
				else : print "error: user %s isn't in shotgun" % un
			else : print "error: can't find project: %s" % pn
		else : print "error: couldn't make the mp4: %s" % rvid
	else : print "error: unhandled file format, expecting: name.nums.ext"
else : print "error: couldn't connect to shotgun"
