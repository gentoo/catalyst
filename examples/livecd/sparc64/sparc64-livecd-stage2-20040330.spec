subarch: sparc64
version_stamp: 20040330
target: livecd-stage2
rel_type: default
rel_version: 2004.0
profile: default-sparc64-2004.0
snapshot: 20040330
source_subpath: default/livecd-stage1-sparc64-20040330
livecd/cdfstype: zisofs
livecd/archscript: examples/livecd/runscript/sparc64-archscript.sh
livecd/runscript: examples/livecd/runscript/default-runscript.sh
livecd/cdtar: examples/livecd/cdtar/silo-1.3.1-cdtar.tar.bz2
boot/kernel: gentoo gentoo-smp
boot/kernel/gentoo/sources: =sys-kernel/sparc-sources-2.4.25
boot/kernel/gentoo/config: examples/livecd/sparc64/config-2.4.25-sparc64-up
boot/kernel/gentoo/extraversion: up
boot/kernel/gentoo/use: ultra1
boot/kernel/gentoo-smp/sources: =sys-kernel/sparc-sources-2.4.25
boot/kernel/gentoo-smp/config: examples/livecd/sparc64/config-2.4.25-sparc64-smp
boot/kernel/gentoo-smp/extraversion: smp
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
	/usr/lib/python2.3
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
