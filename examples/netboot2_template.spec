subarch: mips3
version_stamp: 2006.0
target: netboot2
rel_type: default
profile: uclibc/mips
snapshot: 20060107
source_subpath: default/stage3-mips-uclibc-mips3-20051026

boot/kernel: ip22r4k ip22r5k ip27r10k ip28r10k ip30r10k ip32r5k
boot/kernel/ip22r4k/sources: =mips-sources-2.6.14.5
boot/kernel/ip22r5k/sources: =mips-sources-2.6.14.5
boot/kernel/ip27r10k/sources: =mips-sources-2.6.14.5
boot/kernel/ip28r10k/sources: =mips-sources-2.6.14.5
boot/kernel/ip30r10k/sources: =mips-sources-2.6.14.5
boot/kernel/ip32r5k/sources: =mips-sources-2.6.14.5

boot/kernel/ip22r4k/config: /usr/share/genkernel/mips/ip22r4k-2006_0.cf
boot/kernel/ip22r5k/config: /usr/share/genkernel/mips/ip22r5k-2006_0.cf
boot/kernel/ip27r10k/config: /usr/share/genkernel/mips/ip27r10k-2006_0.cf
boot/kernel/ip28r10k/config: /usr/share/genkernel/mips/ip28r10k-2006_0.cf
boot/kernel/ip30r10k/config: /usr/share/genkernel/mips/ip30r10k-2006_0.cf
boot/kernel/ip32r5k/config: /usr/share/genkernel/mips/ip32r5k-2006_0.cf

boot/kernel/ip22r4k/use: -doc
boot/kernel/ip22r5k/use: -doc
boot/kernel/ip27r10k/use: -doc ip27
boot/kernel/ip28r10k/use: -doc ip28
boot/kernel/ip30r10k/use: -doc ip30
boot/kernel/ip32r5k/use: -doc

boot/kernel/ip22r4k/gk_kernargs: --kernel-cross-compile=mips-unknown-linux-gnu- --makeopts=-j2 --initramfs-overlay=/tmp/image
boot/kernel/ip22r5k/gk_kernargs: --kernel-cross-compile=mips-unknown-linux-gnu- --makeopts=-j2 --initramfs-overlay=/tmp/image
boot/kernel/ip27r10k/gk_kernargs: --kernel-cross-compile=mips64-unknown-linux-gnu- --makeopts=-j2 --initramfs-overlay=/tmp/image
boot/kernel/ip28r10k/gk_kernargs: --kernel-cross-compile=mips64-unknown-linux-gnu- --makeopts=-j2 --initramfs-overlay=/tmp/image
boot/kernel/ip30r10k/gk_kernargs: --kernel-cross-compile=mips64-unknown-linux-gnu- --makeopts=-j2 --initramfs-overlay=/tmp/image
boot/kernel/ip32r5k/gk_kernargs: --kernel-cross-compile=mips64-unknown-linux-gnu- --makeopts=-j2 --initramfs-overlay=/tmp/image

netboot2/builddate: 20060107
netboot2/busybox_config: /usr/share/genkernel/mips/nb-busybox.cf

netboot2/use:
	-*
	multicall
	readline
	ssl

netboot2/packages:
	com_err
	dropbear
	dvhtool
	e2fsprogs
	gcc-mips64
	jfsutils
	mdadm
	nano
	ncurses
	openssl
	popt
	portmap
	reiserfsprogs
	rsync
	sdparm
	ss
	ttcp
	uclibc
	util-linux
	wget
	xfsprogs

netboot2/packages/com_err/files:
	/lib/libcom_err.so
	/lib/libcom_err.so.2
	/lib/libcom_err.so.2.1
	/usr/bin/compile_et
	/usr/lib/libcom_err.so

netboot2/packages/dropbear/files:
	/usr/bin/dbclient
	/usr/bin/dbscp
	/usr/bin/dropbearconvert
	/usr/bin/dropbearkey
	/usr/bin/dropbearmulti
	/usr/sbin/dropbear

netboot2/packages/dvhtool/files:
	/usr/sbin/dvhtool

netboot2/packages/e2fsprogs/files:
	/bin/chattr
	/bin/lsattr
	/bin/uuidgen
	/lib/libblkid.so
	/lib/libblkid.so.1
	/lib/libblkid.so.1.0
	/lib/libe2p.so
	/lib/libe2p.so.2
	/lib/libe2p.so.2.3
	/lib/libext2fs.so
	/lib/libext2fs.so.2
	/lib/libext2fs.so.2.4
	/lib/libuuid.so
	/lib/libuuid.so.1
	/lib/libuuid.so.1.2
	/sbin/badblocks
	/sbin/blkid
	/sbin/debugfs
	/sbin/dumpe2fs
	/sbin/e2fsck
	/sbin/e2image
	/sbin/e2label
	/sbin/filefrag
	/sbin/findfs
	/sbin/fsck
	/sbin/fsck.ext2
	/sbin/fsck.ext3
	/sbin/logsave
	/sbin/mke2fs
	/sbin/mkfs.ext2
	/sbin/mkfs.ext3
	/sbin/resize2fs
	/sbin/tune2fs
	/usr/lib/e2initrd_helper
	/usr/lib/libblkid.so
	/usr/lib/libe2p.so
	/usr/lib/libext2fs.so
	/usr/lib/libuuid.so
	/usr/sbin/mklost+found

netboot2/packages/jfsutils/files:
	/sbin/fsck.jfs
	/sbin/jfs_fsck
	/sbin/jfs_mkfs
	/sbin/jfs_tune
	/sbin/mkfs.jfs

netboot2/packages/mdadm/files:
	/etc/mdadm.conf
	/sbin/mdadm

netboot2/packages/nano/files:
	/bin/nano
	/bin/rnano
	/usr/bin/nano

netboot2/packages/ncurses/files:
	/etc/terminfo
	/lib/libcurses.so
	/lib/libncurses.so
	/lib/libncurses.so.5
	/lib/libncurses.so.5.4
	/usr/bin/toe
	/usr/lib/libcurses.so
	/usr/lib/libform.so
	/usr/lib/libform.so.5
	/usr/lib/libform.so.5.4
	/usr/lib/libmenu.so
	/usr/lib/libmenu.so.5
	/usr/lib/libmenu.so.5.4
	/usr/lib/libncurses.so
	/usr/lib/libpanel.so
	/usr/lib/libpanel.so.5
	/usr/lib/libpanel.so.5.4
	/usr/lib/terminfo
	/usr/share/tabset/std
	/usr/share/tabset/stdcrt
	/usr/share/tabset/vt100
	/usr/share/tabset/vt300
	/usr/share/terminfo/a/ansi
	/usr/share/terminfo/d/dumb
	/usr/share/terminfo/e/eterm
	/usr/share/terminfo/l/linux
	/usr/share/terminfo/r/rxvt
	/usr/share/terminfo/s/screen
	/usr/share/terminfo/s/sun
	/usr/share/terminfo/v/vt100
	/usr/share/terminfo/v/vt102
	/usr/share/terminfo/v/vt200
	/usr/share/terminfo/v/vt220
	/usr/share/terminfo/v/vt52
	/usr/share/terminfo/x/xterm
	/usr/share/terminfo/x/xterm-color
	/usr/share/terminfo/x/xterm-xfree86

netboot2/packages/openssl/files:
	/usr/lib/libcrypto.so
	/usr/lib/libcrypto.so.0
	/usr/lib/libcrypto.so.0.9.7
	/usr/lib/libssl.so
	/usr/lib/libssl.so.0
	/usr/lib/libssl.so.0.9.7

netboot2/packages/popt/files:
	/usr/lib/libpopt.so
	/usr/lib/libpopt.so.0
	/usr/lib/libpopt.so.0.0.0

netboot2/packages/portmap/files:
	/sbin/portmap

netboot2/packages/reiserfsprogs/files:
	/sbin/fsck.reiserfs
	/sbin/mkfs.reiserfs
	/sbin/mkreiserfs
	/sbin/reiserfsck
	/sbin/reiserfstune

netboot2/packages/rsync/files:
	/usr/bin/rsync

netboot2/packages/sdparm/files:
	/usr/bin/sdparm

netboot2/packages/ss/files:
	/lib/libss.so
	/lib/libss.so.2
	/lib/libss.so.2.0
	/usr/bin/mk_cmds
	/usr/lib/libss.so

netboot2/packages/ttcp/files:
	/usr/bin/ttcp

netboot2/packages/uclibc/files:
	/etc/ld.so.cache
	/lib/ld-uClibc-0.9.27.so
	/lib/ld-uClibc.so.0
	/lib/libc.so.0
	/lib/libcrypt-0.9.27.so
	/lib/libcrypt.so.0
	/lib/libdl-0.9.27.so
	/lib/libdl.so.0
	/lib/libm-0.9.27.so
	/lib/libm.so.0
	/lib/libnsl-0.9.27.so
	/lib/libnsl.so.0
	/lib/libpthread-0.9.27.so
	/lib/libpthread.so.0
	/lib/libresolv-0.9.27.so
	/lib/libresolv.so.0
	/lib/librt-0.9.27.so
	/lib/librt.so.0
	/lib/libthread_db-0.9.27.so
	/lib/libthread_db.so.1
	/lib/libuClibc-0.9.27.so
	/lib/libutil-0.9.27.so
	/lib/libutil.so.0
	/sbin/ldconfig
	/usr/bin/getent
	/usr/bin/ldd
	/usr/lib/Scrt1.o
	/usr/lib/crt0.o
	/usr/lib/crt1.o
	/usr/lib/crti.o
	/usr/lib/crtn.o
	/usr/lib/libc.so
	/usr/lib/libcrypt.so
	/usr/lib/libdl.so
	/usr/lib/libm.so
	/usr/lib/libnsl.so
	/usr/lib/libpthread.so
	/usr/lib/libresolv.so
	/usr/lib/librt.so
	/usr/lib/libthread_db.so
	/usr/lib/libutil.so

netboot2/packages/util-linux/files:
	/sbin/fdisk
	/sbin/mkfs
	/sbin/mkswap
	/sbin/swapoff
	/sbin/swapon
	/usr/bin/ddate
	/usr/bin/setterm
	/usr/bin/whereis

netboot2/packages/wget/files:
	/usr/bin/wget

netboot2/packages/xfsprogs/files:
	/bin/xfs_copy
	/bin/xfs_growfs
	/bin/xfs_info
	/lib/libhandle.so
	/lib/libhandle.so.1
	/lib/libhandle.so.1.0.3
	/sbin/fsck.xfs
	/sbin/mkfs.xfs
	/sbin/xfs_repair

# Setting the option overrides the location of the pkgcache
pkgcache_path:

# Setting the option overrides the location of the kerncache
kerncache_path:

