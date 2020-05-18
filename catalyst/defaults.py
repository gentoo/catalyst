
import portage

from collections import OrderedDict

from DeComp.definitions import DECOMPRESSOR_SEARCH_ORDER
from DeComp.definitions import COMPRESSOR_PROGRAM_OPTIONS, XATTRS_OPTIONS
from DeComp.definitions import DECOMPRESSOR_PROGRAM_OPTIONS, LIST_XATTRS_OPTIONS


required_config_file_values = [
    "distdir",
    "portdir",
    "sharedir",
    "storedir",
]

valid_config_file_values = required_config_file_values[:]
valid_config_file_values.extend([
    "compression_mode",
    "compressor_arch",
    "compressor_options",
    "DEBUG",
    "decompressor_search_order",
    "digests",
    "distcc",
    "envscript",
    "options",
    "VERBOSE",
])

confdefaults = {
    "comp_prog": COMPRESSOR_PROGRAM_OPTIONS['linux'],
    "compression_mode": 'lbzip2',
    "compressor_arch": None,
    "compressor_options": XATTRS_OPTIONS['linux'],
    "decomp_opt": DECOMPRESSOR_PROGRAM_OPTIONS['linux'],
    "decompressor_search_order": DECOMPRESSOR_SEARCH_ORDER,
    "distdir": portage.settings['DISTDIR'],
    "icecream": "/var/cache/icecream",
    'list_xattrs_opt': LIST_XATTRS_OPTIONS['linux'],
    "local_overlay": "/var/db/repos/local",
    "port_conf": "/etc/portage",
    "make_conf": "%(port_conf)s/make.conf",
    "options": set(),
    "pkgdir": "/var/cache/binpkgs",
    "port_tmpdir": "/var/tmp/portage",
    "repo_basedir": "/var/db/repos",
    "repo_name": "gentoo",
    "repos": "%(storedir)s/repos",
    "sharedir": "/usr/share/catalyst",
    "shdir": "%(sharedir)s/targets",
    "source_matching": "strict",
    "storedir": "/var/tmp/catalyst",
    "target_distdir": "/var/cache/distfiles",
    "target_pkgdir": "/var/cache/binpkgs",
}

DEFAULT_CONFIG_FILE = '/etc/catalyst/catalyst.conf'

PORT_LOGDIR_CLEAN = \
    'find "${PORT_LOGDIR}" -type f ! -name "summary.log*" -mtime +30 -delete'

MOUNT_DEFAULTS = OrderedDict([
    ('proc', {
        'enable': True,
        'source': '/proc',
        'target': '/proc',
    }),
    ('dev', {
        'enable': True,
        'source': '/dev',
        'target': '/dev',
    }),
    ('devpts', {
        'enable': True,
        'source': '/dev/pts',
        'target': '/dev/pts',
    }),
    ('shm', {
        'enable': True,
        'source': 'shm',
        'target': '/dev/shm',
    }),
    ('run', {
        'enable': True,
        'source': 'tmpfs',
        'target': '/run',
    }),
    ('portdir', {
        'enable': True,
        'source': 'config',
        'target': 'config',
    }),
    ('distdir', {
        'enable': True,
        'source': 'config',
        'target': 'config',
    }),
    ('pkgdir', {
        'enable': False,
        'source': 'config',
        'target': 'config',
    }),
    ('port_tmpdir', {
        'enable': True,
        'source': 'maybe_tmpfs',
        'target': '/var/tmp/portage',
    }),
    ('kerncache', {
        'enable': False,
        'source': 'config',
        'target': '/tmp/kerncache',
    }),
    ('port_logdir', {
        'enable': False,
        'source': 'config',
        'target': '/var/log/portage',
    }),
    ('ccache', {
        'enable': False,
        'source': 'config',
        'target': '/var/tmp/ccache',
    }),
    ('icecream', {
        'enable': False,
        'source': ...,
        'target': '/usr/lib/icecc/bin',
    }),
])

option_messages = {
    "autoresume": "Autoresuming support enabled.",
    "ccache": "Compiler cache support enabled.",
    "clear-autoresume": "Cleaning autoresume flags support enabled.",
    "distcc": "Distcc support enabled.",
    "icecream": "Icecream compiler cluster support enabled.",
    "kerncache": "Kernel cache support enabled.",
    "pkgcache": "Package cache support enabled.",
    "purge": "Purge support enabled.",
    "seedcache": "Seed cache support enabled.",
}
