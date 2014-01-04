

# these should never be touched
required_build_targets = ["generic_target", "generic_stage_target"]

# new build types should be added here
valid_build_targets = ["stage1_target", "stage2_target", "stage3_target",
	"stage4_target", "grp_target", "livecd_stage1_target", "livecd_stage2_target",
	"embedded_target", "tinderbox_target", "snapshot_target", "netboot_target",
	"netboot2_target"
	]

required_config_file_values = ["storedir", "sharedir", "distdir", "portdir"]

valid_config_file_values = required_config_file_values[:]
valid_config_file_values.extend(["PKGCACHE", "KERNCACHE", "CCACHE", "DISTCC",
	"ICECREAM", "ENVSCRIPT", "AUTORESUME", "FETCH", "CLEAR_AUTORESUME",
	"options", "DEBUG", "VERBOSE", "PURGE", "PURGEONLY", "SNAPCACHE",
	"snapshot_cache", "hash_function", "digests", "contents", "SEEDCACHE"
	])

verbosity = 1

