# Distributed under the GNU General Public License version 2
# Copyright 2003-2004 Gentoo Technologies, Inc.

import sys,string,os

required_config_file_values=["storedir","sharedir","distdir","portdir"]
valid_config_file_values=required_config_file_values[:]
valid_config_file_values.append("PKGCACHE")
valid_config_file_values.append("CCACHE")
valid_config_file_values.append("options")

verbosity=1

class CatalystError(Exception):
	def __init__(self, message):
		if message:
			print
			print "catalyst: "+message
def die(msg=None):
	warn(msg)
	sys.exit(1)

def warn(msg):
	print "catalyst: "+msg

def cmd(mycmd,myexc=""):
	print "Running command \""+mycmd+"\""
	retval=os.system(mycmd)
	if retval != 0:
		raise CatalystError,myexc

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
				msg("Skipping invalid spec line "+repr(pos))
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

def read_spec(myspecfile):
	try:
		myf=open(myspecfile,"r")
	except:
		raise CatalystError, "Could not open spec file "+myspecfile
	mylines=myf.readlines()
	myf.close()
	return parse_spec(mylines)
	
def msg(mymsg,verblevel=1):
	if verbosity>=verblevel:
		print mymsg

def ismount(path):
	"enhanced to handle bind mounts"
	if os.path.ismount(path):
		return 1
	a=open("/proc/mounts","r")
	mylines=a.readlines()
	a.close()
	for line in mylines:
		mysplit=line.split()
		if path == mysplit[1]:
			return 1
	return 0

def arg_parse(mydict,remaining,argv):
	"grab settings from argv, storing 'target' in mydict, and everything in remaining for later parsing"
	global required_config_file_values
	for x in argv:
		foo=string.split(x,"=")
		if len(foo)!=2:
			raise CatalystError, "Invalid arg syntax: "+x
		remaining[foo[0]]=foo[1]
	if not remaining.has_key("target"):
		raise CatalystError, "Required value \"target\" not specified."
	mydict["target"]=remaining["target"]
	for x in required_config_file_values:
		if not mydict.has_key(x):
			raise CatalystError, "Required config file value \""+x+"\" not found."

		
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


