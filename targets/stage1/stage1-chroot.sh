#!/bin/bash
# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/stage1/stage1-chroot.sh,v 1.16 2004/06/04 14:03:46 zhen Exp $
		
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
	/usr/bin/distcc-config --install 2>&1 > /dev/null
	/usr/bin/distccd 2>&1 > /dev/null
fi

if [ -n "${clst_PKGCACHE}" ]
then
		export clst_myemergeopts="--usepkg --buildpkg"
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

USE="-* build" emerge ${clst_myemergeopts} --noreplace ${clst_buildpkgs} || exit 1

# if baselayout did not fix up /dev, we do it
# THIS SHOULD BE TEMPORARY CODE - NOT A SOLUTION
if [ ! -d ${ROOT}/dev ]
then
	case ${clst_mainarch} in
		x86)
			clst_devtype=i386
			;;
		ppc)
			clst_devtype=powerpc
			;;
		ppc64)
			clst_devtype=powerpc
			;;
		sparc)
			clst_devtype=sparc
			;;
		sparc64)
			clst_devtype=sparc
			;;
		alpha)
			clst_devtype=alpha
			;;
		s390)
			clst_devtype=s390
			;;
		amd64)
			clst_devtype=i386
			;;
		hppa)
			clst_devtype=hppa
			;;
		ia64)
			clst_devtype=ia64
			;;
		mips)
			clst_devtype=mips
			;;
		arm)
			clst_devtype=arm
			;;
		*)
			echo "!!! Catalyst mainarch ${clst_mainarch} not supported" && exit 1
			;;
	esac

	mkdir -p ${ROOT}/dev
	cd ${ROOT}/dev
	MAKEDEV generic-${clst_devtype}
fi
