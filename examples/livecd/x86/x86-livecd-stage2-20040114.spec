subarch: x86
version_stamp: 20040114
target: livecd-stage2
rel_type: default
rel_version: 1.4
snapshot: 20040114
source_subpath: default-x86-1.4/livecd-stage1-x86-20040114
livecd/looptype: normal
livecd/archscript: examples/livecd/runscript/x86-archcript.sh
livecd/runscript: examples/livecd/runscript/default-runscript.sh
livecd/cdtar: examples/livecd/cdtar/isolinux-2.08-cdtar.tar.bz2
boot/kernel: gentoo
boot/kernel/gentoo/sources: =sys-kernel/gentoo-dev-sources-2.6.1-r1
boot/kernel/gentoo/config: examples/livecd/x86/config-2.6.1-x86
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
