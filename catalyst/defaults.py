

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
valid_config_file_values.extend([ "distcc", "envscript",
	"options", "DEBUG", "VERBOSE",
	"snapshot_cache", "hash_function", "digests", "contents"
	])

verbosity = 1

# Use hash_utils.HashMap.fields for the value legend
# fields = ["func", "cmd", "args", "id"]
hash_definitions = {
	"adler32"  :["calc_hash2", "shash", ["-a", "ADLER32"], "ADLER32"],
	"crc32"    :["calc_hash2", "shash", ["-a", "CRC32"], "CRC32"],
	"crc32b"   :["calc_hash2", "shash", ["-a", "CRC32B"], "CRC32B"],
	"gost"     :["calc_hash2", "shash", ["-a", "GOST"], "GOST"],
	"haval128" :["calc_hash2", "shash", ["-a", "HAVAL128"], "HAVAL128"],
	"haval160" :["calc_hash2", "shash", ["-a", "HAVAL160"], "HAVAL160"],
	"haval192" :["calc_hash2", "shash", ["-a", "HAVAL192"], "HAVAL192"],
	"haval224" :["calc_hash2", "shash", ["-a", "HAVAL224"], "HAVAL224"],
	"haval256" :["calc_hash2", "shash", ["-a", "HAVAL256"], "HAVAL256"],
	"md2"      :["calc_hash2", "shash", ["-a", "MD2"], "MD2"],
	"md4"      :["calc_hash2", "shash", ["-a", "MD4"], "MD4"],
	"md5"      :["calc_hash2", "shash", ["-a", "MD5"], "MD5"],
	"ripemd128":["calc_hash2", "shash", ["-a", "RIPEMD128"], "RIPEMD128"],
	"ripemd160":["calc_hash2", "shash", ["-a", "RIPEMD160"], "RIPEMD160"],
	"ripemd256":["calc_hash2", "shash", ["-a", "RIPEMD256"], "RIPEMD256"],
	"ripemd320":["calc_hash2", "shash", ["-a", "RIPEMD320"], "RIPEMD320"],
	"sha1"     :["calc_hash2", "shash", ["-a", "SHA1"], "SHA1"],
	"sha224"   :["calc_hash2", "shash", ["-a", "SHA224"], "SHA224"],
	"sha256"   :["calc_hash2", "shash", ["-a", "SHA256"], "SHA256"],
	"sha384"   :["calc_hash2", "shash", ["-a", "SHA384"], "SHA384"],
	"sha512"   :["calc_hash2", "shash", ["-a", "SHA512"], "SHA512"],
	"snefru128":["calc_hash2", "shash", ["-a", "SNEFRU128"], "SNEFRU128"],
	"snefru256":["calc_hash2", "shash", ["-a", "SNEFRU256"], "SNEFRU256"],
	"tiger"    :["calc_hash2", "shash", ["-a", "TIGER"], "TIGER"],
	"tiger128" :["calc_hash2", "shash", ["-a", "TIGER128"], "TIGER128"],
	"tiger160" :["calc_hash2", "shash", ["-a", "TIGER160"], "TIGER160"],
	"whirlpool":["calc_hash2", "shash", ["-a", "WHIRLPOOL"], "WHIRLPOOL"],
	}

# use contents.ContentsMap.fields for the value legend
# Key:[function, cmd]
contents_definitions = {
	# 'find' is disabled because it requires the source path, which is not
	# always available
	#"find"		:["calc_contents","find %(path)s"],
	"tar_tv":["calc_contents","tar tvf %(file)s"],
	"tar_tvz":["calc_contents","tar tvzf %(file)s"],
	"tar_tvj":["calc_contents","tar -I lbzip2 -tvf %(file)s"],
	"isoinfo_l":["calc_contents","isoinfo -l -i %(file)s"],
	# isoinfo_f should be a last resort only
	"isoinfo_f":["calc_contents","isoinfo -f -i %(file)s"],
}


confdefaults={
	"distdir": "/usr/portage/distfiles",
	"hash_function": "crc32",
	"packagedir": "/usr/portage/packages",
	"portdir": "/usr/portage",
	"port_tmpdir": "/var/tmp/portage",
	"repo_name": "portage",
	"sharedir": "/usr/lib/catalyst",
	"snapshot_cache": "/var/tmp/catalyst/snapshot_cache",
	"snapshot_name": "portage-",
	"storedir": "/var/tmp/catalyst",
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
