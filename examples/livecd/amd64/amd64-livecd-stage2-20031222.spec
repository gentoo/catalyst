subarch: amd64 
version_stamp: 20031222
target: livecd-stage2
rel_type: default
rel_version: 1.4
snapshot: 20031222
source_subpath: default-amd64-1.4/livecd-stage1-amd64-20031222
boot/kernel: gentoo
boot/kernel/gentoo/sources: =sys-kernel/gentoo-dev-sources-2.6.0
boot/kernel/gentoo/config: /home/drobbins/cvs/gentoo/src/catalyst/kconfig/config-2.6.0-amd64
livecd/cdfstype: zisofs
livecd/cdtar: /home/drobbins/cvs/gentoo/src/catalyst/examples/isolinux-2.08-cdtar.tar.bz2
livecd/runscript: /home/drobbins/cvs/gentoo/src/catalyst/examples/runscript.sh
livecd/archscript: /home/drobbins/cvs/gentoo/src/catalyst/examples/x86-archscript.sh
livecd/unmerge:
	autoconf automake bin86 binutils libtool m4 bison ld.so make perl patch linux-headers man-pages
	sash bison flex gettext texinfo ccache addpatches man groff lib-compat gcc python miscfiles ucl
livecd/empty:
	/var/tmp
	/var/cache
	/var/db
	/var/empty
	/var/cache
	/var/lock
	/tmp
	/usr/portage
	/usr/share/man
	/usr/share/info
	/usr/share/unimaps
	/usr/include
	/usr/share/zoneinfo
	/usr/share/dict
	/usr/share/doc
	/usr/share/ss
	/usr/share/state
	/usr/share/texinfo
	/usr/lib/python2.2
	/usr/lib/portage
	/usr/share/gettext
	/usr/share/i18n
	/usr/share/rfc
	/usr/X11R6/man
	/usr/X11R6/include
	/usr/X11R6/lib/X11/config
	/usr/X11R6/lib/X11/etc
	/usr/X11R6/lib/X11/doc
	/usr/src
	/usr/share/doc
	/usr/share/man
livecd/rm:
	/lib/*.a
	/usr/lib/*.a
	/usr/lib/gcc-lib/*/*/libgcj*
	/usr/X11R6/lib/*.a
