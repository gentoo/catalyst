## livecd-stage1 example specfile
## used to build a livecd-stage1

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
target: livecd-stage1

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

# use variables that we would like to use when building the LiveCD packages
livecd/use:
	-X
	-gtk
	-svga
	ipv6
	socks5
	livecd
	fbcon

# list of packages to be merged into the LiveCD fs.
livecd/packages:
	baselayout
	livecd-tools
	genkernel
	ucl
	kudzu
	module-init-tools
	hotplug
	irssi
	aumix
	metalog
	pciutils
	parted
	mt-st
	links
	star
	strace
	raidtools
	nfs-utils
	jfsutils
	usbutils
	speedtouch
	xfsprogs
	xfsdump
	e2fsprogs
	reiserfsprogs
	hdparm
	nano
	less
	openssh
	dhcpcd
	mingetty
	pwgen
	popt
	dialog
	rp-pppoe
	gpm
	screen
	mirrorselect
	penggy
	iputils
	hwdata-knoppix
	hwsetup
	bootsplash
	device-mapper
	lvm2
	evms
	vim
	gpart
	pwgen
	pptpclient
	mdadm
	tcptraceroute
	netcat
	ethtool
	wireless-tools
	ufed
