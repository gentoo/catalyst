#!/bin/bash
# Copyright 1999-2005 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/grp/grp-chroot.sh,v 1.18 2005/07/07 18:48:08 rocket Exp $

. /tmp/chroot-functions.sh

# check portage version in seed stage
check_portage_version

update_env_settings

[ -f /tmp/envscript ] && source /tmp/envscript

setup_myfeatures

# setup the environment
export FEATURES="${clst_myfeatures}"
export CONFIG_PROTECT="-*"
## START BUILD
setup_portage

#turn off auto-use:
export USE_ORDER="env:pkg:conf:defaults"

unset DISTDIR
#don't grab MS core fonts, etc.
export USE="${USE} ${clst_grp_use}"
	
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
	export USE="${USE} bindist"
	DISTDIR="/tmp/grp/${clst_grp_target}" emerge --fetchonly ${clst_grp_packages} || exit 1
	unset PKGDIR
fi
