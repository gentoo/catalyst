## livecd-stage2 example specfile
## used to build a livecd-stage2 iso image

## John Davis <zhen@gentoo.org>
## Chris Gianelloni <wolf31o2@gentoo.org>

# subarch can be any of the supported Catalyst subarches (like athlon-xp). Refer
# to the catalyst reference manual:
# (http://www.gentoo.org/proj/en/releng/catalyst) for supported arches.
# example:
# subarch: athlon-xp
subarch:

# version stamp is an identifier for the build. can be anything you want it
# to be, but it is usually a date.
# example:
# version_stamp: 2004.3
version_stamp: 

# target specifies what type of build Catalyst is to do.
# check the catalyst reference manual for supported targets.
# example:
# target: livecd-stage2
target: livecd-stage2

# rel_type defines what kind of build we are doing.
# usually, default will suffice.
# example:
# rel_type: default
rel_type:

# system profile used to build the media
# example:
# profile: default-linux/x86/2004.3
profile:

# which snapshot to use
# example:
# snapshot: 20041022
snapshot:

# where the seed stage comes from, path is relative to $clst_sharedir (catalyst.conf)
# example:
# default/stage3-x86-2004.3
source_subpath:

# which cdfs to use. valid values are:
# zisofs, squashfs, cloop, gcloop, and noloop
livecd/cdfstype: squashfs

# archscript and runscript to use. DO NOT CHANGE THESE UNLESS YOU KNOW WHAT YOU ARE DOING.
livecd/archscript: /usr/lib/catalyst/livecd/runscript/x86-archscript.sh
livecd/runscript: /usr/lib/catalyst/livecd/runscript/default-runscript.sh

# bootloader for the LiveCD - DO NOT CHANGE UNLESS YOU KNOW WHAT YOU ARE DOING.
livecd/cdtar: /usr/lib/catalyst/livecd/cdtar/isolinux-2.08-memtest86-cdtar.tar.bz2

# (optional) create a iso and place it in the location specified
# livecd/iso: /tmp/gentoo.iso

# (optional) run this script in the LiveCD chroot to tweak the LiveCD fs
# livecd/fsscript: /tmp/myscript.sh

# (optional) files to be added to the final livecd product. note that they
# *are not* in the loopback fs itself, but in /mnt/cdrom when the cd is booted.
# the layout is in the overlay mirrors how it will be on the LiveCD.
# livecd/overlay: /tmp/files_for_livecd

# (optional) "global" arguments that are to be passed to genkernel
# livecd/gk_mainargs: --makeopts=-j3

# (optional) tweaks things such as the MOTD for release LiveCDs
# livecd/type: gentoo-release-universal

# (optional) the standard Gentoo release MOTD is included with Catalyst
# livecd/motd: /usr/lib/catalyst/livecd/files/motd.txt

# (optional) list of modules that you want to blacklist for hotplug
# livecd/modblacklist: 8139cp

# (optional) splash type you wish to use on your LiveCD,  this can be either
# gensplash or bootsplash
# livecd/splash_type: gensplash

# (optional) splash theme to use - must be present in /etc/splash or
# /etc/bootsplash of the LiveCD before the initrd is completed.
# livecd/splash_theme: livecd-2004.3

# (optional) list of services to add to the specified runlevel
# livecd/rcadd: mkxf86config:default alsasound:default

# (optional) list of services to delete from the specified runlevel
# livecd/rcdel: net.eth0:boot

# (optional) xinitrc to use on the livecd
# livecd/xinitrc: /tmp/livecd_xinitrc

# (optional) directory that is to be overlayed on the livecd rootfs
# (the booted fs)
# livecd/root_overlay: /tmp/livecd-root-overlay

# (optional) if you want your livecd to use udev instead of devfs,
# uncomment this line
# livecd/devmanager: udev

# let catalyst know the names of the kernels that you want it to build
boot/kernel: gentoo smp

# for the first kernel (gentoo), let catalyst know what sources to use and
# what kernel config to use
boot/kernel/gentoo/sources: sys-kernel/gentoo-sources
boot/kernel/gentoo/config:

# (optional) per-kernel arguments for genkernel
# boot/kernel/gentoo/gk_kernargs: --makeopts=-j2

# same as the gentoo kernel above, just different data
boot/kernel/smp/sources: sys-kernel/gentoo-dev-sources
boot/kernel/smp/config:

# (optional) per-kernel arguments for genkernel
# boot/kernel/smp/gk_kernargs: --makeopts=-j1

# this next line sets any USE settings you want exported to the environment for
# your kernel build *and* during the build of any kernel-dependent packages
boot/kernel/gentoo/use: pcmcia usb
boot/kernel/smp/use: pcmcia usb

# use this next option to add an extension to the name of your kernel. This
# allows you to have 2 identical kernels on the livecd built with different
# options, and each with their own modules dir in /lib/modules (otherwise
# the second kernel would overwrite the first modules directory.
boot/kernel/gentoo/extraversion: gentoo
boot/kernel/smp/extraversion: smp

# this next line is for merging kernel-dependent packages after your kernel
# is built. This is where you merge third-party ebuilds that contain kernel
# modules.
boot/kernel/gentoo/packages:
	pcmcia-cs
	speedtouch
	slmodem
	globespan-adsl
	hostap-driver
	hostap-utils
	ipw2100
	
boot/kernel/smp/packages:
	pcmcia-cs
	speedtouch
	slmodem
	globespan-adsl
	hostap-driver
	hostap-utils
	ipw2100

# remove gcc from the list if you want distcc
livecd/unmerge:
	autoconf
	automake
	gcc
	bin86
	binutils
	libtool
	m4
	bison
	ld.so
	make
	perl
	patch
	linux-headers
	man-pages
	sash
	bison
	flex
	gettext
	texinfo
	ccache
	addpatches
	man
	groff
	lib-compat
	python
	miscfiles

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
	/var/log/emerge.log
	/var/log/genkernel.log

