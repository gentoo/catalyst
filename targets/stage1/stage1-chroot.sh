#!/bin/bash
# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/stage1/stage1-chroot.sh,v 1.20 2004/08/02 23:23:34 zhen Exp $
		
/usr/sbin/env-update
source /etc/profile

[ -f /tmp/envscript ] && source /tmp/envscript
		
if [ -n "${clst_CCACHE}" ]
then
	export clst_myfeatures="${clst_myfeatures} ccache"	
	emerge -b -k --oneshot --nodeps ccache || exit 1
fi
		
if [ -n "${clst_DISTCC}" ]
then   
	export clst_myfeatures="${clst_myfeatures} distcc"
	export DISTCC_HOSTS="${clst_distcc_hosts}"

	USE="-gtk -gnome" emerge -b -k --oneshot --nodeps distcc || exit 1
	/usr/bin/distcc-config --install 2>&1 > /dev/null
	/usr/bin/distccd 2>&1 > /dev/null
fi

if [ -n "${clst_PKGCACHE}" ]
then
	export clst_myemergeopts="${clst_myemergeopts} --usepkg --buildpkg"
fi

# setup our environment
export FEATURES="${clst_myfeatures}"
export ROOT=${1}
install -d ${ROOT}
		
## START BUILD
export clst_buildpkgs="$(/tmp/build.py)"
STAGE1_USE="$(source /etc/make.profile/make.defaults ; echo ${STAGE1_USE})"

USE="-* build ${STAGE1_USE}" emerge ${clst_myemergeopts} --noreplace ${clst_buildpkgs} || exit 1

if [ -n "${clst_VERBOSE}" ]
then
	USE="-* build" emerge ${clst_myemergeopts} -vp --noreplace ${clst_buildpkgs} || exit 1
	sleep 15
fi

USE="-* build" emerge ${clst_myemergeopts} --noreplace ${clst_buildpkgs} || exit 1
