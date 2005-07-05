# Copyright 1999-2005 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/livecd-stage1/livecd-stage1-controller.sh,v 1.8 2005/07/05 21:53:41 wolf31o2 Exp $

. ${clst_sharedir}/targets/support/functions.sh

## START RUNSCRIPT

case $1 in
	build_packages)
		shift
		export clst_packages="$*"
		exec_in_chroot ${clst_sharedir}/targets/${clst_target}/${clst_target}-chroot.sh
		;;

	clean)
		find ${clst_chroot_path}/usr/lib -iname "*.pyc" -exec rm -f {} \;
		;;
esac
exit $?
