
from DeComp.definitions import DECOMPRESSOR_SEARCH_ORDER
from DeComp.definitions import COMPRESSOR_PROGRAM_OPTIONS, XATTRS_OPTIONS
from DeComp.definitions import DECOMPRESSOR_PROGRAM_OPTIONS, LIST_XATTRS_OPTIONS


# these should never be touched
required_build_targets = [
    "generic_stage_target",
    "targetbase",
]

# new build types should be added here
valid_build_targets = [
    "embedded_target",
    "livecd_stage1_target",
    "livecd_stage2_target",
    "netboot_target",
    "snapshot_target",
    "stage1_target",
    "stage2_target",
    "stage3_target",
    "stage4_target",
]

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
    "hash_function",
    "options",
    "snapshot_cache",
    "VERBOSE",
])

# set our base defaults here to keep
# them in one location.
BASE_GENTOO_DIR = "/var/gentoo"
REPODIR = BASE_GENTOO_DIR + "/repos"
DISTDIR = BASE_GENTOO_DIR + "/distfiles"
PKGDIR = BASE_GENTOO_DIR + "/packages"
MAINREPO = "gentoo"
PORTDIR = REPODIR + "/" + MAINREPO

confdefaults = {
    "comp_prog": COMPRESSOR_PROGRAM_OPTIONS['linux'],
    "compression_mode": 'lbzip2',
    "compressor_arch": None,
    "compressor_options": XATTRS_OPTIONS['linux'],
    "decomp_opt": DECOMPRESSOR_PROGRAM_OPTIONS['linux'],
    "decompressor_search_order": DECOMPRESSOR_SEARCH_ORDER,
    "distdir": DISTDIR[:],
    "hash_function": "crc32",
    "icecream": "/var/cache/icecream",
    'list_xattrs_opt': LIST_XATTRS_OPTIONS['linux'],
    "local_overlay": REPODIR[:] + "/local",
    "port_conf": "/etc/portage",
    "make_conf": "%(port_conf)s/make.conf",
    "options": set(),
    "packagedir": PKGDIR[:],
    "portdir": PORTDIR[:],
    "port_tmpdir": "/var/tmp/portage",
    "PythonDir": "./catalyst",
    "repo_basedir": REPODIR[:],
    "repo_name": MAINREPO[:],
    "sharedir": "/usr/share/catalyst",
    "shdir": "/usr/share/catalyst/targets/",
    "snapshot_cache": "/var/tmp/catalyst/snapshot_cache",
    "snapshot_name": "%(repo_name)s-",
    "source_matching": "strict",
    "storedir": "/var/tmp/catalyst",
    "target_distdir": DISTDIR[:],
    "target_pkgdir": PKGDIR[:],
}

DEFAULT_CONFIG_FILE = '/etc/catalyst/catalyst.conf'

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
    "run": "/run",
}

SOURCE_MOUNT_DEFAULTS = {
    "dev": "/dev",
    "devpts": "/dev/pts",
    "distdir": DISTDIR[:],
    "portdir": PORTDIR[:],
    "port_tmpdir": "maybe_tmpfs",
    "proc": "/proc",
    "shm": "shmfs",
    "run": "tmpfs",
}

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
    "snapcache": "Snapshot cache support enabled.",
}
