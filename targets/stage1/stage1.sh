# Copyright 1999-2003 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/stage1/Attic/stage1.sh,v 1.5 2003/10/30 20:00:04 drobbins Exp $

case $1 in
enter)
	$clst_CHROOT $clst_chroot_path /bin/bash
	;;
run)
	cp ${clst_sharedir}/targets/stage1/stage1-chroot.sh ${clst_chroot_path}/tmp
	cp ${clst_sharedir}/targets/stage1/build.sh ${clst_chroot_path}/tmp
	# set up "ROOT in chroot" dir
	install -d ${clst_chroot_path}/tmp/stage1root/etc
	# set up make.conf and make.profile link in "ROOT in chroot":
	cp ${clst_chroot_path}/etc/make.conf ${clst_chroot_path}/tmp/stage1root/etc
	cp -a ${clst_chroot_path}/etc/make.profile ${clst_chroot_path}/tmp/stage1root/etc
	# enter chroot, execute our build script
	$clst_CHROOT ${clst_chroot_path} /tmp/stage1-chroot.sh build /tmp/stage1root
	[ $? -ne 0 ] && exit 1
	;;
clean)
	$clst_CHROOT ${clst_chroot_path} /tmp/stage1-chroot.sh clean /tmp/stage1root
	[ $? -ne 0 ] && exit 1
	echo
	;;
*)
	exit 1
	;;
esac
exit 0

