subarch: ppc
target: livecd-stage1

rel_type: default
rel_version: 2004.0
snapshot: 20040225
version_stamp: 20040225
source_subpath: default-ppc-2004.0/stage3-ppc-20040225

livecd/use:
	-*
	ipv6
	pic
	livecd

livecd/packages:
	baselayout
	ccache
	curl
	cvs
	dhcpcd
	dialog
	e2fsprogs
	ftp
	gpm
	hdparm
	hfsplusutils
	hfsutils
	host 
	hotplug
	iputils
	irssi
	keychain
	kpnadsl4linux
	less
	links
	logrotate
	lynx
	lzo 
	mac-fdisk
	metalog
	mirrorselect
	module-init-tools
	nano
	nfs-utils
	openssh
	parted
	passook
	pciutils
	popt
	ppp
	pppconfig
	pppoed
	ppc-development-sources
	pwgen
	raidtools
	reiserfsprogs
	rp-pppoe
	screen
	star
	strace
	ucl
	ufed
	unzip
	usbutils
	vim
	vixie-cron
	wget
	wireless-tools
	yaboot
