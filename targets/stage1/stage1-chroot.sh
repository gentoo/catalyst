#!/bin/bash
# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/stage1/stage1-chroot.sh,v 1.13 2004/04/14 22:35:29 zhen Exp $
		
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

	USE="-gtk -gnome" emerge --oneshot --nodeps distcc || exit 1
	echo "distcc:x:7980:2:distccd:/dev/null:/bin/false" >> /etc/passwd
	/usr/bin/distcc-config --install 2>&1 > /dev/null
	/usr/bin/distccd 2>&1 > /dev/null
fi

if [ -n "${clst_PKGCACHE}" ]
then
		export EMERGE_OPTS="--usepkg --buildpkg"
fi
	
# setup our environment
export FEATURES="${clst_myfeatures}"
export ROOT=${1}
install -d ${ROOT}
		
## START BUILD
for x in $(/tmp/build.sh)
do
	echo $x >> /tmp/build.log
	USE="-* build" emerge ${EMERGE_OPTS} --noreplace $x || exit 1
done

# if baselayout did not fix up /dev, we do it
if [ ! -d i${ROOT}/dev ]
then
	mkdir -p ${ROOT}/dev
	cd ${ROOT}/dev
	MAKEDEV generic-i386
fi
