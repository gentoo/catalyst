subarch: sparc64
version_stamp: 20040330
target: livecd-stage1
rel_type: default
rel_version: 2004.0
profile: default-sparc64-2004.0
snapshot: 20040330
source_subpath: default/stage3-sparc64-20040330
livecd/use:
	-X
	-gtk
	-perl
	livecd
	minimal
livecd/packages:
	>=sys-apps/baselayout-1.8.6.13
	module-init-tools
	hotplug
	irssi
	rdate
	aumix
	metalog
	pciutils
	parted
	links
	star
	strace
	raidtools
	nfs-utils
	usbutils
	e2fsprogs
	reiserfsprogs
	hdparm
	nano
	vim
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
	iputils
	lvm-user
	
