subarch: amd64
version_stamp: 20040223
target: livecd-stage2
rel_type: default
rel_version: 2004.0
snapshot: 20040223
source_subpath: default-amd64-2004.0/livecd-stage1-amd64-20040223
livecd/cdfstype: zisofs
livecd/archscript: examples/livecd/runscript/x86-archscript.sh
livecd/runscript: examples/livecd/runscript/default-runscript.sh
livecd/cdtar: examples/livecd/cdtar/isolinux-2.08-cdtar.tar.bz2
boot/kernel: gentoo smp emachines
boot/kernel/gentoo/sources: =sys-kernel/gentoo-dev-sources-2.6.3-r2
boot/kernel/gentoo/config: /usr/share/genkernel/x86_64/kernel-config-2.6
boot/kernel/gentoo/packages: >=sys-apps/pcmcia-cs-3.2.7
boot/kernel/gentoo/extraversion: up
boot/kernel/gentoo/kernelopts:
boot/kernel/gentoo/use: -X
boot/kernel/smp/sources: =sys-kernel/gentoo-dev-sources-2.6.3-r2
boot/kernel/smp/config: /usr/share/genkernel/x86_64/kernel-config-2.6-smp
boot/kernel/smp/packages: >=sys-apps/pcmcia-cs-3.2.7
boot/kernel/smp/extraversion: smp
boot/kernel/smp/kernelopts:
boot/kernel/smp/use: -X
boot/kernel/emachines/sources: =sys-kernel/gentoo-dev-sources-2.6.3-r2
boot/kernel/emachines/config: /usr/share/genkernel/x86_64/kernel-config-2.6-emachines
boot/kernel/emachines/packages: >=sys-apps/pcmcia-cs-3.2.7
boot/kernel/emachines/extraversion: emachines
boot/kernel/emachines/use: -X
boot/kernel/emachines/kernelopts: pci=noacpi noapic

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
	/root/.ccache
livecd/rm:
	/lib/*.a
	/usr/lib/*.a
	/usr/lib/gcc-lib/*/*/libgcj*
	/usr/X11R6/lib/*.a
	/usr/share/genkernel
	/usr/share/gtk-doc
	/boot/kernel*
	/boot/initrd*

