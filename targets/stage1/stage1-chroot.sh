#!/bin/bash
# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/stage1/stage1-chroot.sh,v 1.19 2004/07/12 15:01:17 zhen Exp $
		
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
for x in $(/tmp/build.sh)
do
	#echo $x >> /tmp/build.log
	export clst_buildpkgs="${clst_buildpkgs} ${x}"
done

if [ -n "${clst_VERBOSE}" ]
then
	USE="-* build" emerge ${clst_myemergeopts} -vp --noreplace ${clst_buildpkgs} || exit 1
	sleep 15
fi

USE="-* build" emerge ${clst_myemergeopts} --noreplace ${clst_buildpkgs} || exit 1
