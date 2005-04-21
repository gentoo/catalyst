# Copyright 1999-2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/modules/catalyst_support.py,v 1.40 2005/04/21 14:45:09 rocket Exp $

import sys,string,os,types,re,signal,traceback,md5
# a function to turn a string of non-printable characters into a string of
# hex characters
def hexify(str):
    hexStr = string.hexdigits
    r = ''
    for ch in str:
	i = ord(ch)
	r = r + hexStr[(i >> 4) & 0xF] + hexStr[i & 0xF]
    return r
# hexify()

# A function to calculate the md5 sum of a file
def calc_md5(file):
    m = md5.new()
    f = open(file, 'r')
    for line in f.readlines():
	m.update(line)
    f.close()
    md5sum = hexify(m.digest())
    print "MD5 (%s) = %s" % (file, md5sum)
    return md5sum
# calc_md5
    
def read_from_clst(file):
	line = ''
	myline = ''
	try:
		myf=open(file,"r")
	except:
		raise CatalystError, "Could not open file "+file
	for line in myf.readlines():
	    line = string.replace(line, "\n", "") # drop newline
	    myline = myline + line
	myf.close()
	return myline
# read_from_clst

# these should never be touched
required_build_targets=["generic_target","generic_stage_target"]

# new build types should be added here
valid_build_targets=["stage1_target","stage2_target","stage3_target","stage4_target","grp_target",
			"livecd_stage1_target","livecd_stage2_target","embedded_target",
			"tinderbox_target","snapshot_target","netboot_target"]

required_config_file_values=["storedir","sharedir","distdir","portdir"]
valid_config_file_values=required_config_file_values[:]
valid_config_file_values.append("PKGCACHE")
valid_config_file_values.append("KERNCACHE")
valid_config_file_values.append("CCACHE")
valid_config_file_values.append("DISTCC")
valid_config_file_values.append("ENVSCRIPT")
valid_config_file_values.append("AUTORESUME")
valid_config_file_values.append("options")
valid_config_file_values.append("DEBUG")
valid_config_file_values.append("VERBOSE")
valid_config_file_values.append("PURGE")

verbosity=1

def list_bashify(mylist):
	if type(mylist)==types.StringType:
		mypack=[mylist]
	else:
		mypack=mylist[:]
	for x in range(0,len(mypack)):
		# surround args with quotes for passing to bash,
		# allows things like "<" to remain intact
		mypack[x]="'"+mypack[x]+"'"
	mypack=string.join(mypack)
	return mypack

def list_to_string(mylist):
	if type(mylist)==types.StringType:
		mypack=[mylist]
	else:
		mypack=mylist[:]
	for x in range(0,len(mypack)):
		# surround args with quotes for passing to bash,
		# allows things like "<" to remain intact
		mypack[x]=mypack[x]
	mypack=string.join(mypack)
	return mypack

class CatalystError(Exception):
	def __init__(self, message):
		if message:
			print
			print traceback.print_exc(file=sys.stdout)
			print
			print "!!! catalyst: "+message
			print
			
def die(msg=None):
	warn(msg)
	sys.exit(1)

def warn(msg):
	print "!!! catalyst: "+msg

def spawn(mystring,debug=0,fd_pipes=None):
	"""
	apparently, os.system mucks up return values, so this code
	should fix that.

	Taken from portage.py - thanks to carpaski@gentoo.org
	"""
	print "Running command \""+mystring+"\""
	myargs=[]
	mycommand = "/bin/bash"
	if debug:
		myargs=["bash","-x","-c",mystring]
	else:
		myargs=["bash","-c",mystring]
	
	mypid=os.fork()
	if mypid==0:
		if fd_pipes:
			os.dup2(fd_pipes[0], 0) # stdin  -- (Read)/Write
			os.dup2(fd_pipes[1], 1) # stdout -- Read/(Write)
			os.dup2(fd_pipes[2], 2) # stderr -- Read/(Write)
		try:
			os.execvp(mycommand,myargs)
		except Exception, e:
			raise CatalystError,myexc
		
		# If the execve fails, we need to report it, and exit
		# *carefully* --- report error here
		os._exit(1)
		sys.exit(1)
		return # should never get reached
	try:
		retval=os.waitpid(mypid,0)[1]
	except:
	       	os.kill(mypid,signal.SIGTERM)
		if os.waitpid(mypid,os.WNOHANG)[1] == 0:
		# feisty bugger, still alive.
			os.kill(mypid,signal.SIGKILL)

	if (retval & 0xff)==0:
		return (retval >> 8) # return exit code
	else:
		return ((retval & 0xff) << 8) # interrupted by signal
	

def cmd(mycmd,myexc=""):
	try:
		retval=spawn(mycmd)
		if retval != 0:
			raise CatalystError,myexc
	except KeyboardInterrupt:
		raise CatalystError,"Caught SIGINT, aborting."


def file_locate(settings,filelist,expand=1):
	#if expand=1, non-absolute paths will be accepted and
	# expanded to os.getcwd()+"/"+localpath if file exists
	for myfile in filelist:
		if not settings.has_key(myfile):
			#filenames such as cdtar are optional, so we don't assume the variable is defined.
			pass
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

def parse_spec(mylines):
	myspec={}
	pos=0
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
			myline=mylines[pos].split()
			
			if (len(myline)==0) or (myline[0][-1] != ":"):
				msg("Skipping invalid spec line "+repr(pos+1))
			#strip colon:
			myline[0]=myline[0][:-1]
			if len(myline)==2:
				#foo: bar  --> foo:"bar"
				myspec[myline[0]]=myline[1]
				pos += 1
			elif len(myline)>2:
				#foo: bar oni --> foo: [ "bar", "oni" ]
				myspec[myline[0]]=myline[1:]
				pos += 1
			else:
				#foo:
				# bar
				# oni meep
				# --> foo: [ "bar", "oni", "meep" ]
				accum=[]
				pos += 1
				while (pos<len(mylines)):
					if len(mylines[pos])<=1:
						#skip blanks
						pos += 1
						continue
					if mylines[pos][0] == "#":
						#skip comments
						pos += 1
						continue
					if mylines[pos][0] in [" ","\t"]:
						#indented line, add to accumulator
						accum.extend(mylines[pos].split())
						pos += 1
					else:
						#we've hit the next item, break out
						break
				myspec[myline[0]]=accum
	return myspec

def parse_makeconf(mylines):
	mymakeconf={}
	pos=0
	pat=re.compile("([a-zA-Z_]*)=(.*)")
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

def read_spec(myspecfile):
	try:
		myf=open(myspecfile,"r")
	except:
		raise CatalystError, "Could not open spec file "+myspecfile
	mylines=myf.readlines()
	myf.close()
	return parse_spec(mylines)

def read_makeconf(mymakeconffile):
	if os.path.exists(mymakeconffile):
	    try:
		    myf=open(mymakeconffile,"r")
		    mylines=myf.readlines()
		    myf.close()
		    return parse_makeconf(mylines)
	    except:
		    raise CatalystError, "Could not open make.conf file "+myspecfile
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
	a=open("/proc/mounts","r")
	mylines=a.readlines()
	a.close()
	for line in mylines:
		mysplit=line.split()
		if pathcompare(path,mysplit[1]):
			return 1
	return 0

def arg_parse(cmdline):
	#global required_config_file_values
	mydict={}
	for x in cmdline:
		foo=string.split(x,"=")
		if len(foo)!=2:
			raise CatalystError, "Invalid arg syntax: "+x

		else:
			mydict[foo[0]]=foo[1]
	
	# if all is well, we should return (we should have bailed before here if not)
	return mydict
		
def addl_arg_parse(myspec,addlargs,requiredspec,validspec):
	"helper function to help targets parse additional arguments"
	global valid_config_file_values
	for x in addlargs.keys():
		if x not in validspec and x not in valid_config_file_values:
			raise CatalystError, "Argument \""+x+"\" not recognized."
		else:
			myspec[x]=addlargs[x]
	for x in requiredspec:
		if not myspec.has_key(x):
			raise CatalystError, "Required argument \""+x+"\" not specified."
	
def spec_dump(myspec):
	for x in myspec.keys():
		print x+": "+repr(myspec[x])

def touch(myfile):
	try:
		myf=open(myfile,"w")
		myf.close()
	except IOError:
		raise CatalystError, "Could not touch "+myfile+"."
