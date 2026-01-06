import argparse
import copy
import datetime
import hashlib
import os
import sys
import textwrap

import tomli

from DeComp.definitions import (COMPRESS_DEFINITIONS, DECOMPRESS_DEFINITIONS,
                                CONTENTS_DEFINITIONS)
from DeComp.contents import ContentsMap

from catalyst import log
import catalyst.config
from catalyst.context import namespace
from catalyst.defaults import (confdefaults, option_messages,
                               DEFAULT_CONFIG_FILE, valid_config_file_values)
from catalyst.support import CatalystError
from catalyst.version import get_version

conf_values = copy.deepcopy(confdefaults)


def version():
    log.info(get_version())
    log.info('Copyright 2003-%s Gentoo Foundation',
             datetime.datetime.now().year)
    log.info('Copyright 2008-2012 various authors')
    log.info('Distributed under the GNU General Public License version 2.1')


def parse_config(config_files):
    for config_file in config_files:
        log.notice('Loading configuration file: %s', config_file)
        try:
            with open(config_file, 'rb') as f:
                config = tomli.load(f)
            for key in config:
                if key not in valid_config_file_values:
                    log.critical("Unknown option '%s' in config file %s",
                                 key, config_file)
            conf_values.update(config)
        except Exception as e:
            log.critical('Could not find parse configuration file: %s: %s',
                         config_file, e)

    # print out any options messages
    for opt in conf_values['options']:
        if opt in option_messages:
            log.info(option_messages[opt])

    if "envscript" in conf_values:
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
        module = __import__(mod_name, [], [], ["not empty"])
    except ImportError:
        log.critical('Python module import error: %s', target, exc_info=True)
    return module


def build_target(addlargs):
    try:
        target = addlargs["target"].replace('-', '_')
        module = import_module(target)
        target = getattr(module, target)(conf_values, addlargs)
    except AttributeError as e:
        raise CatalystError(
            "Target \"%s\" not available." % target,
            print_traceback=True) from e
    except CatalystError:
        return False
    return target.run()


class FilePath():
    """Argparse type for getting a path to a file."""

    def __init__(self, exists=True):
        self.exists = exists

    def __call__(self, string):
        if not os.path.exists(string):
            raise argparse.ArgumentTypeError(
                'file does not exist: %s' % string)
        return string

    def __repr__(self):
        return '%s(exists=%s)' % (type(self).__name__, self.exists)


def get_parser():
    """Return an argument parser"""
    epilog = textwrap.dedent("""\
        Usage examples:

        Using the snapshot option to make a snapshot of the ebuild repo:
        $ catalyst --snapshot <git-treeish>

        Using the specfile option (-f, --file) to build a stage target:
        $ catalyst -f stage1-specfile.spec
        """)

    parser = argparse.ArgumentParser(
        epilog=epilog, formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('-V', '--version',
                        action='version', version=get_version(),
                        help='display version information')
    parser.add_argument('--enter-chroot', default=False, action='store_true',
                        help='Enter chroot before starting the build')

    group = parser.add_argument_group('Program output options')
    group.add_argument('-d', '--debug',
                       default=False, action='store_true',
                       help='enable debugging (and default --log-level debug)')
    group.add_argument('-v', '--verbose',
                       default=False, action='store_true',
                       help='verbose output (and default --log-level info)')
    group.add_argument('--log-level',
                       default=None,
                       choices=('critical', 'error', 'warning',
                                'notice', 'info', 'debug'),
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

    group = parser.add_argument_group('Developer options')
    group.add_argument('--trace',
                       default=False, action='store_true',
                       help='trace program output (akin to `sh -x`)')
    group.add_argument('--profile',
                       default=False, action='store_true',
                       help='profile program execution')

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
    group.add_argument('--versioned-cachedir',
                       dest='versioned_cachedir', action='store_true',
                       help='use stage version on cache directory name')
    group.add_argument('--unversioned-cachedir',
                       dest='versioned_cachedir', action='store_false',
                       help='do not use stage version on cache directory name')
    group.set_defaults(versioned_cachedir=False)

    group = parser.add_argument_group('Target/config file management')
    group.add_argument('-F', '--fetchonly',
                       default=False, action='store_true',
                       help='fetch files only')
    group.add_argument('-c', '--configs',
                       type=FilePath(), action='append',
                       help='use specified configuration files')
    group.add_argument('-f', '--file',
                       type=FilePath(),
                       help='read specfile')
    group.add_argument('-s', '--snapshot', type=str,
                       help='Make an ebuild repo snapshot')

    return parser


def trace(func, *args, **kwargs):
    """Run |func| through the trace module (akin to `sh -x`)"""
    import trace

    # Ignore common system modules we use.
    ignoremods = set((
        'argparse',
        'genericpath', 'gettext',
        'locale',
        'os',
        'posixpath',
        're',
        'sre_compile', 'sre_parse', 'sys',
        'tempfile', 'threading',
        'UserDict',
    ))

    # Ignore all the system modules.
    ignoredirs = set(sys.path)
    # But try to strip out the catalyst paths.
    try:
        ignoredirs.remove(os.path.dirname(os.path.dirname(
            os.path.realpath(__file__))))
    except KeyError:
        pass

    tracer = trace.Trace(
        count=False,
        trace=True,
        timing=True,
        ignoremods=ignoremods,
        ignoredirs=ignoredirs)
    return tracer.runfunc(func, *args, **kwargs)


def profile(func, *args, **kwargs):
    """Run |func| through the profile module"""
    # Should make this an option.
    sort_keys = ('time',)

    # Collect the profile.
    import cProfile
    profiler = cProfile.Profile(subcalls=True, builtins=True)
    try:
        ret = profiler.runcall(func, *args, **kwargs)
    finally:
        # Then process the results.
        import pstats
        stats = pstats.Stats(profiler, stream=sys.stderr)
        stats.strip_dirs().sort_stats(*sort_keys).print_stats()

    return ret


def main(argv):
    """The main entry point for frontends to use"""
    parser = get_parser()
    opts = parser.parse_args(argv)

    if opts.trace:
        return trace(_main, parser, opts)
    if opts.profile:
        return profile(_main, parser, opts)
    return _main(parser, opts)


def _main(parser, opts):
    """The "main" main function so we can trace/profile."""
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
    myconfigs = opts.configs
    if not myconfigs:
        myconfigs = [DEFAULT_CONFIG_FILE]
    myspecfile = opts.file

    mycmdline = list()
    if opts.snapshot:
        mycmdline.append('target: snapshot')
        mycmdline.append('snapshot_treeish: ' + opts.snapshot)

    conf_values['DEBUG'] = opts.debug
    conf_values['VERBOSE'] = opts.debug or opts.verbose

    options = []
    if opts.fetchonly:
        options.append('fetch')
    if opts.purge:
        options.append('purge')
    if opts.purgeonly:
        options.append('purgeonly')
    if opts.purgetmponly:
        options.append('purgetmponly')
    if opts.clear_autoresume:
        options.append('clear-autoresume')
    if opts.enter_chroot:
        options.append('enter-chroot')

    # Make sure we have some work before moving further.
    if not myspecfile and not mycmdline:
        parser.error('please specify one of either -f or -C or -s')

    # made it this far so start by outputting our version info
    version()
    # import configuration file and import our main module using those settings
    parse_config(myconfigs)

    conf_values["options"].extend(options)
    log.notice('conf_values[options] = %s', conf_values['options'])

    CONTENTS_DEFINITIONS_CATALYST = CONTENTS_DEFINITIONS
    CONTENTS_DEFINITIONS_CATALYST["pixz"][4].append("wsl")
    CONTENTS_DEFINITIONS_CATALYST["xz"][4].append("wsl")
    # TODO add capability to config/spec new definitions

    # initialize our contents generator
    contents_map = ContentsMap(CONTENTS_DEFINITIONS_CATALYST,
                               comp_prog=conf_values['comp_prog'],
                               decomp_opt=conf_values['decomp_opt'],
                               list_xattrs_opt=conf_values['list_xattrs_opt'])
    conf_values["contents_map"] = contents_map

    # initialize our (de)compression definitions
    conf_values['decompress_definitions'] = DECOMPRESS_DEFINITIONS
    conf_values['compress_definitions'] = COMPRESS_DEFINITIONS
    # TODO add capability to config/spec new definitions

    if "digests" in conf_values:
        valid_digests = hashlib.algorithms_available
        digests = set(conf_values['digests'])
        conf_values['digests'] = digests

        # First validate all the requested digests are valid keys.
        if digests - valid_digests:
            raise CatalystError('These are not valid digest entries:\n%s\n'
                                'Valid digest entries:\n%s' %
                                (', '.join(sorted(digests - valid_digests)),
                                 ', '.join(sorted(valid_digests))))

    addlargs = {}

    if myspecfile:
        log.notice("Processing spec file: %s", myspecfile)
        spec = catalyst.config.SpecParser(myspecfile)
        addlargs.update(spec.get_values())

    if mycmdline:
        try:
            cmdline = catalyst.config.SpecParser()
            cmdline.parse_lines(mycmdline)
            addlargs.update(cmdline.get_values())
        except CatalystError:
            log.critical('Could not parse commandline')

    if "target" not in addlargs:
        raise CatalystError("Required value \"target\" not specified.")

    if os.getuid() != 0:
        # catalyst cannot be run as a normal user due to chroots, mounts, etc
        log.critical('This script requires root privileges to operate')

    # Start off by creating unique namespaces to run in.  Would be nice to
    # use pid & user namespaces, but snakeoil's namespace module has signal
    # transfer issues (CTRL+C doesn't propagate), and user namespaces need
    # more work due to Gentoo build process (uses sudo/root/portage).
    with namespace(uts=True, ipc=True, hostname='catalyst'):
        # everything is setup, so the build is a go
        try:
            success = build_target(addlargs)
        except KeyboardInterrupt:
            log.critical('Catalyst build aborted due to user interrupt (Ctrl-C)')

    if not success:
        sys.exit(2)
    sys.exit(0)
