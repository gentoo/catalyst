#!/bin/bash
# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/livecd/runscript-support/Attic/kmerge.sh,v 1.9 2004/09/08 15:58:12 zhen Exp $

die() {
	echo "$1"
	exit 1
}

build_kernel() {
	if [ -n "${clst_livecd_bootsplash}" ]
	then
		genkernel --bootsplash=${clst_livecd_bootsplash} \
			--callback="emerge ${clst_kernel_merge}" ${clst_livecd_gk_mainargs} \
			${clst_livecd_gk_kernargs} --kerneldir=/usr/src/linux \
			--kernel-config=/var/tmp/${clst_kname}.config \
			--minkernpackage=/usr/portage/packages/gk_binaries/${clst_kname}-${clst_version_stamp}.tar.bz2 all \
				|| exit 1
				
		tar cjpf /usr/portage/packages/gk_binaries/${1}-modules-${clst_version_stamp}.tar.bz2 \
			/lib/modules/"${1}" || die "Could not package kernel modules, exiting"
	else
		genkernel --callback="emerge ${clst_kernel_merge}" \
			${clst_livecd_gk_mainargs} ${clst_livecd_gk_kernargs} \
			--kerneldir=/usr/src/linux --kernel-config=/var/tmp/${clst_kname}.config \
			--minkernpackage=/usr/portage/packages/gk_binaries/${clst_kname}-${clst_version_stamp}.tar.bz2 all \
				|| exit 1
		
		tar cjpf /usr/portage/packages/gk_binaries/${1}-modules-${clst_version_stamp}.tar.bz2 \
			/lib/modules/"${1}" || die "Could not package kernel modules, exiting"
	fi
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

# kernel building happens here
# does the old config exist? if it does not, we build by default
if [ -e "/usr/portage/packages/gk_binaries/${clst_kname}-${clst_version_stamp}.config" ]
then
	# test to see if the kernel .configs are the same, if so, then we skip kernel building
	test1=$(md5sum /var/tmp/${clst_kname}.config | cut -d " " -f 1)
	test2=$(md5sum /usr/portage/packages/gk_binaries/${clst_kname}-${clst_version_stamp}.config | cut -d " " -f 1)
	if [ "${test1}" == "${test2}" ]
	then
		echo
		echo "No kernel configuration change, skipping kernel build..."
		echo
		sleep 5

		# copy over our config file so that kernel_merge packages like pcmcia don't complain
		#cp /usr/portage/packages/gk_binaries/${clst_kname}-${clst_version_stamp}.config /usr/src/linux/.config
		#emerge ${clst_kernel_merge}

		# unpack our modules to the LiveCD fs
		echo
		echo "Unpacking kernel modules from the previous build..."
		echo
		[ ! -d /lib/modules ] && mkdir /lib/modules
		tar xvjpf /usr/portage/packages/gk_binaries/${clst_fudgeuname}-modules-${clst_version_stamp}.tar.bz2 \
			-C / || die "Could not unpack kernel modules"
	else
		build_kernel ${clst_fudgeuname}
	fi

else
	build_kernel ${clst_fudgeuname}
	
fi

/sbin/modules-update --assume-kernel=${clst_fudgeuname}
		
#now the unmerge... (wipe db entry)
emerge -C ${clst_ksource}
unset USE

# keep the config around so that we can resume at some point
cp /var/tmp/${clst_kname}.config /usr/portage/packages/gk_binaries/${clst_kname}-${clst_version_stamp}.config
