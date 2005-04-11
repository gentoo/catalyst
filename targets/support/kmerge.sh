#!/bin/bash
# Copyright 1999-2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2

source /tmp/chroot-functions.sh

check_genkernel_version

PKGDIR=/usr/portage/packages/gk_binaries/${clst_kname}/ebuilds

setup_gk_args() {
	# default genkernel args
	GK_ARGS="${clst_gk_mainargs} \
			 ${clst_kernel_gk_kernargs} \
			 --no-mountboot \
			 --no-install \
			 --kerneldir=/usr/src/linux \
			 --kernel-config=/var/tmp/${clst_kname}.config \
			 --modulespackage=/usr/portage/packages/gk_binaries/${clst_kname}-modules-${clst_version_stamp}.tar.bz2 \
			 --minkernpackage=/usr/portage/packages/gk_binaries/${clst_kname}-kernel-initrd-${clst_version_stamp}.tar.bz2 \
			 --kerncache=/usr/portage/packages/gk_binaries/${clst_kname}-kerncache-${clst_version_stamp}.tar.bz2 all"
	# extra genkernel options that we have to test for
	if [ "${clst_splash_type}" == "bootsplash" -a -n "${clst_splash_theme}" ]
	then
		GK_ARGS="${GK_ARGS} --bootsplash=${clst_splash_theme}"
	fi
	
	if [ "${clst_splash_type}" == "gensplash" -a -n "${clst_splash_theme}" ]
	then
		GK_ARGS="${GK_ARGS} --gensplash=${clst_splash_theme}"
	fi

	if [ -n "${clst_CCACHE}" ]
	then
		GK_ARGS="${GK_ARGS} --kernel-cc=/usr/lib/ccache/bin/gcc --utils-cc=/usr/lib/ccache/bin/gcc"
	fi
	
	if [ "${clst_devmanager}" == "devfs" ]
	then
		GK_ARGS="${GK_ARGS} --no-udev"
	fi
}

genkernel_compile(){

	setup_gk_args
	
	eval "clst_kernel_postconf=\$clst_boot_kernel_${clst_kname}_postconf"
	eval "clst_kernel_merge=\$clst_boot_kernel_${clst_kname}_packages"
	export clst_kernel_postconf
	export clst_kernel_merge
	# build with genkernel using the set options
	# callback and postconf are put here to avoid escaping issues
	if [ -n "${clst_KERNCACHE}" ]
	then
		if [ "$clst_kernel_postconf" != "" \
 			-a "$clst_kernel_merge" != "" ]
		then
			genkernel --callback="PKGDIR=${PKGDIR} emerge -kb ${clst_kernel_merge}" \
				--postconf="PKGDIR=${PKGDIR} emerge -kb ${clst_kernel_postconf}" \
					${GK_ARGS} || exit 1
		elif [ "$clst_kernel_merge" != "" ]
		then
			genkernel --callback="PKGDIR=${PKGDIR} emerge -kb ${clst_kernel_merge}" \
				${GK_ARGS} || exit 1
		elif [ "$clst_kernel_postconf" != "" ]
		then
			genkernel --postconf="PKGDIR=${PKGDIR} emerge -kb ${clst_kernel_postconf}" \
				${GK_ARGS} || exit 1
		else
			genkernel ${GK_ARGS} || exit 1
		fi
	else
		if [ "$clst_kernel_postconf" != "" \
 			-a "$clst_kernel_merge" != "" ]
		then
			genkernel --callback="emerge ${clst_kernel_merge}" \
				--postconf="emerge ${clst_kernel_postconf}" \
				${GK_ARGS} || exit 1
		elif [ "$clst_kernel_merge" != "" ]
		then
			genkernel --callback="emerge ${clst_kernel_merge}" \
				${GK_ARGS} || exit 1
		elif [ "$clst_kernel_postconf" != "" ]
		then
			genkernel --postconf="emerge ${clst_kernel_postconf}" \
				${GK_ARGS} || exit 1
		else
			genkernel ${GK_ARGS} || exit 1
		fi
	fi
	md5sum /var/tmp/${clst_kname}.config|awk '{print $1}' > /usr/portage/packages/gk_binaries/${clst_kname}/${clst_kname}-${clst_version_stamp}.CONFIG
}

build_kernel() {
	genkernel_compile
}



# Script to build each kernel, kernel-related packages
/usr/sbin/env-update
source /etc/profile

setup_myfeatures
setup_myemergeopts

[ -n "${clst_ENVSCRIPT}" ] && source /tmp/envscript
export CONFIG_PROTECT="-*"

#set the timezone for the kernel build
rm /etc/localtime
ln -s /usr/share/zoneinfo/UTC /etc/localtime

eval "clst_kernel_use=\$clst_boot_kernel_${clst_kname}_use"
export USE=$clst_kernel_use

eval "clst_kernel_gk_kernargs=\$clst_boot_kernel_${clst_kname}_gk_kernargs"
eval "clst_ksource=\$clst_boot_kernel_${clst_kname}_sources"



# Don't use pkgcache here, as the kernel source may get emerge with different USE variables
# (and thus different patches enabled/disabled.) Also, there's no real benefit in using the
# pkgcache for kernel source ebuilds.

USE_MATCH=0 
if [ -e /usr/portage/packages/gk_binaries/${clst_kname}/${clst_kname}-${clst_version_stamp}.USE ]
then

	STR1=$(for i in `cat /usr/portage/packages/gk_binaries/${clst_kname}/${clst_kname}-${clst_version_stamp}.USE`; do echo $i; done|sort)
	STR2=$(for i in ${clst_kernel_use}; do echo $i; done|sort)
	if [ "${STR1}" = "${STR2}" ]
	then 
		#echo "USE Flags match"
		USE_MATCH=1 
	else
	    if [ -n "${clst_KERNCACHE}" ]
	    then
		[ -d /usr/portage/packages/gk_binaries/${clst_kname}/ebuilds ] && \
			rm -r /usr/portage/packages/gk_binaries/${clst_kname}/ebuilds
		[ -e /usr/portage/packages/gk_binaries/${clst_kname}/usr/src/linux/.config ] && \
			rm /usr/portage/packages/gk_binaries/${clst_kname}/usr/src/linux/.config
	    fi
	fi
fi

EXTRAVERSION_MATCH=0
if [ -e /usr/portage/packages/gk_binaries/${clst_kname}/${clst_kname}-${clst_version_stamp}.EXTRAVERSION ]
then
	STR1=`cat /usr/portage/packages/gk_binaries/${clst_kname}/${clst_kname}-${clst_version_stamp}.EXTRAVERSION`
	STR2=${clst_kextraversion}
	if [ "${STR1}" = "${STR2}" ]
	then 
		if [ -n "${clst_KERNCACHE}" ]
		then
			#echo "EXTRAVERSION match"
			EXTRAVERSION_MATCH=1
		fi
	fi
fi

CONFIG_MATCH=0
if [ -e /usr/portage/packages/gk_binaries/${clst_kname}/${clst_kname}-${clst_version_stamp}.CONFIG ]
then
	STR1=`cat /usr/portage/packages/gk_binaries/${clst_kname}/${clst_kname}-${clst_version_stamp}.CONFIG`
	STR2=`md5sum /var/tmp/${clst_kname}.config|awk '{print $1}'`
	if [ "${STR1}" = "${STR2}" ]
	then 
		if [ -n "${clst_KERNCACHE}" ]
		then
			#echo "CONFIG match"
			CONFIG_MATCH=1
		fi

	fi
fi

if [ "${USE_MATCH}" = "0" -o "${EXTRAVERSION_MATCH}" = "0" -o "${CONFIG_MATCH}" = "0" ]
then
	echo "Cleaning up ${clst_kname} kernel install ..."
	echo "This may take some time ..."
	if [ -d /usr/portage/packages/gk_binaries/${clst_kname}/ ] 
	then
		rm -r /usr/portage/packages/gk_binaries/${clst_kname}/ || exit 1
	fi
fi

mkdir -p /usr/portage/packages/gk_binaries/${clst_kname}
	
if [ -n "${clst_KERNCACHE}" ]
then
   	ROOT=/usr/portage/packages/gk_binaries/${clst_kname} PKGDIR=${PKGDIR} USE="${USE} symlink build" emerge -ukb  "${clst_ksource}" || exit 1
	KERNELVERSION=`/usr/lib/portage/bin/portageq best_visible / "${clst_ksource}"`
	if [ ! -e /etc/portage/profile/package.provided ]
	then
		mkdir -p /etc/portage/profile
		echo "${KERNELVERSION}" > /etc/portage/profile/package.provided
	else
		if ( ! grep -q "^${KERNELVERSION}"  /etc/portage/profile/package.provided ) 
		then
			echo "${KERNELVERSION}" >> /etc/portage/profile/package.provided
		fi
	fi
    	[ -d /usr/src/linux ] && rm /usr/src/linux
	ln -s /usr/portage/packages/gk_binaries/${clst_kname}/usr/src/linux /usr/src/linux
else
    	USE="${USE} symlink build" emerge "${clst_ksource}" || exit 1
fi

#if catalyst has set to a empty string, extraversion wasn't specified so we skip this part
if [ "${EXTRAVERSION_MATCH}" != "1" ]
then
    if [ "${clst_kextraversion}" != "" ]
    then
	echo "Setting extraversion to ${clst_kextraversion}"
	sed -i -e "s:EXTRAVERSION \(=.*\):EXTRAVERSION \1-${clst_kextraversion}:" /usr/src/linux/Makefile
    	echo ${clst_kextraversion} > /usr/portage/packages/gk_binaries/${clst_kname}/${clst_kname}-${clst_version_stamp}.EXTRAVERSION
    else 
    	touch /usr/portage/packages/gk_binaries/${clst_kname}/${clst_kname}-${clst_version_stamp}.EXTRAVERSION
    fi
fi
	

build_kernel
# grep out the kernel version so that we can do our modules magic
VER=`grep ^VERSION\ \= /usr/src/linux/Makefile | awk '{ print $3 };'`
PAT=`grep ^PATCHLEVEL\ \= /usr/src/linux/Makefile | awk '{ print $3 };'`
SUB=`grep ^SUBLEVEL\ \= /usr/src/linux/Makefile | awk '{ print $3 };'`
EXV=`grep ^EXTRAVERSION\ \= /usr/src/linux/Makefile | sed -e "s/EXTRAVERSION =//" -e "s/ //g"`
clst_fudgeuname=${VER}.${PAT}.${SUB}${EXV}

/sbin/modules-update --assume-kernel=${clst_fudgeuname}

unset USE
echo ${clst_kernel_use} > /usr/portage/packages/gk_binaries/${clst_kname}/${clst_kname}-${clst_version_stamp}.USE
