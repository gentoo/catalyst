## generic netboot image specfile
## used to build a network bootable image

## John Davis <zhen@gentoo.org>

# subarch can be any of the supported Catalyst subarches (like athlon-xp). Refer
# to the catalyst reference manual (http://www.gentoo.org/proj/en/releng/catalyst) for supported arches.
# example:
# subarch: athlon-xp
subarch:

# version stamp is an identifier for the build. can be anything you want it to be, but it
# is usually a date.
# example:
# version_stamp: 2004.2
version_stamp: 

# target specifies what type of build Catalyst is to do. check the catalyst reference manual
# for supported targets.
# example:
# target: stage2
target:

# rel_type defines what kind of build we are doing. usually, default will suffice.
# example:
# rel_type: default
rel_type:

# system profile used to build the media
# example:
# profile: default-x86-2004.0
profile:

# which snapshot to use
# example:
# snapshot: 20040614
snapshot:

# where the seed stage comes from, path is relative to $clst_sharedir (catalyst.conf)
# example:
# default/stage3-x86-2004.1
source_subpath:

# kernel sources to use (e.g gentoo-dev-sources, gentoo-sources, vanilla-sources)
netboot/kernel/sources:

# kernel config (.config) used to build the kernel
netboot/kernel/config:

# (optional) USE flags to set for the kernel
netboot/kernel/use:

# (optional) USE flags to set for the packages that are to be included in the netboot image
netboot/use:

# config used to build busybox
netboot/busybox_config:

# base tarball to use for the netboot image
netboot/base_tarball: /usr/lib/catalyst/netboot/netboot-base.tar.bz2

# packages that you want to have available in the netboot image
netboot/packages:
	raidtools
	xfsprogs
	e2fsprogs
	reiserfsprogs

# here you can set which files from the above packages you want copied over to the image
netboot/packages/raidtools/files: /sbin/raidstart /sbin/mkraid /sbin/detect_multipath /sbin/raidreconf /sbin/raidstop /sbin/raidhotadd /sbin/raidhotremove /sbin/raidsetfaulty /sbin/raid0run

netboot/packages/xfsprogs/files: /sbin/mkfs.xfs /sbin/xfs_repair /bin/xfs_check

netboot/packages/e2fsprogs/files: /sbin/mke2fs

netboot/packages/reiserfsprogs/files: /sbin/mkreiserfs

# any extra files that need copied over to the image to make it work
netboot/extra_files: /lib/libresolv.so.2 /lib/libnss_compat.so.2 /lib/libnss_dns.so.2 /lib/libnss_files.so.2 /sbin/consoletype
