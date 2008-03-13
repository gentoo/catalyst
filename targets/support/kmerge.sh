#!/bin/bash

source /tmp/chroot-functions.sh

check_genkernel_version

install -d /tmp/kerncache
PKGDIR=/tmp/kerncache/${clst_kname}/ebuilds

setup_gk_args() {
	# default genkernel args
	GK_ARGS="${clst_gk_mainargs} \
			 ${clst_kernel_gk_kernargs} \
			 --cachedir=/tmp/kerncache/${clst_kname}-genkernel_cache-${clst_version_stamp} \
			 --no-mountboot \
			 --kerneldir=/usr/src/linux \
			 --modulespackage=/tmp/kerncache/${clst_kname}-modules-${clst_version_stamp}.tar.bz2 \
			 --minkernpackage=/tmp/kerncache/${clst_kname}-kernel-initrd-${clst_version_stamp}.tar.bz2 all"
	# extra genkernel options that we have to test for
	if [ -n "${clst_KERNCACHE}" ]
	then
		GK_ARGS="${GK_ARGS} --kerncache=/tmp/kerncache/${clst_kname}-kerncache-${clst_version_stamp}.tar.bz2"
	fi
	if [ -e /var/tmp/${clst_kname}.config ]
	then
		GK_ARGS="${GK_ARGS} --kernel-config=/var/tmp/${clst_kname}.config"
	fi

	if [ -n "${clst_splash_theme}" ]
	then
		GK_ARGS="${GK_ARGS} --splash=${clst_splash_theme}"
		# Setup case structure for livecd_type
		case ${clst_livecd_type} in
			gentoo-release-minimal|gentoo-release-universal)
				case ${clst_hostarch} in
					amd64|x86)
						GK_ARGS="${GK_ARGS} --splash-res=1024x768"
					;;
				esac
			;;
		esac
	fi

	if [ -d "/tmp/initramfs_overlay/${clst_initramfs_overlay}" ]
	then
		GK_ARGS="${GK_ARGS} --initramfs-overlay=/tmp/initramfs_overlay/${clst_initramfs_overlay}"
	fi
	if [ -n "${clst_CCACHE}" ]
	then
		GK_ARGS="${GK_ARGS} --kernel-cc=/usr/lib/ccache/bin/gcc --utils-cc=/usr/lib/ccache/bin/gcc"
	fi
	
	if [ "${clst_devmanager}" == "devfs" ]
	then
		GK_ARGS="${GK_ARGS} --no-udev"
	fi

	if [ -n "${clst_linuxrc}" ]
	then
		GK_ARGS="${GK_ARGS} --linuxrc=/tmp/linuxrc"
	fi

    if [ "${clst_target}" == "netboot2" -a -n "${clst_merge_path}" ]
    then
        GK_ARGS="${GK_ARGS} --initramfs-overlay=\"${clst_merge_path}\""
    fi
}

genkernel_compile(){
	eval "clst_initramfs_overlay=\$clst_boot_kernel_${filtered_kname}_initramfs_overlay"
	eval "clst_kernel_merge=\$clst_boot_kernel_${filtered_kname}_packages"

	setup_gk_args
	#echo "The GK_ARGS are"
	#echo ${GK_ARGS}	
	export clst_kernel_merge
	export clst_initramfs_overlay
	# Build our list of kernel packages
	if [ "${clst_livecd_type}" = "gentoo-release-livecd" ] \
	&& [ -n "${clst_kernel_merge}" ]
	then
		mkdir -p /usr/livecd
		echo "${clst_kernel_merge}" > /usr/livecd/kernelpkgs.txt
	fi
	# Build with genkernel using the set options
	# callback is put here to avoid escaping issues
	gk_callback_opts="-qN"
	PKGDIR=${PKGDIR}
	if [ -n "${clst_KERNCACHE}" ]
	then
		gk_callback_opts="${gk_callback_opts} -kb"
	fi
	if [ -n "${clst_FETCH}" ]
	then
		gk_callback_opts="${gk_callback_opts} -f"
	fi
	if [ "${clst_kernel_merge}" != "" ]
	then
		genkernel --callback="emerge ${gk_callback_opts} ${clst_kernel_merge}" \
			${GK_ARGS} || exit 1
	else
		genkernel ${GK_ARGS} || exit 1
	fi
	md5sum /var/tmp/${clst_kname}.config | awk '{print $1}' > \
		/tmp/kerncache/${clst_kname}/${clst_kname}-${clst_version_stamp}.CONFIG
}

build_kernel() {
	genkernel_compile
}

[ -n "${clst_ENVSCRIPT}" ] && source /tmp/envscript
export CONFIG_PROTECT="-*"

# Set the timezone for the kernel build
rm /etc/localtime
cp -f /usr/share/zoneinfo/UTC /etc/localtime

filtered_kname=${clst_kname/-/_}
filtered_kname=${clst_kname/\//_}
filtered_kname=${filtered_kname/\./_}

eval "clst_kernel_use=\$clst_boot_kernel_${filtered_kname}_use"
eval "clst_kernel_gk_kernargs=\$clst_boot_kernel_${filtered_kname}_gk_kernargs"
eval "clst_ksource=\$clst_boot_kernel_${filtered_kname}_sources"

if [ -z "${clst_ksource}" ]
then
	clst_ksource="virtual/linux-sources"
fi

# Don't use pkgcache here, as the kernel source may get emerged with different
# USE variables (and thus different patches enabled/disabled.) Also, there's no
# real benefit in using the pkgcache for kernel source ebuilds.

USE_MATCH=0 
if [ -e /tmp/kerncache/${clst_kname}/${clst_kname}-${clst_version_stamp}.USE ]
then
	STR1=$(for i in `cat /tmp/kerncache/${clst_kname}/${clst_kname}-${clst_version_stamp}.USE`; do echo $i; done|sort)
	STR2=$(for i in ${clst_kernel_use}; do echo $i; done|sort)
	if [ "${STR1}" = "${STR2}" ]
	then 
		#echo "USE Flags match"
		USE_MATCH=1 
	else
		if [ -n "${clst_KERNCACHE}" ]
		then
		[ -d /tmp/kerncache/${clst_kname}/ebuilds ] && \
			rm -r /tmp/kerncache/${clst_kname}/ebuilds
		[ -e /tmp/kerncache/${clst_kname}/usr/src/linux/.config ] && \
			rm /tmp/kerncache/${clst_kname}/usr/src/linux/.config
		fi
	fi
fi

EXTRAVERSION_MATCH=0
if [ -e /tmp/kerncache/${clst_kname}/${clst_kname}-${clst_version_stamp}.EXTRAVERSION ]
then
	STR1=`cat /tmp/kerncache/${clst_kname}/${clst_kname}-${clst_version_stamp}.EXTRAVERSION`
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
if [ -e /tmp/kerncache/${clst_kname}/${clst_kname}-${clst_version_stamp}.CONFIG ]
then
	STR1=`cat /tmp/kerncache/${clst_kname}/${clst_kname}-${clst_version_stamp}.CONFIG`
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

[ -e /etc/make.conf ] && \
	echo "USE=\"\${USE} ${clst_kernel_use} build\"" >> /etc/make.conf

if [ -n "${clst_KERNCACHE}" ]
then
	mkdir -p /tmp/kerncache/${clst_kname}
   	clst_root_path=/tmp/kerncache/${clst_kname} PKGDIR=${PKGDIR} clst_myemergeopts="--quiet --nodeps --update --newuse" run_merge "${clst_ksource}" || exit 1
	KERNELVERSION=`portageq best_visible / "${clst_ksource}"`
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
	[ -L /usr/src/linux ] && rm -f /usr/src/linux
	ln -s /tmp/kerncache/${clst_kname}/usr/src/linux /usr/src/linux
else
	[ -L /usr/src/linux ] && rm -f /usr/src/linux
	run_merge "${clst_ksource}" || exit 1
fi
make_destpath

# If catalyst has set to a empty string, extraversion wasn't specified so we
# skip this part
if [ "${EXTRAVERSION_MATCH}" = "0" ]
then
	if [ ! "${clst_kextraversion}" = "" ]
	then
		echo "Setting extraversion to ${clst_kextraversion}"
		sed -i -e "s:EXTRAVERSION \(=.*\):EXTRAVERSION \1-${clst_kextraversion}:" /usr/src/linux/Makefile
		echo ${clst_kextraversion} > /tmp/kerncache/${clst_kname}/${clst_kname}-${clst_version_stamp}.EXTRAVERSION
	else 
		touch /tmp/kerncache/${clst_kname}/${clst_kname}-${clst_version_stamp}.EXTRAVERSION
	fi
fi

build_kernel
sed -i "/USE=\"\${USE} ${clst_kernel_use} build\"/d" /etc/make.conf
# grep out the kernel version so that we can do our modules magic
VER=`grep ^VERSION\ \= /usr/src/linux/Makefile | awk '{ print $3 };'`
PAT=`grep ^PATCHLEVEL\ \= /usr/src/linux/Makefile | awk '{ print $3 };'`
SUB=`grep ^SUBLEVEL\ \= /usr/src/linux/Makefile | awk '{ print $3 };'`
EXV=`grep ^EXTRAVERSION\ \= /usr/src/linux/Makefile | sed -e "s/EXTRAVERSION =//" -e "s/ //g"`
clst_fudgeuname=${VER}.${PAT}.${SUB}${EXV}

/sbin/update-modules --assume-kernel=${clst_fudgeuname}

unset USE
echo ${clst_kernel_use} > /tmp/kerncache/${clst_kname}/${clst_kname}-${clst_version_stamp}.USE
