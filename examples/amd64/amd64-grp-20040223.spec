subarch: amd64 
version_stamp: 20040223
target: grp
rel_type: default
rel_version: 2004.0
snapshot: 20040223
source_subpath: default-amd64-2004.0/stage3-amd64-20040223
grp: src cd2

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
	postgres
	ruby
	tcltk
	acl
	cups
	ldap
	ssl
	tcpd
	-bindist

grp/src/type: srcset
grp/src/packages:
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
	lvm2
	dosfstools
	grub-static
	gentoo-dev-sources
	superadduser
	gentoolkit
#USE effects for these?:
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
#isdn4k-utils was a binary pkg in 1.4, so we will need to get docs updated
#since it's kernel-dependent? maybe?
	isdn4k-utils
	iproute
#nvidia-glx requires nvidia-kernel
	nvidia-kernel
	nvidia-glx
	wireless-tools
	pcmcia-cs
	
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
	apache
	app-cdr/cdrtools
	gnome
	evolution
	cups
	dev-db/mysql
	dev-db/postgresql
	dev-lang/ruby
	emacs
	enlightenment
	fluxbox
	kde
	libsdl
	mozilla
#	openbox
	sylpheed
	vim
	xemacs
	xmms
#use interactions?
	mozilla-firefox
#	gaim
	tetex
	xcdroast
#	kdrive
	samba
	nmap
#	gradm
	xchat

