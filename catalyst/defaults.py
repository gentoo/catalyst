

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
	"snapshot_cache", "hash_function", "digests", "contents"
	])

verbosity = 1

confdefaults={
	"distdir": "/usr/portage/distfiles",
	"hash_function": "crc32",
	"icecream": "/var/cache/icecream",
	"local_overlay": "/usr/local/portage",
	"make.conf": "/etc/portage/make.conf",
	"options": "",
	"packagedir": "/usr/portage/packages",
	"portdir": "/usr/portage",
	"port_tmpdir": "/var/tmp/portage",
	"repo_name": "portage",
	"sharedir": "/usr/lib/catalyst",
	"shdir": "/usr/lib/catalyst/targets/",
	"snapshot_cache": "/var/tmp/catalyst/snapshot_cache",
	"snapshot_name": "portage-",
	"storedir": "/var/tmp/catalyst",
	}

PORT_LOGDIR_CLEAN = \
	'find "${PORT_LOGDIR}" -type f ! -name "summary.log*" -mtime +30 -delete'

TARGET_MOUNT_DEFAULTS = {
	"ccache": "/var/tmp/ccache",
	"dev": "/dev",
	"devpts": "/dev/pts",
	"distdir": "/usr/portage/distfiles",
	"icecream": "/usr/lib/icecc/bin",
	"kerncache": "/tmp/kerncache",
	"packagedir": "/usr/portage/packages",
	"portdir": "/usr/portage",
	"port_tmpdir": "/var/tmp/portage",
	"port_logdir": "/var/log/portage",
	"proc": "/proc",
	"shm": "/dev/shm",
	}

SOURCE_MOUNT_DEFAULTS = {
	"dev": "/dev",
	"devpts": "/dev/pts",
	"distdir": "/usr/portage/distfiles",
	"portdir": "/usr/portage",
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
