subarch: ppc
target: livecd-stage2

rel_type: default
rel_version: 2004.0
snapshot: 20040225
version_stamp: 20040225
source_subpath: default-ppc-2004.0/livecd-stage1-ppc-20040225

livecd/cdfstype: gcloop
livecd/archscript: examples/livecd/runscript/ppc-archscript.sh
livecd/runscript: examples/livecd/runscript/default-runscript.sh
livecd/cdtar: examples/livecd/cdtar/yaboot-1.3.11-cdtar.tar.bz2

boot/kernel: G4 G5 G4-SMP G5-SMP
boot/kernel/G4/sources: =sys-kernel/ppc-development-sources-2.6.3-r2
boot/kernel/G4/config: /usr/src/configs/G4
boot/kernel/G4/use: extlib
boot/kernel/G4/packages: >=sys-apps/pcmcia-cs-3.2.7
boot/kernel/G4/extraversion: G4
boot/kernel/G5/sources: =sys-kernel/ppc-development-sources-2.6.3-r2
boot/kernel/G5/config: /usr/src/configs/G5
boot/kernel/G5/use: extlib
boot/kernel/G5/extraversion: G5
boot/kernel/G4-SMP/sources: =sys-kernel/ppc-development-sources-2.6.3-r2
boot/kernel/G4-SMP/config: /usr/src/configs/G4-SMP
boot/kernel/G4-SMP/use: extlib
boot/kernel/G4-SMP/packages: >=sys-apps/pcmcia-cs-3.2.7
boot/kernel/G4-SMP/extraversion: G4-SMP
boot/kernel/G5-SMP/sources: =sys-kernel/ppc-development-sources-2.6.3-r2
boot/kernel/G5-SMP/use: extlib
boot/kernel/G5-SMP/config: /usr/src/configs/G5-SMP
boot/kernel/G5-SMP/extraversion: G5-SMP

livecd/unmerge:
	autoconf automake binutils libtool m4 bison  make perl patch linux-headers man-pages
	sash bison flex gettext sys-apps/texinfo ccache addpatches man groff lib-compat gcc python miscfiles xfree

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
	/root/.ccache
	
livecd/rm:
	/lib/*.a
	/usr/lib/*.a
	/usr/lib/gcc-lib/*/*/libgcj*
	/usr/X11R6/lib/*.a
