
import sys, os, re, signal
from catalyst.output import warn
import catalyst.util
from catalyst.error import *

required_config_file_values=["storedir","sharedir","distdir","portdir"]
valid_config_file_values=required_config_file_values[:]
valid_config_file_values.append("PKGCACHE")
valid_config_file_values.append("KERNCACHE")
valid_config_file_values.append("CCACHE")
valid_config_file_values.append("DISTCC")
valid_config_file_values.append("ICECREAM")
valid_config_file_values.append("ENVSCRIPT")
valid_config_file_values.append("AUTORESUME")
valid_config_file_values.append("FETCH")
valid_config_file_values.append("CLEAR_AUTORESUME")
valid_config_file_values.append("options")
valid_config_file_values.append("DEBUG")
valid_config_file_values.append("VERBOSE")
valid_config_file_values.append("PURGE")
valid_config_file_values.append("PURGEONLY")
valid_config_file_values.append("SNAPCACHE")
valid_config_file_values.append("snapshot_cache")
valid_config_file_values.append("hash_function")
valid_config_file_values.append("digests")
valid_config_file_values.append("contents")
valid_config_file_values.append("SEEDCACHE")

verbosity=1

def file_locate(settings,filelist,expand=1):
	#if expand=1, non-absolute paths will be accepted and
	# expanded to os.getcwd()+"/"+localpath if file exists
	for myfile in filelist:
		if not myfile in settings:
			#filenames such as cdtar are optional, so we don't assume the variable is defined.
			pass
		else:
		    if len(settings[myfile])==0:
			    raise CatalystError, "File variable \""+myfile+"\" has a length of zero (not specified.)"
		    if settings[myfile][0]=="/":
			    if not os.path.exists(settings[myfile]):
				    raise CatalystError, "Cannot locate specified "+myfile+": "+settings[myfile]
		    elif expand and os.path.exists(os.getcwd()+"/"+settings[myfile]):
			    settings[myfile]=os.getcwd()+"/"+settings[myfile]
		    else:
			    raise CatalystError, "Cannot locate specified "+myfile+": "+settings[myfile]+" (2nd try)"
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
"""

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
				import snakeoil.fileutils
				return snakeoil.fileutils.read_bash_dict(mymakeconffile, sourcing_command="source")
			except ImportError:
				try:
					import portage_util
					return portage_util.getconfig(mymakeconffile, tolerant=1, allow_sourcing=True)
				except ImportError:
					myf=open(mymakeconffile,"r")
					mylines=myf.readlines()
					myf.close()
					return parse_makeconf(mylines)
		except:
			raise CatalystError, "Could not parse make.conf file "+mymakeconffile
	else:
		makeconf={}
		return makeconf

def addl_arg_parse(myspec,addlargs,requiredspec,validspec):
	"helper function to help targets parse additional arguments"
	global valid_config_file_values

	for x in addlargs.keys():
		if x not in validspec and x not in valid_config_file_values and x not in requiredspec:
			raise CatalystError, "Argument \""+x+"\" not recognized."
		else:
			myspec[x]=addlargs[x]

	for x in requiredspec:
		if not x in myspec:
			raise CatalystError, "Required argument \""+x+"\" not specified."

