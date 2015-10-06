
import glob
import sys
import os
import types
import re
import traceback
import time
from subprocess import Popen

from catalyst.defaults import verbosity, valid_config_file_values

BASH_BINARY             = "/bin/bash"


def read_from_clst(path):
	line = ''
	myline = ''
	try:
		myf = open(path, "r")
	except Exception:
		return -1
		#raise CatalystError("Could not open file " + path)
	for line in myf.readlines():
		#line = line.replace("\n", "") # drop newline
		myline = myline + line
	myf.close()
	return myline


def list_bashify(mylist):
	if type(mylist)==types.StringType:
		mypack=[mylist]
	else:
		mypack=mylist[:]
	for x in range(0,len(mypack)):
		# surround args with quotes for passing to bash,
		# allows things like "<" to remain intact
		mypack[x]="'"+mypack[x]+"'"
	mypack = ' '.join(mypack)
	return mypack


class CatalystError(Exception):
	def __init__(self, message, print_traceback=False):
		if message:
			if print_traceback:
				(_type, value) = sys.exc_info()[:2]
				if value!=None:
					print
					print "Traceback values found.  listing..."
					print traceback.print_exc(file=sys.stdout)
			print
			print "!!! catalyst: "+message
			print


def die(msg=None):
	warn(msg)
	sys.exit(1)


def warn(msg):
	print "!!! catalyst: "+msg


def cmd(mycmd, myexc="", env=None, debug=False, fail_func=None):
	if env is None:
		env = {}
	#print "***** cmd()"
	sys.stdout.flush()
	args=[BASH_BINARY]
	if "BASH_ENV" not in env:
		env = env.copy()
		env["BASH_ENV"] = "/etc/spork/is/not/valid/profile.env"
	if debug:
		args.append("-x")
	args.append("-c")
	args.append(mycmd)

	if debug:
		print "***** cmd(); args =", args
	proc = Popen(args, env=env)
	if proc.wait() != 0:
		if fail_func:
			print "CMD(), NON-Zero command return.  Running fail_func()"
			fail_func()
		raise CatalystError("cmd() NON-zero return value from: %s" % myexc,
			print_traceback=False)


def file_check(filepath):
	'''Check for the files existence and that only one exists
	if others are found with various extensions
	'''
	if os.path.exists(filepath):
		return filepath
	# it didn't exist
	# so check if there are files of that name with an extension
	files = glob.glob("%s.*" % filepath)
	# remove any false positive files
	files = [x for x in files if not x.endswith(".CONTENTS") and not x.endswith(".DIGESTS")]
	if len(files) is 1:
		return files[0]
	elif len(files) > 1:
		msg = "Ambiguos Filename: %s\nPlease specify the correct extension as well" % filepath
		raise CatalystError(msg, print_traceback=False)
	raise CatalystError("File Not Found: %s" % filepath)


def file_locate(settings,filelist,expand=1):
	#if expand=1, non-absolute paths will be accepted and
	# expanded to os.getcwd()+"/"+localpath if file exists
	for myfile in filelist:
		if myfile not in settings:
			#filenames such as cdtar are optional, so we don't assume the variable is defined.
			pass
		else:
			if len(settings[myfile])==0:
				raise CatalystError("File variable \"" + myfile +
					"\" has a length of zero (not specified.)", print_traceback=True)
			if settings[myfile][0]=="/":
				if not os.path.exists(settings[myfile]):
					raise CatalystError("Cannot locate specified " + myfile +
						": " + settings[myfile], print_traceback=False)
			elif expand and os.path.exists(os.getcwd()+"/"+settings[myfile]):
				settings[myfile]=os.getcwd()+"/"+settings[myfile]
			else:
				raise CatalystError("Cannot locate specified " + myfile +
					": "+settings[myfile]+" (2nd try)" +
"""
Spec file format:

The spec file format is a very simple and easy-to-use format for storing data. Here's an example
file:

item1: value1
item2: foo bar oni
item3:
	meep
	bark
	gleep moop

This file would be interpreted as defining three items: item1, item2 and item3. item1 would contain
the string value "value1". Item2 would contain an ordered list [ "foo", "bar", "oni" ]. item3
would contain an ordered list as well: [ "meep", "bark", "gleep", "moop" ]. It's important to note
that the order of multiple-value items is preserved, but the order that the items themselves are
defined are not preserved. In other words, "foo", "bar", "oni" ordering is preserved but "item1"
"item2" "item3" ordering is not, as the item strings are stored in a dictionary (hash).
""",
					print_traceback=True)


def parse_makeconf(mylines):
	mymakeconf={}
	pos=0
	pat=re.compile("([0-9a-zA-Z_]*)=(.*)")
	while pos<len(mylines):
		if len(mylines[pos])<=1:
			#skip blanks
			pos += 1
			continue
		if mylines[pos][0] in ["#"," ","\t"]:
			#skip indented lines, comments
			pos += 1
			continue
		else:
			myline=mylines[pos]
			mobj=pat.match(myline)
			pos += 1
			if mobj.group(2):
				clean_string = re.sub(r"\"",r"",mobj.group(2))
				mymakeconf[mobj.group(1)]=clean_string
	return mymakeconf


def read_makeconf(mymakeconffile):
	if os.path.exists(mymakeconffile):
		try:
			try:
				import snakeoil.bash #import snakeoil.fileutils
				return snakeoil.bash.read_bash_dict(mymakeconffile, sourcing_command="source")
			except ImportError:
				try:
					import portage.util
					return portage.util.getconfig(mymakeconffile, tolerant=1, allow_sourcing=True)
				except Exception:
					try:
						import portage_util
						return portage_util.getconfig(mymakeconffile, tolerant=1, allow_sourcing=True)
					except ImportError:
						myf=open(mymakeconffile,"r")
						mylines=myf.readlines()
						myf.close()
						return parse_makeconf(mylines)
		except Exception:
			raise CatalystError("Could not parse make.conf file " +
				mymakeconffile, print_traceback=True)
	else:
		makeconf={}
		return makeconf


def msg(mymsg,verblevel=1):
	if verbosity>=verblevel:
		print mymsg


def pathcompare(path1,path2):
	# Change double slashes to slash
	path1 = re.sub(r"//",r"/",path1)
	path2 = re.sub(r"//",r"/",path2)
	# Removing ending slash
	path1 = re.sub("/$","",path1)
	path2 = re.sub("/$","",path2)

	if path1 == path2:
		return 1
	return 0


def ismount(path):
	"enhanced to handle bind mounts"
	if os.path.ismount(path):
		return 1
	a=os.popen("mount")
	mylines=a.readlines()
	a.close()
	for line in mylines:
		mysplit=line.split()
		if pathcompare(path,mysplit[2]):
			return 1
	return 0


def addl_arg_parse(myspec,addlargs,requiredspec,validspec):
	"helper function to help targets parse additional arguments"
	messages = []
	for x in addlargs.keys():
		if x not in validspec and x not in valid_config_file_values and x not in requiredspec:
			messages.append("Argument \""+x+"\" not recognized.")
		else:
			myspec[x]=addlargs[x]

	for x in requiredspec:
		if x not in myspec:
			messages.append("Required argument \""+x+"\" not specified.")

	if messages:
		raise CatalystError('\n\tAlso: '.join(messages))


def touch(myfile):
	try:
		myf=open(myfile,"w")
		myf.close()
	except IOError:
		raise CatalystError("Could not touch "+myfile+".", print_traceback=True)


def countdown(secs=5, doing="Starting"):
	if secs:
		print ">>> Waiting",secs,"seconds before starting..."
		print ">>> (Control-C to abort)...\n"+doing+" in: ",
		ticks=range(secs)
		ticks.reverse()
		for sec in ticks:
			sys.stdout.write(str(sec+1)+" ")
			sys.stdout.flush()
			time.sleep(1)
		print


def normpath(mypath):
	TrailingSlash=False
	if mypath[-1] == "/":
		TrailingSlash=True
	newpath = os.path.normpath(mypath)
	if len(newpath) > 1:
		if newpath[:2] == "//":
			newpath = newpath[1:]
	if TrailingSlash:
		newpath=newpath+'/'
	return newpath
