# Copyright 1999-2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/livecd-stage2/Attic/livecd-stage2-cdfs.sh,v 1.1 2005/04/04 17:48:33 rocket Exp $
. ${clst_sharedir}/targets/support/functions.sh
. ${clst_sharedir}/targets/support/filesystem-functions.sh
#. ${clst_sharedir}/targets/${clst_target}/${clst_mainarch}-archscript.sh

#source ${clst_livecd_archscript}
## START RUNSCRIPT

loopret=1
case ${clst_livecd_cdfstype} in
	normal)
		create_normal_loop
		loopret=$?
	;;
	zisofs)
		create_zisofs
		loopret=$?
	;;
	noloop)
		create_noloop
		loopret=$?
	;;
	gcloop)
		create_gcloop
		loopret=$?
	;;
	squashfs)
		create_squashfs
		loopret=$?
	;;
esac
exit $loopret
