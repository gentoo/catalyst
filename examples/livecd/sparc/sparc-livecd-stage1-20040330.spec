subarch: sparc
version_stamp: 20040330
target: livecd-stage1
rel_type: default
rel_version: 2004.0
profile: default-sparc-2004.0
snapshot: 20040330
source_subpath: default/stage3-sparc-20040330
livecd/use:
	-X
	-gtk
	-perl
	livecd
	minimal
livecd/packages:
	>=sys-apps/baselayout-1.8.6.13
	module-init-tools
	irssi
	rdate
	aumix
	metalog
	parted
	links
	star
	strace
	raidtools
	nfs-utils
	usbutils
	e2fsprogs
	reiserfsprogs
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
	
