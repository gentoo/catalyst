
import glob
import sys
import os
import re
import time
from subprocess import Popen

from catalyst import log
from catalyst.defaults import valid_config_file_values

BASH_BINARY             = "/bin/bash"


class CatalystError(Exception):
	def __init__(self, message, print_traceback=False):
		if message:
			log.error('CatalystError: %s', message, exc_info=print_traceback)


def cmd(mycmd, env=None, debug=False, fail_func=None):
	"""Run the external |mycmd|.

	If |mycmd| is a string, then it's assumed to be a bash snippet and will
	be run through bash.  Otherwise, it's a standalone command line and will
	be run directly.
	"""
	log.debug('cmd: %r', mycmd)
	sys.stdout.flush()

	if env is None:
		env = {}
	if 'BASH_ENV' not in env:
		env = env.copy()
		env['BASH_ENV'] = '/etc/spork/is/not/valid/profile.env'

	args = []
	if isinstance(mycmd, str):
		args.append(BASH_BINARY)
		if debug:
			args.append('-x')
		args.extend(['-c', mycmd])
	else:
		args.extend(mycmd)

	log.debug('args: %r', args)
	proc = Popen(args, env=env)
	ret = proc.wait()
	if ret:
		if fail_func:
			log.error('cmd(%r) exited %s; running fail_func().', args, ret)
			fail_func()
		raise CatalystError('cmd(%r) exited %s' % (args, ret),
			print_traceback=False)


def file_check(filepath, extensions=None, strict=True):
	'''Check for the files existence and that only one exists
	if others are found with various extensions
	'''
	if os.path.isfile(filepath):
		return filepath
	# it didn't exist
	# so check if there are files of that name with an extension
	files = glob.glob("%s.*" % filepath)
	# remove any false positive files
	files = [x for x in files if not x.endswith(".CONTENTS") and not x.endswith(".DIGESTS")]
	if len(files) == 1:
		return files[0]
	if len(files) > 1 and strict:
		msg = "Ambiguos Filename: %s\nPlease specify the correct extension as well" % filepath
		raise CatalystError(msg, print_traceback=False)
	target_file = None
	for ext in extensions:
		target = filepath + "." + ext
		if target in files:
			target_file = target
			break
	if target_file:
		return target_file
	raise CatalystError("File Not Found: %s" % filepath)


def file_locate(settings,filelist,expand=1):
	#if expand=1, non-absolute paths will be accepted and
	# expanded to os.getcwd()+"/"+localpath if file exists
	for myfile in filelist:
		if myfile not in settings:
			#filenames such as cdtar are optional, so we don't assume the variable is defined.
			pass
		else:
			if not settings[myfile]:
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
						with open(mymakeconffile, "r") as myf:
							mylines=myf.readlines()
						return parse_makeconf(mylines)
		except Exception:
			raise CatalystError("Could not parse make.conf file " +
				mymakeconffile, print_traceback=True)
	else:
		makeconf={}
		return makeconf


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
	"""Like os.path.ismount, but also support bind mounts"""
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


def countdown(secs=5, doing="Starting"):
	# If this is non-interactive (e.g. a cronjob), then sleeping is pointless.
	if not os.isatty(sys.stdin.fileno()):
		return

	if secs:
		sys.stdout.write(
			('>>> Waiting %s seconds before starting...\n'
			 '>>> (Control-C to abort)...\n'
			 '%s in: ') % (secs, doing))
		# py3 now creates a range object, so wrap it with list()
		ticks=list(range(secs))
		ticks.reverse()
		for sec in ticks:
			sys.stdout.write(str(sec+1)+" ")
			sys.stdout.flush()
			time.sleep(1)
		sys.stdout.write('\n')


def normpath(mypath):
	"""Clean up a little more than os.path.normpath

	Namely:
	 - Make sure leading // is turned into /.
	 - Leave trailing slash intact.
	"""
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
