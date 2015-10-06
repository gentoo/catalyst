
# Maintained in full by:
# Catalyst Team <catalyst@gentoo.org>
# Release Engineering Team <releng@gentoo.org>
# Andrew Gaffney <agaffney@gentoo.org>
# Chris Gianelloni <wolf31o2@wolf31o2.org>
# $Id$

import os
import sys
import getopt
import os.path

__selfpath__ = os.path.abspath(os.path.dirname(__file__))

from DeComp.definitions import (COMPRESS_DEFINITIONS, DECOMPRESS_DEFINITIONS,
	CONTENTS_DEFINITIONS)
from DeComp.contents import ContentsMap

import catalyst.config
import catalyst.util
from catalyst.defaults import confdefaults, option_messages
from catalyst.hash_utils import HashMap, HASH_DEFINITIONS
from catalyst.support import CatalystError, find_binary
from catalyst.version import get_version


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
	print get_version()
	print "Copyright 2003-2008 Gentoo Foundation"
	print "Copyright 2008-2012 various authors"
	print "Distributed under the GNU General Public License version 2.1\n"

def parse_config(myconfig):
	# search a couple of different areas for the main config file
	myconf={}
	config_file=""

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
	for x in list(confdefaults):
		if x in myconf:
			if x == 'options':
				conf_values[x] = set(myconf[x].split())
			elif x in ["decompressor_search_order"]:
				conf_values[x] = myconf[x].split()
			else:
				conf_values[x]=myconf[x]
		else:
			conf_values[x]=confdefaults[x]

	# add our python base directory to use for loading target arch's
	conf_values["PythonDir"] = __selfpath__

	# print out any options messages
	for opt in conf_values['options']:
		if opt in option_messages:
			print option_messages[opt]

	for key in ["digests", "envscript", "var_tmpfs_portage", "port_logdir",
				"local_overlay"]:
		if key in myconf:
			conf_values[key] = myconf[key]

	if "contents" in myconf:
		# replace '-' with '_' (for compatibility with existing configs)
		conf_values["contents"] = myconf["contents"].replace("-", '_')

	if "envscript" in myconf:
		print "Envscript support enabled."

	# take care of any variable substitutions that may be left
	for x in list(conf_values):
		if isinstance(conf_values[x], str):
			conf_values[x] = conf_values[x] % conf_values


def import_module(target):
	"""
	import catalyst's own modules
	(i.e. targets and the arch modules)
	"""
	try:
		mod_name = "catalyst.targets." + target
		module = __import__(mod_name, [],[], ["not empty"])
	except ImportError as e:
		print "!!! catalyst: Python module import error: %s " % target + \
			"in catalyst/targets/ ... exiting."
		print "ERROR was: ", e
		sys.exit(1)
	return module


def build_target(addlargs):
	try:
		target = addlargs["target"].replace('-', '_')
		module = import_module(target)
		target = getattr(module, target)(conf_values, addlargs)
	except AttributeError:
		raise CatalystError(
			"Target \"%s\" not available." % target,
			print_traceback=True)
	except CatalystError:
		return False
	return target.run()


def main():

	if os.getuid() != 0:
		version()
		# catalyst cannot be run as a normal user due to chroots, mounts, etc
		print "!!! catalyst: This script requires root privileges to operate"
		sys.exit(2)

	# we need some options in order to work correctly
	if len(sys.argv) < 2:
		usage()
		sys.exit(2)

	# parse out the command line arguments
	try:
		opts, _args = getopt.getopt(sys.argv[1:], "apPThvdc:C:f:FVs:", ["purge", "purgeonly", "purgetmponly", "help", "version", "debug",
			"clear-autoresume", "config=", "cli=", "file=", "fetch", "verbose","snapshot="])

	except getopt.GetoptError:
		usage()
		sys.exit(2)

	myconfig=""
	myspecfile=""
	mycmdline=[]

	# check preconditions
	if len(opts) == 0:
		print "!!! catalyst: please specify one of either -f or -C\n"
		usage()
		sys.exit(2)

	options = set()

	run = False
	for o, a in opts:
		if o in ("-h", "--help"):
			version()
			usage()
			sys.exit(1)

		if o in ("-V", "--version"):
			print get_version()
			sys.exit(1)

		if o in ("-d", "--debug"):
			conf_values["DEBUG"] = True
			conf_values["VERBOSE"] = True

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
			options.add("fetch")

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
			options.add("purge")

		if o in ("-P", "--purgeonly"):
			options.add("purgeonly")

		if o in ("-T", "--purgetmponly"):
			options.add("purgetmponly")

		if o in ("-a", "--clear-autoresume"):
			options.add("clear-autoresume")

	#print "MAIN: cli options =", options

	if not run:
		print "!!! catalyst: please specify one of either -f or -C\n"
		usage()
		sys.exit(2)

	# made it this far so start by outputting our version info
	version()
	# import configuration file and import our main module using those settings
	parse_config(myconfig)

	conf_values["options"].update(options)
	#print "MAIN: conf_values['options'] =", conf_values["options"]

	# initialize our contents generator
	contents_map = ContentsMap(CONTENTS_DEFINITIONS)
	conf_values["contents_map"] = contents_map

	# initialze our hash and contents generators
	hash_map = HashMap(HASH_DEFINITIONS)
	conf_values["hash_map"] = hash_map

	# initialize our (de)compression definitions
	conf_values['decompress_definitions'] = DECOMPRESS_DEFINITIONS
	conf_values['compress_definitions'] = COMPRESS_DEFINITIONS
	# TODO add capability to config/spec new definitions

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
		raise CatalystError("Required value \"target\" not specified.")

	# everything is setup, so the build is a go
	try:
		success = build_target(addlargs)
	except KeyboardInterrupt:
		print "\nCatalyst build aborted due to user interrupt ( Ctrl-C )"
		print
		print "Catalyst aborting...."
		sys.exit(2)
	if not success:
		sys.exit(2)
	sys.exit(0)
