#!/bin/bash
# Copyright 1999-2003 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/grp/grp-chroot.sh,v 1.7 2004/09/08 15:58:12 zhen Exp $

/usr/sbin/env-update
source /etc/profile

if [ -f /tmp/envscript ]
then
	source /tmp/envscript
fi

if [ -n "${clst_CCACHE}" ]
then
	export clst_myfeatures="${clst_myfeatures} ccache"
	emerge --oneshot --nodeps -b -k ccache || exit 1
fi

if [ -n "${clst_DISTCC}" ]
then   
	export clst_myfeatures="${clst_myfeatures} distcc"
	export DISTCC_HOSTS="${clst_distcc_hosts}"

	USE="-gnome -gtk" emerge --oneshot --nodeps -b -k distcc || exit 1
	/usr/bin/distcc-config --install 2>&1 > /dev/null
	/usr/bin/distccd 2>&1 > /dev/null
fi

# setup the environment
export FEATURES="${clst_myfeatures}"
export CONFIG_PROTECT="-*"

## START BUILD
USE="build" emerge portage

#turn off auto-use:
export USE_ORDER="env:conf:defaults"
	
if [ "${clst_grp_type}" = "pkgset" ]
then
	unset DISTDIR
	export PKGDIR="/tmp/grp/${clst_grp_target}"

	if [ -n "${clst_VERBOSE}" ]
	then
		emerge --usepkg --buildpkg --noreplace -vp ${clst_grp_packages} || exit 1
		sleep 15
	fi
	
	emerge --usepkg --buildpkg --noreplace ${clst_grp_packages} || exit 1
else
	unset DISTDIR
	#don't grab MS core fonts, etc.
	export USE="${USE} bindist"
	
	DISTDIR="/tmp/grp/${clst_grp_target}" emerge --fetchonly ${clst_grp_packages} || exit 1
	unset PKGDIR
fi
