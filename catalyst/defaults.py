
import os

from DeComp.definitions import DECOMPRESSOR_SEARCH_ORDER
from DeComp.definitions import COMPRESSOR_PROGRAM_OPTIONS, XATTRS_OPTIONS
from DeComp.definitions import DECOMPRESSOR_PROGRAM_OPTIONS, LIST_XATTRS_OPTIONS

# Used for the (de)compressor definitions
if os.uname()[0] in  ["Linux", "linux"]:
	TAR = 'linux'
else:
	TAR = 'bsd'

# establish the eprefix, initially set so eprefixify can
# set it on install
EPREFIX = "@GENTOO_PORTAGE_EPREFIX@".lstrip(os.sep)
# check and set it if it wasn't
if "GENTOO_PORTAGE_EPREFIX" in EPREFIX:
    EPREFIX = ''

# these should never be touched
required_build_targets = ["targetbase", "generic_stage_target"]

# new build types should be added here
valid_build_targets = ["stage1_target", "stage2_target", "stage3_target",
	"stage4_target", "grp_target", "livecd_stage1_target", "livecd_stage2_target",
	"embedded_target", "tinderbox_target", "snapshot_target", "netboot_target",
	"netboot2_target"
	]

required_config_file_values = ["storedir", "sharedir", "distdir", "portdir"]

valid_config_file_values = required_config_file_values[:]
valid_config_file_values.extend([ "distcc", "envscript",
	"options", "DEBUG", "VERBOSE",
	"snapshot_cache", "hash_function", "digests", "contents", "compressor_arch",
	"compression_mode", "compressor_options", "decompressor_search_order",
	])

# set our base defaults here to keep
# them in one location.
BASE_GENTOO_DIR = os.path.join(os.sep, EPREFIX, "var/gentoo")
REPODIR = BASE_GENTOO_DIR + "/repos"
DISTDIR = BASE_GENTOO_DIR + "/distfiles"
PKGDIR = BASE_GENTOO_DIR + "/packages"
MAINREPO = "gentoo"
PORTDIR = REPODIR + "/" + MAINREPO

confdefaults={
	"archdir": "%(PythonDir)s/arch",
	"comp_prog": COMPRESSOR_PROGRAM_OPTIONS[TAR],
	"compression_mode": 'lbzip2',
	"compressor_arch": None,
	"compressor_options": XATTRS_OPTIONS[TAR],
	"decomp_opt": DECOMPRESSOR_PROGRAM_OPTIONS[TAR],
	"decompressor_search_order": DECOMPRESSOR_SEARCH_ORDER,
	"distdir": DISTDIR[:],
	"hash_function": "crc32",
	"icecream": os.path.join(os.sep, EPREFIX, "var/cache/icecream"),
	'list_xattrs_opt': LIST_XATTRS_OPTIONS[TAR],
	"local_overlay": REPODIR[:] + "/local",
	"port_conf": "/etc/portage",
	"make_conf": "%(port_conf)s/make.conf",
	"options": set(),
	"packagedir": PKGDIR[:],
	"portdir": PORTDIR[:],
	"port_tmpdir": os.path.join(os.sep, EPREFIX, "var/tmp/portage"),
	"PythonDir": "./catalyst",
	"repo_basedir": REPODIR[:],
	"repo_name": MAINREPO[:],
	"sed": "sed",
	"sharedir": os.path.join(os.sep, EPREFIX, "usr/share/catalyst"),
	"shdir": os.path.join(os.sep, EPREFIX, "usr/share/catalyst/targets/"),
	"snapshot_cache": os.path.join(os.sep, EPREFIX, "var/tmp/catalyst/snapshot_cache"),
	"snapshot_name": "%(repo_name)s-",
	"source_matching": "strict",
	"storedir": os.path.join(os.sep, EPREFIX, "var/tmp/catalyst"),
	"target_distdir": DISTDIR[:],
	"target_pkgdir": PKGDIR[:],
	}

DEFAULT_CONFIG_FILE = os.path.join(os.sep, EPREFIX, 'etc/catalyst/catalyst.conf')

PORT_LOGDIR_CLEAN = \
	'find "${PORT_LOGDIR}" -type f ! -name "summary.log*" -mtime +30 -delete'

TARGET_MOUNT_DEFAULTS = {
	"ccache": "/var/tmp/ccache",
	"dev": "/dev",
	"devpts": "/dev/pts",
	"distdir": DISTDIR[:],
	"icecream": "/usr/lib/icecc/bin",
	"kerncache": "/tmp/kerncache",
	"packagedir": PKGDIR[:],
	"portdir": PORTDIR[:],
	"port_tmpdir": "/var/tmp/portage",
	"port_logdir": "/var/log/portage",
	"proc": "/proc",
	"shm": "/dev/shm",
	}

SOURCE_MOUNT_DEFAULTS = {
	"dev": "/dev",
	"devpts": "/dev/pts",
	"distdir": DISTDIR[:],
	"portdir": PORTDIR[:],
	"port_tmpdir": "tmpfs",
	"proc": "/proc",
	"shm": "shmfs",
	}

# legend:  key: message
option_messages = {
	"autoresume": "Autoresuming support enabled.",
	"ccache": "Compiler cache support enabled.",
	"clear-autoresume": "Cleaning autoresume flags support enabled.",
	#"compress": "Compression enabled.",
	"distcc": "Distcc support enabled.",
	"icecream": "Icecream compiler cluster support enabled.",
	"kerncache": "Kernel cache support enabled.",
	"pkgcache": "Package cache support enabled.",
	"purge": "Purge support enabled.",
	"seedcache": "Seed cache support enabled.",
	"snapcache": "Snapshot cache support enabled.",
	#"tarball": "Tarball creation enabled.",
	}
