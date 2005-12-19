#!/bin/bash
# Copyright 1999-2005 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/stage1/stage1-controller.sh,v 1.6 2005/12/19 15:23:50 wolf31o2 Exp $

. ${clst_sharedir}/targets/support/functions.sh

case $1 in
	enter)
	;;
	run)
		cp ${clst_sharedir}/targets/stage1/build.py ${clst_chroot_path}/tmp
		
		# Setup "ROOT in chroot" dir
		install -d ${clst_chroot_path}/${clst_root_path}/etc
		
		# Setup make.conf and make.profile link in "ROOT in chroot":
		copy_to_chroot ${clst_chroot_path}/etc/make.conf /${clst_root_path}/etc
		copy_to_chroot ${clst_chroot_path}/etc/make.profile \
			/${clst_root_path}/etc
		
		# Enter chroot, execute our build script
		exec_in_chroot \
			${clst_sharedir}/targets/${clst_target}/${clst_target}-chroot.sh \
			|| exit 1
	;;
	preclean)
		# We run gcc-config here this way so it works on all arches.
		if [ -x /usr/bin/gcc-config ]
		then
			mythang=$( cd /etc/env.d/gcc; ls ${clst_CHOST}-* | head -n 1 )
			if [ -z "${mythang}" ]
			then
				mythang=1
			fi
			ROOT=/tmp/stage1root gcc-config ${mythang}
		fi
		# We run binutils-config here so it works on all arches.
		if [ -x /usr/bin/binutils-config ]
		then
			mythang=$( cd /etc/env.d/binutils; ls ${clst_CHOST}-* | head -n 1 )
			if [ -z "${mythang}" ]
			then
				mythang=1
			fi
			ROOT=/tmp/stage1root binutils-config ${mythang}
		fi
		exec_in_chroot ${clst_sharedir}/targets/${clst_target}/${clst_target}-preclean-chroot.sh /tmp/stage1root || exit 1
	;;
	clean)
		# Clean out man, info and doc files
		rm -rf usr/share/{man,doc,info}/*
		# Zap all .pyc and .pyo files
		find -iname "*.py[co]" -exec rm -f {} \;
		# Cleanup all .a files except libgcc.a, *_nonshared.a and
		# /usr/lib/portage/bin/*.a
		find -iname "*.a" | grep -v 'libgcc.a' | grep -v 'nonshared.a' | \
			grep -v '/usr/lib/portage/bin/' | grep -v 'libgcc_eh.a' | xargs \
			rm -f
	;;
	*)
		exit 1
	;;
esac
exit $?
