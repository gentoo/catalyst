subarch: alpha
version_stamp: 20040225
target: livecd-stage1
rel_type: default
rel_version: 1.4
snapshot: 20040225
source_subpath: default-alpha-1.4/stage3-alpha-20040225
livecd/use:
	-X
	-gtk
	livecd
livecd/packages:
	>=sys-apps/baselayout-1.8.6.12-r4
	module-init-tools
	pciutils
	usbutils
	hotplug
	irssi
	gpm
	aumix
	metalog
	parted
	links
	star
	strace
	raidtools
	nfs-utils
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
	screen
	mirrorselect
	iputils
	lvm-user
	livecd-tools
