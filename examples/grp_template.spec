## generic GRP (Gentoo Reference Platform) specfile
## used to build a GRP set

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
# target: grp
target: grp 

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

# directories to organize the GRP into
grp: src cd2

# use variables to use when building the GRP set
grp/use: 
	gtk2 
	gnome 
	kde 
	qt 
	bonobo 
	cdr 
	esd 
	gtkhtml 
	mozilla
	mysql
	perl
	ruby
	tcltk
	acl
	cups
	ldap
	ssl
	tcpd
	-svga

# okay, two things here. first, we know we are building stuff to go into the "src" directory
# because of the grp/src line (first part before the / is the build type, second part is
# directory specified in the grp: key). It is identified as a "srcset" which means that these
# packages will be *fetched only* and not compiled.
grp/src/type: srcset
grp/src/packages:
	gentoo-sources
	gentoo-dev-sources
	vanilla-sources
	development-sources
	iptables
	gpm
	rp-pppoe
	ppp
	speedtouch
	pciutils
	hdparm
	hotplug
	aumix
	xfree
	iputils
	vixie-cron
	sysklogd
	metalog
	syslog-ng
	raidtools
	jfsutils
	xfsprogs
	reiserfsprogs
	lvm-user
	dosfstools
	lilo
	grub
	superadduser
	gentoolkit
	chkrootkit
	minicom
	lynx
	rpm2targz
	parted
	rdate
	whois
	tcpdump
	cvs
	unzip
	zip
	netcat
	isdn4k-utils
	nforce-net
	nforce-audio
	iproute
	nvidia-kernel
	nvidia-glx
	ati-drivers
	e100
	e1000
	wireless-tools
	pcmcia-cs
	emu10k1
	evms
	linux-wlan-ng
	sys-apps/eject
	genkernel

# same as above, but this time we have a "pkgset". this means that we will fetch and compile
# the desired package
grp/cd2/type: pkgset
grp/cd2/packages:
	pciutils
	hdparm
	hotplug
	aumix
	xfree
	dante
	tsocks
	chkrootkit
	minicom
	lynx
	rpm2targz
	parted
	rdate
	whois
	tcpdump
	cvs
	unzip
	zip
	netcat
	partimage
	DirectFB
	apache
	app-cdr/cdrtools
	gnome
	evolution
	cups
	dev-db/mysql
	dev-lang/ruby
	emacs
	enlightenment
	fluxbox
	kde
	libsdl
	mozilla
	xfce4
	openbox
	openoffice
	sylpheed
	vim
	xemacs
	xmms
	mozilla-firefox
	abiword
	gaim
	tetex
	xcdroast
	samba
	nmap
	gradm
	ettercap
	xchat
	dante
	tsocks
