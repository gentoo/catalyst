#!/bin/bash
# Copyright 1999-2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/tinderbox/tinderbox-controller.sh,v 1.2 2005/04/27 17:44:58 rocket Exp $

. ${clst_sharedir}/targets/support/functions.sh

case $1 in
	run)
		shift
		exec_in_chroot ${clst_sharedir}/targets/tinderbox/tinderbox-chroot.sh
	;;

	preclean)
		#exec_in_chroot ${clst_sharedir}/targets/grp/tinderbox-preclean-chroot.sh
		delete_from_chroot /tmp/chroot-functions.sh
	;;

	clean)
		exit 0
	;;

	*)
		exit 1
	;;
	
esac

exit $?
