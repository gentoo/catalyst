subarch: hppa
version_stamp: 20040227
target: livecd-stage1
rel_type: default
rel_version: 2004.0
snapshot: 20040227
source_subpath: default-hppa-2004.0/stage3-hppa-20040227
livecd/use:
	-X
	-gtk
	-svga
	fbcon
	livecd
livecd/packages:
	>=sys-apps/baselayout-1.8.6.12-r4
#	kudzu
#	module-init-tools
#	hotplug
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
#	jfsutils
	usbutils
	speedtouch
	xfsprogs
	e2fsprogs
	reiserfsprogs
	hdparm
	nano
	less
	openssh
	dhcpcd
	mingetty
	pwgen
#	popt
	dialog
	rp-pppoe
	gpm
	screen
	mirrorselect
	iputils
#	hwdata-knoppix
#	hwsetup
#	bootsplash
#	device-mapper
#	lvm2
	livecd-tools	
	ucl

