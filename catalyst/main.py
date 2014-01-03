
# Maintained in full by:
# Catalyst Team <catalyst@gentoo.org>
# Release Engineering Team <releng@gentoo.org>
# Andrew Gaffney <agaffney@gentoo.org>
# Chris Gianelloni <wolf31o2@wolf31o2.org>
# $Id$

import os
import sys
import imp
import string
import getopt
import pdb
import os.path

__selfpath__ = os.path.abspath(os.path.dirname(__file__))

sys.path.append(__selfpath__ + "/modules")

from . import __version__
import catalyst.config
import catalyst.util
from catalyst.support import (required_build_targets,
	valid_build_targets, CatalystError, find_binary, LockInUse)

from hash_utils import HashMap, HASH_DEFINITIONS



conf_values={}

def usage():
	print """Usage catalyst [options] [-C variable=value...] [ -s identifier]
 -a --clear-autoresume  clear autoresume flags
 -c --config            use specified configuration file
 -C --cli               catalyst commandline (MUST BE LAST OPTION)
 -d --debug             enable debugging
 -f --file              read specfile
 -F --fetchonly         fetch files only
 -h --help              print this help message
 -p --purge             clear tmp dirs,package cache, autoresume flags
 -P --purgeonly         clear tmp dirs,package cache, autoresume flags and exit
 -T --purgetmponly      clear tmp dirs and autoresume flags and exit
 -s --snapshot          generate a release snapshot
 -V --version           display version information
 -v --verbose           verbose output

Usage examples:

Using the commandline option (-C, --cli) to build a Portage snapshot:
catalyst -C target=snapshot version_stamp=my_date

Using the snapshot option (-s, --snapshot) to build a release snapshot:
catalyst -s 20071121"

Using the specfile option (-f, --file) to build a stage target:
catalyst -f stage1-specfile.spec
"""


def version():
	print "Catalyst, version "+__version__
	print "Copyright 2003-2008 Gentoo Foundation"
	print "Copyright 2008-2012 various authors"
	print "Distributed under the GNU General Public License version 2.1\n"

def parse_config(myconfig):
	# search a couple of different areas for the main config file
	myconf={}
	config_file=""

	confdefaults = {
		"distdir": "/usr/portage/distfiles",
		"hash_function": "crc32",
		"icecream": "/var/cache/icecream",
		"local_overlay": "/usr/local/portage",
		"options": "",
		"packagedir": "/usr/portage/packages",
		"portdir": "/usr/portage",
		"repo_name": "portage",
		"sharedir": "/usr/share/catalyst",
		"snapshot_name": "portage-",
		"snapshot_cache": "/var/tmp/catalyst/snapshot_cache",
		"storedir": "/var/tmp/catalyst",
		}

	# first, try the one passed (presumably from the cmdline)
	if myconfig:
		if os.path.exists(myconfig):
			print "Using command line specified Catalyst configuration file, "+myconfig
			config_file=myconfig

		else:
			print "!!! catalyst: Could not use specified configuration file "+\
				myconfig
			sys.exit(1)

	# next, try the default location
	elif os.path.exists("/etc/catalyst/catalyst.conf"):
		print "Using default Catalyst configuration file, /etc/catalyst/catalyst.conf"
		config_file="/etc/catalyst/catalyst.conf"

	# can't find a config file (we are screwed), so bail out
	else:
		print "!!! catalyst: Could not find a suitable configuration file"
		sys.exit(1)

	# now, try and parse the config file "config_file"
	try:
#		execfile(config_file, myconf, myconf)
		myconfig = catalyst.config.ConfigParser(config_file)
		myconf.update(myconfig.get_values())

	except:
		print "!!! catalyst: Unable to parse configuration file, "+myconfig
		sys.exit(1)

	# now, load up the values into conf_values so that we can use them
	for x in confdefaults.keys():
		if x in myconf:
			print "Setting",x,"to config file value \""+myconf[x]+"\""
			conf_values[x]=myconf[x]
		else:
			print "Setting",x,"to default value \""+confdefaults[x]+"\""
			conf_values[x]=confdefaults[x]

	# add our python base directory to use for loading target arch's
	conf_values["PythonDir"] = __selfpath__

	# parse out the rest of the options from the config file
	if "autoresume" in string.split(conf_values["options"]):
		print "Autoresuming support enabled."
		conf_values["AUTORESUME"]="1"

	if "bindist" in string.split(conf_values["options"]):
		print "Binary redistribution enabled"
		conf_values["BINDIST"]="1"
	else:
		print "Bindist is not enabled in catalyst.conf"
		print "Binary redistribution of generated stages/isos may be prohibited by law."
		print "Please see the use description for bindist on any package you are including."

	if "ccache" in string.split(conf_values["options"]):
		print "Compiler cache support enabled."
		conf_values["CCACHE"]="1"

	if "clear-autoresume" in string.split(conf_values["options"]):
		print "Cleaning autoresume flags support enabled."
		conf_values["CLEAR_AUTORESUME"]="1"

	if "distcc" in string.split(conf_values["options"]):
		print "Distcc support enabled."
		conf_values["DISTCC"]="1"

	if "icecream" in string.split(conf_values["options"]):
		print "Icecream compiler cluster support enabled."
		conf_values["ICECREAM"]="1"

	if "kerncache" in string.split(conf_values["options"]):
		print "Kernel cache support enabled."
		conf_values["KERNCACHE"]="1"

	if "pkgcache" in string.split(conf_values["options"]):
		print "Package cache support enabled."
		conf_values["PKGCACHE"]="1"

	if "preserve_libs" in string.split(conf_values["options"]):
		print "Preserving libs during unmerge."
		conf_values["PRESERVE_LIBS"]="1"

	if "purge" in string.split(conf_values["options"]):
		print "Purge support enabled."
		conf_values["PURGE"]="1"

	if "seedcache" in string.split(conf_values["options"]):
		print "Seed cache support enabled."
		conf_values["SEEDCACHE"]="1"

	if "snapcache" in string.split(conf_values["options"]):
		print "Snapshot cache support enabled."
		conf_values["SNAPCACHE"]="1"

	if "digests" in myconf:
		conf_values["digests"]=myconf["digests"]
	if "contents" in myconf:
		conf_values["contents"]=myconf["contents"]

	if "envscript" in myconf:
		print "Envscript support enabled."
		conf_values["ENVSCRIPT"]=myconf["envscript"]

	if "var_tmpfs_portage" in myconf:
		conf_values["var_tmpfs_portage"]=myconf["var_tmpfs_portage"];

	if "port_logdir" in myconf:
		conf_values["port_logdir"]=myconf["port_logdir"];

def import_modules():
	# import catalyst's own modules
	# (i.e. stage and the arch modules)
	targetmap={}

	try:
		module_dir = __selfpath__ + "/targets/"
		for x in required_build_targets:
			try:
				fh=open(module_dir + x + ".py")
				module=imp.load_module(x, fh,"targets/" + x + ".py",
					(".py", "r", imp.PY_SOURCE))
				fh.close()

			except IOError:
				raise CatalystError, "Can't find " + x + ".py plugin in " + \
					module_dir
		for x in valid_build_targets:
			try:
				fh=open(module_dir + x + ".py")
				module=imp.load_module(x, fh, "targets/" + x + ".py",
					(".py", "r", imp.PY_SOURCE))
				module.register(targetmap)
				fh.close()

			except IOError:
				raise CatalystError,"Can't find " + x + ".py plugin in " + \
					module_dir

	except ImportError:
		print "!!! catalyst: Python modules not found in "+\
			module_dir + "; exiting."
		sys.exit(1)

	return targetmap

def build_target(addlargs, targetmap):
	try:
		if addlargs["target"] not in targetmap:
			raise CatalystError,"Target \""+addlargs["target"]+"\" not available."

		mytarget=targetmap[addlargs["target"]](conf_values, addlargs)

		mytarget.run()

	except:
		catalyst.util.print_traceback()
		print "!!! catalyst: Error encountered during run of target " + addlargs["target"]
		sys.exit(1)

def main():
	targetmap={}

	version()
	if os.getuid() != 0:
		# catalyst cannot be run as a normal user due to chroots, mounts, etc
		print "!!! catalyst: This script requires root privileges to operate"
		sys.exit(2)

	# we need some options in order to work correctly
	if len(sys.argv) < 2:
		usage()
		sys.exit(2)

	# parse out the command line arguments
	try:
		opts,args = getopt.getopt(sys.argv[1:], "apPThvdc:C:f:FVs:", ["purge", "purgeonly", "purgetmponly", "help", "version", "debug",\
			"clear-autoresume", "config=", "cli=", "file=", "fetch", "verbose","snapshot="])

	except getopt.GetoptError:
		usage()
		sys.exit(2)

	# defaults for commandline opts
	debug=False
	verbose=False
	fetch=False
	myconfig=""
	myspecfile=""
	mycmdline=[]
	myopts=[]

	# check preconditions
	if len(opts) == 0:
		print "!!! catalyst: please specify one of either -f or -C\n"
		usage()
		sys.exit(2)

	run = False
	for o, a in opts:
		if o in ("-h", "--help"):
			usage()
			sys.exit(1)

		if o in ("-V", "--version"):
			print "Catalyst version "+__version__
			sys.exit(1)

		if o in ("-d", "--debug"):
			conf_values["DEBUG"]="1"
			conf_values["VERBOSE"]="1"

		if o in ("-c", "--config"):
			myconfig=a

		if o in ("-C", "--cli"):
			run = True
			x=sys.argv.index(o)+1
			while x < len(sys.argv):
				mycmdline.append(sys.argv[x])
				x=x+1

		if o in ("-f", "--file"):
			run = True
			myspecfile=a

		if o in ("-F", "--fetchonly"):
			conf_values["FETCH"]="1"

		if o in ("-v", "--verbose"):
			conf_values["VERBOSE"]="1"

		if o in ("-s", "--snapshot"):
			if len(sys.argv) < 3:
				print "!!! catalyst: missing snapshot identifier\n"
				usage()
				sys.exit(2)
			else:
				run = True
				mycmdline.append("target=snapshot")
				mycmdline.append("version_stamp="+a)

		if o in ("-p", "--purge"):
			conf_values["PURGE"] = "1"

		if o in ("-P", "--purgeonly"):
			conf_values["PURGEONLY"] = "1"

		if o in ("-T", "--purgetmponly"):
			conf_values["PURGETMPONLY"] = "1"

		if o in ("-a", "--clear-autoresume"):
			conf_values["CLEAR_AUTORESUME"] = "1"

	if not run:
		print "!!! catalyst: please specify one of either -f or -C\n"
		usage()
		sys.exit(2)

	# import configuration file and import our main module using those settings
	parse_config(myconfig)

	# initialze our hash and contents generators
	hash_map = HashMap(HASH_DEFINITIONS)
	conf_values["hash_map"] = hash_map

	# Start checking that digests are valid now that hash_map is initialized
	if "digests" in conf_values:
		for i in conf_values["digests"].split():
			if i not in HASH_DEFINITIONS:
				print
				print i+" is not a valid digest entry"
				print "Valid digest entries:"
				print HASH_DEFINITIONS.keys()
				print
				print "Catalyst aborting...."
				sys.exit(2)
			if find_binary(hash_map.hash_map[i].cmd) == None:
				print
				print "digest=" + i
				print "\tThe " + hash_map.hash_map[i].cmd + \
					" binary was not found. It needs to be in your system path"
				print
				print "Catalyst aborting...."
				sys.exit(2)
	if "hash_function" in conf_values:
		if conf_values["hash_function"] not in HASH_DEFINITIONS:
			print
			print conf_values["hash_function"]+\
				" is not a valid hash_function entry"
			print "Valid hash_function entries:"
			print HASH_DEFINITIONS.keys()
			print
			print "Catalyst aborting...."
			sys.exit(2)
		if find_binary(hash_map.hash_map[conf_values["hash_function"]].cmd) == None:
			print
			print "hash_function="+conf_values["hash_function"]
			print "\tThe "+hash_map.hash_map[conf_values["hash_function"]].cmd + \
				" binary was not found. It needs to be in your system path"
			print
			print "Catalyst aborting...."
			sys.exit(2)

	# import the rest of the catalyst modules
	targetmap=import_modules()

	addlargs={}

	if myspecfile:
		spec = catalyst.config.SpecParser(myspecfile)
		addlargs.update(spec.get_values())

	if mycmdline:
		try:
			cmdline = catalyst.config.ConfigParser()
			cmdline.parse_lines(mycmdline)
			addlargs.update(cmdline.get_values())
		except CatalystError:
			print "!!! catalyst: Could not parse commandline, exiting."
			sys.exit(1)

	if "target" not in addlargs:
		raise CatalystError, "Required value \"target\" not specified."

	# everything is setup, so the build is a go
	try:
		build_target(addlargs, targetmap)

	except CatalystError:
		print
		print "Catalyst aborting...."
		sys.exit(2)
	except KeyboardInterrupt:
		print "\nCatalyst build aborted due to user interrupt ( Ctrl-C )"
		print
		print "Catalyst aborting...."
		sys.exit(2)
	except LockInUse:
		print "Catalyst aborting...."
		sys.exit(2)
	except:
		print "Catalyst aborting...."
		raise
		sys.exit(2)
