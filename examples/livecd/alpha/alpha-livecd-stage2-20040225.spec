subarch: alpha
version_stamp: 20040225
target: livecd-stage2
rel_type: default
rel_version: 1.4
snapshot: 20040225
source_subpath: default-alpha-1.4/livecd-stage1-alpha-20040225
livecd/cdfstype: zisofs
livecd/archscript: /usr/share/doc/catalyst-1.0.1-r1/examples/livecd/runscript/alpha-archscript.sh
livecd/runscript: /usr/share/doc/catalyst-1.0.1-r1/examples/livecd/runscript/default-runscript.sh
livecd/cdtar: /usr/share/doc/catalyst-1.0.1-r1/examples/livecd/cdtar/aboot-0.9-r1-cdtar.tar.bz2
boot/kernel: alpha legacy jensen
boot/kernel/alpha/sources: =sys-kernel/alpha-sources-2.4.21-r4
boot/kernel/alpha/config: /usr/share/doc/catalyst-1.0.1-r1/examples/livecd/alpha/config-2.4.21-r4-alpha
boot/kernel/legacy/sources: =sys-kernel/alpha-sources-2.4.21-r4
boot/kernel/legacy/config: /usr/share/doc/catalyst-1.0.1-r1/examples/livecd/alpha/config-2.4.21-r4-legacy
boot/kernel/jensen/sources: =sys-kernel/alpha-sources-2.4.21-r4
boot/kernel/jensen/config: /usr/share/doc/catalyst-1.0.1-r1/examples/livecd/alpha/config-2.4.21-r4-jensen
livecd/unmerge:
	autoconf automake bin86 binutils libtool m4 bison ld.so make perl
	patch linux-headers man-pages sash bison flex gettext texinfo ccache
	addpatches man groff lib-compat gcc python miscfiles ucl
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
