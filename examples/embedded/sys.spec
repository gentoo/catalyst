subarch: x86
version_stamp: embedded
target: embedded
rel_type: default
rel_version: 1.4
snapshot: embedded
source_subpath: default-x86-1.4/stage3-x86-20040202
distcc_hosts: 10.1.1.6 10.1.1.51 10.1.1.21

embedded/runscript: scripts/root.sh
embedded/use:
		links
		devfs
		-initrd
		berkdb
		-gdbm
		-doc
		-pam
		-kerberos
		-selinux
		-skey
embedded/rm:
		/usr/share
		/usr/include
		/usr/lib/gconv
		/usr/lib/locale
		/var/db/pkg
		/var/edb

embedded/packages:
		sys-kernel/linux-headers
		sys-libs/glibc
		sys-apps/baselayout-lite
		sys-apps/busybox
		sys-apps/tinylogin
		net-misc/dhcpcd
		sys-libs/zlib
		=dev-libs/openssl-0.9.7d
		=net-misc/openssh-3.7.1_p2-r1
		sys-apps/parted
		sys-fs/e2fsprogs
		sys-fs/devfsd
		sys-devel/libperl
		=dev-lang/perl-5.8.2-r1
		
embedded/unmerge:
		sys-kernel/linux-headers

