#!/bin/bash
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/tinderbox/tinderbox-controller.sh,v 1.6 2006/10/02 20:41:54 wolf31o2 Exp $

. ${clst_sharedir}/targets/support/functions.sh

case $1 in
	run)
		shift
		exec_in_chroot ${clst_sharedir}/targets/tinderbox/tinderbox-chroot.sh
	;;
	preclean)
		#exec_in_chroot ${clst_sharedir}/targets/tinderbox/tinderbox-preclean-chroot.sh
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
