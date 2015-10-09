
# Maintained in full by:
# Catalyst Team <catalyst@gentoo.org>
# Release Engineering Team <releng@gentoo.org>
# Andrew Gaffney <agaffney@gentoo.org>
# Chris Gianelloni <wolf31o2@wolf31o2.org>
# $Id$

import argparse
import datetime
import os
import sys

from snakeoil import process

__selfpath__ = os.path.abspath(os.path.dirname(__file__))

from DeComp.definitions import (COMPRESS_DEFINITIONS, DECOMPRESS_DEFINITIONS,
	CONTENTS_DEFINITIONS)
from DeComp.contents import ContentsMap

from catalyst import log
import catalyst.config
from catalyst.defaults import confdefaults, option_messages
from catalyst.hash_utils import HashMap, HASH_DEFINITIONS
from catalyst.support import CatalystError
from catalyst.version import get_version


conf_values={}


def version():
	log.info(get_version())
	log.info('Copyright 2003-%s Gentoo Foundation', datetime.datetime.now().year)
	log.info('Copyright 2008-2012 various authors')
	log.info('Distributed under the GNU General Public License version 2.1')

def parse_config(myconfig):
	# search a couple of different areas for the main config file
	myconf={}
	config_file=""
	default_config_file = '/etc/catalyst/catalyst.conf'

	# first, try the one passed (presumably from the cmdline)
	if myconfig:
		if os.path.exists(myconfig):
			log.notice('Using command line specified Catalyst configuration file: %s',
				myconfig)
			config_file=myconfig

		else:
			log.critical('Specified configuration file does not exist: %s', myconfig)

	# next, try the default location
	elif os.path.exists(default_config_file):
		log.notice('Using default Catalyst configuration file: %s',
			default_config_file)
		config_file = default_config_file

	# can't find a config file (we are screwed), so bail out
	else:
		log.critical('Could not find a suitable configuration file')

	# now, try and parse the config file "config_file"
	try:
#		execfile(config_file, myconf, myconf)
		myconfig = catalyst.config.ConfigParser(config_file)
		myconf.update(myconfig.get_values())

	except Exception:
		log.critical('Could not find parse configuration file: %s', myconfig)

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
			log.info(option_messages[opt])

	for key in ["digests", "envscript", "var_tmpfs_portage", "port_logdir",
				"local_overlay"]:
		if key in myconf:
			conf_values[key] = myconf[key]

	if "contents" in myconf:
		# replace '-' with '_' (for compatibility with existing configs)
		conf_values["contents"] = myconf["contents"].replace("-", '_')

	if "envscript" in myconf:
		log.info('Envscript support enabled.')

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
	except ImportError:
		log.critical('Python module import error: %s', target, exc_info=True)
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


class FilePath(object):
	"""Argparse type for getting a path to a file."""

	def __init__(self, exists=True):
		self.exists = exists

	def __call__(self, string):
		if not os.path.exists(string):
			raise argparse.ArgumentTypeError('file does not exist: %s' % string)
		return string

	def __repr__(self):
		return '%s(exists=%s)' % (type(self).__name__, self.exists)


def get_parser():
	"""Return an argument parser"""
	epilog = """Usage examples:

Using the commandline option (-C, --cli) to build a Portage snapshot:
$ catalyst -C target=snapshot version_stamp=my_date

Using the snapshot option (-s, --snapshot) to build a release snapshot:
$ catalyst -s 20071121

Using the specfile option (-f, --file) to build a stage target:
$ catalyst -f stage1-specfile.spec"""

	parser = argparse.ArgumentParser(epilog=epilog, formatter_class=argparse.RawDescriptionHelpFormatter)

	parser.add_argument('-V', '--version',
		action='version', version=get_version(),
		help='display version information')

	group = parser.add_argument_group('Program output options')
	group.add_argument('-d', '--debug',
		default=False, action='store_true',
		help='enable debugging (and default --log-level debug)')
	group.add_argument('-v', '--verbose',
		default=False, action='store_true',
		help='verbose output (and default --log-level info)')
	group.add_argument('--log-level',
		default=None,
		choices=('critical', 'error', 'warning', 'notice', 'info', 'debug'),
		help='set verbosity of output (default: notice)')
	group.add_argument('--log-file',
		type=FilePath(exists=False),
		help='write all output to this file (instead of stdout)')
	group.add_argument('--color',
		default=None, action='store_true',
		help='colorize output all the time (default: detect)')
	group.add_argument('--nocolor',
		dest='color', action='store_false',
		help='never colorize output all the time (default: detect)')

	group = parser.add_argument_group('Temporary file management')
	group.add_argument('-a', '--clear-autoresume',
		default=False, action='store_true',
		help='clear autoresume flags')
	group.add_argument('-p', '--purge',
		default=False, action='store_true',
		help='clear tmp dirs, package cache, autoresume flags')
	group.add_argument('-P', '--purgeonly',
		default=False, action='store_true',
		help='clear tmp dirs, package cache, autoresume flags and exit')
	group.add_argument('-T', '--purgetmponly',
		default=False, action='store_true',
		help='clear tmp dirs and autoresume flags and exit')

	group = parser.add_argument_group('Target/config file management')
	group.add_argument('-F', '--fetchonly',
		default=False, action='store_true',
		help='fetch files only')
	group.add_argument('-c', '--config',
		type=FilePath(),
		help='use specified configuration file')
	group.add_argument('-f', '--file',
		type=FilePath(),
		help='read specfile')
	group.add_argument('-s', '--snapshot',
		help='generate a release snapshot')
	group.add_argument('-C', '--cli',
		default=[], nargs=argparse.REMAINDER,
		help='catalyst commandline (MUST BE LAST OPTION)')

	return parser


def main():
	parser = get_parser()
	opts = parser.parse_args(sys.argv[1:])

	# Initialize the logger before anything else.
	log_level = opts.log_level
	if log_level is None:
		if opts.debug:
			log_level = 'debug'
		elif opts.verbose:
			log_level = 'info'
		else:
			log_level = 'notice'
	log.setup_logging(log_level, output=opts.log_file, debug=opts.debug,
		color=opts.color)

	# Parse the command line options.
	myconfig = opts.config
	myspecfile = opts.file
	mycmdline = opts.cli[:]

	if opts.snapshot:
		mycmdline.append('target=snapshot')
		mycmdline.append('version_stamp=' + opts.snapshot)

	conf_values['DEBUG'] = opts.debug
	conf_values['VERBOSE'] = opts.debug or opts.verbose

	options = set()
	if opts.fetchonly:
		options.add('fetch')
	if opts.purge:
		options.add('purge')
	if opts.purgeonly:
		options.add('purgeonly')
	if opts.purgetmponly:
		options.add('purgetmponly')
	if opts.clear_autoresume:
		options.add('clear-autoresume')

	# Make sure we have some work before moving further.
	if not myspecfile and not mycmdline:
		parser.error('please specify one of either -f or -C or -s')

	# made it this far so start by outputting our version info
	version()
	# import configuration file and import our main module using those settings
	parse_config(myconfig)

	conf_values["options"].update(options)
	log.debug('conf_values[options] = %s', conf_values['options'])

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
		digests = set(conf_values['digests'].split())
		valid_digests = set(HASH_DEFINITIONS.keys())

		# Use the magic keyword "auto" to use all algos that are available.
		skip_missing = False
		if 'auto' in digests:
			skip_missing = True
			digests.remove('auto')
			if not digests:
				digests = set(valid_digests)

		# First validate all the requested digests are valid keys.
		if digests - valid_digests:
			log.critical(
				'These are not valid digest entries:\n'
				'%s\n'
				'Valid digest entries:\n'
				'%s',
				', '.join(digests - valid_digests),
				', '.join(sorted(valid_digests)))

		# Then check for any programs that the hash func requires.
		for digest in digests:
			try:
				process.find_binary(hash_map.hash_map[digest].cmd)
			except process.CommandNotFound:
				# In auto mode, just ignore missing support.
				if skip_missing:
					digests.remove(digest)
					continue
				log.critical(
					'The "%s" binary needed by digest "%s" was not found. '
					'It needs to be in your system path.',
					hash_map.hash_map[digest].cmd, digest)

		# Now reload the config with our updated value.
		conf_values['digests'] = ' '.join(digests)

	if "hash_function" in conf_values:
		if conf_values["hash_function"] not in HASH_DEFINITIONS:
			log.critical(
				'%s is not a valid hash_function entry\n'
				'Valid hash_function entries:\n'
				'%s', HASH_DEFINITIONS.keys())
		try:
			process.find_binary(hash_map.hash_map[conf_values["hash_function"]].cmd)
		except process.CommandNotFound:
			log.critical(
				'The "%s" binary needed by hash_function "%s" was not found. '
				'It needs to be in your system path.',
				hash_map.hash_map[conf_values['hash_function']].cmd,
				conf_values['hash_function'])

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
			log.critical('Could not parse commandline')

	if "target" not in addlargs:
		raise CatalystError("Required value \"target\" not specified.")

	if os.getuid() != 0:
		# catalyst cannot be run as a normal user due to chroots, mounts, etc
		log.critical('This script requires root privileges to operate')

	# everything is setup, so the build is a go
	try:
		success = build_target(addlargs)
	except KeyboardInterrupt:
		log.critical('Catalyst build aborted due to user interrupt (Ctrl-C)')
	if not success:
		sys.exit(2)
	sys.exit(0)
