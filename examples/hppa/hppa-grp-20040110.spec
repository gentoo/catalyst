subarch: hppa
version_stamp: 20040110
target: grp
rel_type: default
rel_version: 1.4
snapshot: 20040110
source_subpath: default-hppa-1.4/stage3-hppa-20040110
grp: cd1 src

grp/use:
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
	lynx
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
	aumix
	apache
	app-cdr/cdrtools
	cups
	dev-db/mysql
	dev-db/postgresql
	dev-lang/ruby
	vim
	emacs
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
	
grp/cd2/type: pkgset
grp/cd2/packages:
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
