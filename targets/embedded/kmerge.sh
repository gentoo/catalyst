#!/bin/bash
# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/embedded/Attic/kmerge.sh,v 1.1 2005/01/10 01:16:07 zhen Exp $

die() {
	echo "$1"
	exit 1
}

# Script to build each kernel, kernel-related packages
/usr/sbin/env-update
source /etc/profile

[ -n "${clst_ENVSCRIPT}" ] && source /tmp/envscript
export CONFIG_PROTECT="-*"
rm -f /usr/src/linux

#set the timezone for the kernel build
rm /etc/localtime
ln -s /usr/share/zoneinfo/UTC /etc/localtime

[ -e "/var/tmp/${clst_kname}.use" ] && export USE="$( cat /var/tmp/${clst_kname}.use )" || unset USE
[ -e "/var/tmp/${clst_kname}.gk_kernargs" ] && source /var/tmp/${clst_kname}.gk_kernargs
# Don't use pkgcache here, as the kernel source may get emerge with different USE variables
# (and thus different patches enabled/disabled.) Also, there's no real benefit in using the
# pkgcache for kernel source ebuilds.
	
emerge "${clst_ksource}" || exit 1
[ ! -e /usr/src/linux ] && die "Can't find required directory /usr/src/linux"
	
#if catalyst has set NULL_VALUE, extraversion wasn't specified so we skip this part
if [ "${clst_kextversion}" != "NULL_VALUE" ]
then
	sed -i -e "s:EXTRAVERSION \(=.*\):EXTRAVERSION \1-${clst_kextversion}:" /usr/src/linux/Makefile
fi
	
if [ -n "${clst_CCACHE}" ]
then
	#enable ccache for genkernel
	export PATH="/usr/lib/ccache/bin:${PATH}"
fi

# grep out the kernel version so that we can do our modules magic
VER=`grep ^VERSION\ \= /usr/src/linux/Makefile | awk '{ print $3 };'`
PAT=`grep ^PATCHLEVEL\ \= /usr/src/linux/Makefile | awk '{ print $3 };'`
SUB=`grep ^SUBLEVEL\ \= /usr/src/linux/Makefile | awk '{ print $3 };'`
EXV=`grep ^EXTRAVERSION\ \= /usr/src/linux/Makefile | sed -e "s/EXTRAVERSION =//" -e "s/ //g"`
clst_fudgeuname=${VER}.${PAT}.${SUB}${EXV}

# now we merge any kernel-dependent packages
if [ -e "/var/tmp/${clst_kname}.packages" ]
then
	for x in $( cat /var/tmp/${clst_kname}.packages )
	do
		# we don't want to use the pkgcache for these since the results
		# are kernel-dependent.
		clst_kernel_merge="${clst_kernel_merge} ${x}"
	done
fi

echo "genkernel action is set to: ${clst_gk_action}"

if [ -n "${clst_livecd_bootsplash}" ]
then
	genkernel --debuglevel=4 --bootsplash=${clst_livecd_bootsplash} \
		--callback="emerge ${clst_kernel_merge}" ${clst_livecd_gk_mainargs} \
		${clst_embedded_gk_kernargs} --kerneldir=/usr/src/linux \
		--kernel-config=/var/tmp/${clst_kname}.config \
		--minkernpackage=/tmp/binaries/${clst_kname}.tar.bz2 \
		${clst_gk_action} || exit 1
else
	genkernel --debuglevel=4 --callback="emerge ${clst_kernel_merge}" \
		${clst_embedded_gk_mainargs} ${clst_embedded_gk_kernargs} \
		--kerneldir=/usr/src/linux --kernel-config=/var/tmp/${clst_kname}.config \
		--minkernpackage=/tmp/binaries/${clst_kname}.tar.bz2 \
		${clst_gk_action} || exit 1
fi

/sbin/modules-update --assume-kernel=${clst_fudgeuname}
		
#now the unmerge... (wipe db entry)
emerge -C "${clst_ksource}"
unset USE
