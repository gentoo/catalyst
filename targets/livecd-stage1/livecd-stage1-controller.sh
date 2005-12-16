# Copyright 1999-2005 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/livecd-stage1/livecd-stage1-controller.sh,v 1.10 2005/12/16 19:32:31 wolf31o2 Exp $

. ${clst_sharedir}/targets/support/functions.sh

## START RUNSCRIPT

case $1 in
	build_packages)
		shift
		export clst_packages="$*"
		if [ "${clst_livecd_type}" = "gentoo-release-livecd" ]
		then
			mkdir -p ${clst_chroot_path}/usr/livecd
			echo "${clst_packages}" > \
				${clst_chroot_path}/usr/livecd/grppkgs.txt
		fi
		exec_in_chroot \
			${clst_sharedir}/targets/${clst_target}/${clst_target}-chroot.sh
		;;
	clean)
		find ${clst_chroot_path}/usr/lib -iname "*.pyc" -exec rm -f {} \;
		;;
esac
exit $?
