subarch: hppa
version_stamp: 20040227
target: grp
rel_type: default
rel_version: 2004.0
snapshot: 20040227
source_subpath: default-hppa-2004.0/stage3-hppa-20040227
#grp: cd1 cd2
grp: cd1

grp/use:
	-*
	berkdb
	cdr
	crypt
	cups
	gdbm
	gif
	gnome
	gpm
	innodb
	ipv6
	jpeg
	libg++
	mysql
	ncurses
	nls
	pam
	pdflib
	perl
	png
	postgres
	python
	readline
	spell
	ssl
	tpcd
	truetype
	X
	xinerama
	xfs
	xml2
	zlib
	
grp/cd1/type: pkgset
grp/cd1/packages:
	iptables
	gpm
	ppp
	pciutils
	hdparm
	hotplug
	vcron
	sysklogd
	metalog
	syslog-ng
	raidtools
	lvm-user
	dosfstools
	hppa-sources
	hppa-dev-sources
	gentoolkit
	minicom
	iptraf
	gdb
	strace
	ifstat
	lynx
	mtr
	rpm2targz
	parted
	rdate
	ntp
	whois
	tcpdump
	cvs
	unzip
	zip
	netcat
	lftp
	screen
	nfs-utils
	mirrorselect
	ufed
	apache
	app-cdr/cdrtools
	aumix
	cups
	dev-db/mysql
	dev-db/postgresql
	dev-lang/ruby
	vim
	samba
	nmap
	irssi
	mailx
	exim
	bind
	radvd
	sendmail
	iproute
	pure-ftpd
	proftpd
	squid
	xfsprogs
	
#grp/cd2/type: pkgset
#grp/cd2/packages:
	xfree
	rp-pppoe
	xfce4
	sylpheed
	kde
	dev-lang/tcl
	dev-lang/tk
	gnome
	nautilus
	evolution
	fluxbox
	libsdl
	xmms
	xchat
	bitchx
	links
	tetex
	mod_php
	emacs
	mc
