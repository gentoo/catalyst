#!/bin/bash
# Copyright 1999-2003 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/grp/grp-chroot.sh,v 1.2 2004/04/14 14:27:38 zhen Exp $

/usr/sbin/env-update
source /etc/profile

if [ -f /tmp/envscript ]
then
	source /tmp/envscript
	rm -f /tmp/envscript
fi

if [ -n "${clst_CCACHE}" ]
then
	export clst_myfeatures="${clst_myfeatures} ccache"
	emerge --oneshot --nodeps ccache || exit 1
fi

if [ -n "${clst_DISTCC}" ]
then   
	export clst_myfeatures="${clst_myfeatures} distcc"
	export DISTCC_HOSTS="${clst_distcc_hosts}"

	USE="-gnome -gtk" emerge --oneshot --nodeps distcc || exit 1
	echo "distcc:x:7980:2:distccd:/dev/null:/bin/false" >> /etc/passwd
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
	emerge --usepkg --buildpkg --noreplace ${clst_grp_packages} || exit 1
else
	unset DISTDIR
	#don't grab MS core fonts, etc.
	export USE="${USE} bindist"
	#first grab to the normal distdir
	
	## why don't we just set distdir first and fetch once???
	DISTDIR="/tmp/grp/${clst_grp_target}" emerge --fetchonly ${clst_grp_packages} || exit 1
	#export DISTDIR="/tmp/grp/${clst_grp_target}"
	#export OLD_MIRRORS="${GENTOO_MIRRORS}"
	#export GENTOO_MIRRORS="/usr/portage/distfiles"
	#now grab them again, but with /usr/portage/distfiles as the primary mirror (local grab)
	#emerge --fetchonly ${clst_grp_packages} || exit 1
	#restore original GENTOO_MIRRORS setting, if any
	#export GENTOO_MIRRORS="${OLD_MIRRORS}"
	unset PKGDIR
fi
