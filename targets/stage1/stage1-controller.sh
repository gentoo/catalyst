#!/bin/bash
# Copyright 1999-2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/stage1/stage1-controller.sh,v 1.1 2005/04/04 17:48:33 rocket Exp $
. ${clst_sharedir}/targets/support/functions.sh

case $1 in
	enter)
	;;

	run)
		cp ${clst_sharedir}/targets/stage1/build.py ${clst_chroot_path}/tmp
		
		# set up "ROOT in chroot" dir
		install -d ${clst_chroot_path}/${clst_root_path}/etc
		
		# set up make.conf and make.profile link in "ROOT in chroot":
		copy_to_chroot ${clst_chroot_path}/etc/make.conf /${clst_root_path}/etc
		copy_to_chroot ${clst_chroot_path}/etc/make.profile /${clst_root_path}/etc
		
		# enter chroot, execute our build script
		exec_in_chroot ${clst_sharedir}/targets/${clst_target}/${clst_target}-chroot.sh || exit 1
	;;

	preclean)
		exec_in_chroot ${clst_sharedir}/targets/${clst_target}/${clst_target}-preclean-chroot.sh /tmp/stage1root || exit 1

	;;

	clean)
		# clean out man, info and doc files
		rm -rf usr/share/{man,doc,info}/*
		# zap all .pyc and .pyo files
		find -iname "*.py[co]" -exec rm -f {} \;
		# cleanup all .a files except libgcc.a, *_nonshared.a and /usr/lib/portage/bin/*.a
		find -iname "*.a" | grep -v 'libgcc.a' | grep -v 'nonshared.a' | grep -v '/usr/lib/portage/bin/' | grep -v 'libgcc_eh.a' | xargs rm -f
	;;
	
	*)
		exit 1
	;;

esac
exit 0

