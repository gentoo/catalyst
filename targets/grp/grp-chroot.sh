#!/bin/bash
# Copyright 1999-2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/grp/grp-chroot.sh,v 1.14 2005/01/28 18:37:23 wolf31o2 Exp $

# check portage version in seed stage
portage_version=`/usr/lib/portage/bin/portageq best_version / sys-apps/portage \
	| cut -d/ -f2 | cut -d- -f2,3`
if [ `echo ${portage_version} | cut -d- -f1 | cut -d. -f3` -lt 51 ]
then
	echo "ERROR: Your portage version is too low in your seed stage.  Portage version"
	echo "2.0.51 or greater is required."
	exit 1
fi

/usr/sbin/env-update
source /etc/profile

[ -f /tmp/envscript ] && source /tmp/envscript

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
fi

# setup the environment
export FEATURES="${clst_myfeatures}"
export CONFIG_PROTECT="-*"

## START BUILD
USE="build" emerge portage

#turn off auto-use:
export USE_ORDER="env:pkg:conf:defaults"
	
if [ "${clst_grp_type}" = "pkgset" ]
then
	unset DISTDIR
	export PKGDIR="/tmp/grp/${clst_grp_target}"

	if [ -n "${clst_FETCH}" ]
	then
		export clst_myemergeopts="${clst_myemergeopts} -f"
	fi

	if [ -n "${clst_VERBOSE}" ]
	then
		emerge --usepkg --buildpkg --noreplace --newuse -vp ${clst_myemergeopts} ${clst_grp_packages} || exit 1
		echo "Press any key within 15 seconds to pause the build..."
		read -s -t 15 -n 1
		if [ $? -eq 0 ]
		then
			echo "Press any key to continue..."
			read -s -n 1
		fi
	fi
	
	emerge --usepkg --buildpkg --noreplace --newuse ${clst_myemergeopts} ${clst_grp_packages} || exit 1
else
	unset DISTDIR
	#don't grab MS core fonts, etc.
	export USE="${USE} bindist"
	
	DISTDIR="/tmp/grp/${clst_grp_target}" emerge --fetchonly ${clst_grp_packages} || exit 1
	unset PKGDIR
fi
