subarch: x86
version_stamp: 20040209
target: livecd-stage2
rel_type: default
rel_version: 1.4
snapshot: 20040209
source_subpath: default-x86-1.4/livecd-stage1-x86-20040209
livecd/cdfstype: zisofs
livecd/archscript: examples/livecd/runscript/x86-archscript.sh
livecd/runscript: examples/livecd/runscript/default-runscript-with-x.sh
livecd/cdtar: examples/livecd/cdtar/isolinux-2.08-cdtar.tar.bz2
boot/kernel: gentoo
#boot/kernel/gentoo/extraversion: foo
boot/kernel/gentoo/sources: =sys-kernel/xfs-sources-2.4.24
boot/kernel/gentoo/packages: pcmcia-cs nforce-net linux-wlan-ng slmodem
boot/kernel/gentoo/config: examples/livecd/x86/config-2.4.24-x86
livecd/unmerge:
	autoconf automake bin86 binutils libtool m4 bison make patch linux-headers man-pages
	sash bison flex texinfo ccache addpatches man groff lib-compat miscfiles ucl
	kdeedu mozilla epiphany bug-buddy
livecd/empty:
	/var/tmp
	/var/cache
	/var/db
	/var/empty
	/var/cache
	/tmp
	/root
	/usr/portage
	/usr/share/ss
	/usr/share/state
	/usr/share/texinfo
#	/usr/lib/python2.2
#	/usr/share/gettext
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
	/usr/lib/gcc-lib/*/*/libgcj*
	
