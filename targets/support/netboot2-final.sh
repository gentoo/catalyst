#!/bin/bash
# Copyright 1999-2005 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/support/netboot2-final.sh,v 1.2 2006/01/16 15:25:08 wolf31o2 Exp $

. ${clst_sharedir}/targets/support/functions.sh
. ${clst_sharedir}/targets/support/filesystem-functions.sh


extract_kernels ${clst_target_path}boot

# Move kernel binaries to ${clst_target_path}kernels, and
# move everything else to ${clst_target_path}kernels/misc
mkdir ${clst_target_path}kernels
mkdir ${clst_target_path}kernels/misc

for x in ${clst_boot_kernel}; do
	mv ${clst_target_path}boot/${x} ${clst_target_path}kernels
	mv ${clst_target_path}boot/${x}.igz ${clst_target_path}kernels/misc
done

rmdir ${clst_target_path}boot

# Any post-processing necessary for each architecture can be done here.  This
# may include things like sparc's elftoaout, x86's PXE boot, etc.
case ${clst_mainarch} in
	alpha)
		sleep 0
		;;
	arm)
		sleep 0
		;;
	hppa)
		sleep 0
		;;
	sparc*)
		sleep 0
		;;
	ia64)
		sleep 0
		;;
	x86|amd64)
		sleep 0
		;;
esac
exit $?
