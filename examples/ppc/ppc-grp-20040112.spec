subarch: ppc
version_stamp: 20040112
target: grp
rel_type: default
rel_version: 1.4
snapshot: 20040112
source_subpath: default-ppc-1.4/stage3-ppc-20040112
grp: cd1 cd2 src

grp/use: 
	gtk2 
	gnome 
	kde 
	qt 
	bonobo 
	cdr 
	directfb
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

grp/cd1/type: pkgset
grp/cd1/packages:
	iptables
	gpm
	rp-pppoe
	ppp
#	wvdial (not building correctly)
	pciutils
	hdparm
	hotplug
	pmud
	pbbuttonsd
	powerprefs
	aumix
	xfree
	iputils
	vcron
	sysklogd
	metalog
	syslog-ng
	raidtools
	mac-fdisk
#xfsprogs
	reiserfsprogs
	lvm-user
	dosfstools
	yaboot
	quik
	ppc-sources
	ppc-sources-benh
	ppc-sources-dev
	ppc-development-sources
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
	partimage
	lukemftp
	lcrzoex
#	genkernel
#We have to switch to xautoconf
	xeasyconf
	genflags
	screen
	joe
	vile
	nfs-utils
	mirrorselect
	ufed	
	dev-lang/tcl
	dev-lang/tk

	grp/cd2/type: pkgset
	grp/cd2/packages:
	DirectFB
	apache
	app-cdr/cdrtools
	gnome
	gtkpbbuttons
	powerprefs
	evolution
	cups
	dev-db/mysql
	dev-db/postgresql
	dev-lang/ruby
	emacs
#enlightenment has a build problem if USER!=root
#	enlightenment
	fluxbox
	kde
	libsdl
	links
	mozilla
#will be unmasked asap
#xfce4
	openbox
# gentoo-ppc prefers the ximian flavour, to be unmasked asap
	openoffice-ximian
	sylpheed
	vim
	xemacs
	xmms
#use interactions?
	mozilla-firebird
	abiword
	gaim
	tetex
	xcdroast
#endian issue
#	kdrive
	samba
	nmap
	gradm
	gradm2
	ettercap
	xchat

	grp/src/type: srcset
	grp/src/packages:
#isdn4k-utils was a binary pkg in 1.4, so we will need to get docs updated
#since it's kernel-dependent? maybe?
	iproute
	wireless-tools
	pcmcia-cs
#not yet on stable
#evms
	linux-wlan-ng
	mol


