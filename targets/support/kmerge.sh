#!/bin/bash

source /tmp/chroot-functions.sh

check_genkernel_version

install -d /tmp/kerncache
PKGDIR=/tmp/kerncache/${clst_kname}/ebuilds

setup_gk_args() {
	# default genkernel args
	GK_ARGS=(
		"${clst_kernel_gk_kernargs[@]}"
		--cachedir=/tmp/kerncache/${clst_kname}-genkernel_cache-${clst_version_stamp}
		--no-mountboot
		--kerneldir=/usr/src/linux
		--modulespackage=/tmp/kerncache/${clst_kname}-modules-${clst_version_stamp}.tar.bz2
		--minkernpackage=/tmp/kerncache/${clst_kname}-kernel-initrd-${clst_version_stamp}.tar.bz2 all
	)
	# extra genkernel options that we have to test for
	if [ -n "${clst_gk_mainargs}" ]
	then
		GK_ARGS+=(${clst_gk_mainargs})
	fi
	if [ -n "${clst_KERNCACHE}" ]
	then
		GK_ARGS+=(--kerncache=/tmp/kerncache/${clst_kname}-kerncache-${clst_version_stamp}.tar.bz2)
	fi
	if [ -e /var/tmp/${clst_kname}.config ]
	then
		GK_ARGS+=(--kernel-config=/var/tmp/${clst_kname}.config)
	fi

	if [ -n "${clst_splash_theme}" ]
	then
		GK_ARGS+=(--splash=${clst_splash_theme})
		# Setup case structure for livecd_type
		case ${clst_livecd_type} in
			gentoo-release-minimal|gentoo-release-universal)
				case ${clst_hostarch} in
					amd64|x86)
						GK_ARGS+=(--splash-res=1024x768)
					;;
				esac
			;;
		esac
	fi

	if [ -d "/tmp/initramfs_overlay/${clst_initramfs_overlay}" ]
	then
		GK_ARGS+=(--initramfs-overlay=/tmp/initramfs_overlay/${clst_initramfs_overlay})
	fi
	if [ -n "${clst_CCACHE}" ]
	then
		GK_ARGS+=(--kernel-cc=/usr/lib/ccache/bin/gcc --utils-cc=/usr/lib/ccache/bin/gcc)
	fi

	if [ -n "${clst_linuxrc}" ]
	then
		GK_ARGS+=(--linuxrc=/tmp/linuxrc)
	fi

	if [ -n "${clst_busybox_config}" ]
	then
		GK_ARGS+=(--busybox-config=/tmp/busy-config)
	fi

	if [ "${clst_target}" == "netboot2" ]
	then
		GK_ARGS+=(--netboot)

		if [ -n "${clst_merge_path}" ]
		then
			GK_ARGS+=(--initramfs-overlay="${clst_merge_path}")
		fi
	fi

	if [[ "${clst_VERBOSE}" == "true" ]]
	then
		GK_ARGS+=(--loglevel=2)
	fi
}

genkernel_compile(){
	eval "clst_initramfs_overlay=\$clst_boot_kernel_${filtered_kname}_initramfs_overlay"
	eval "clst_kernel_merge=\$clst_boot_kernel_${filtered_kname}_packages"

	setup_gk_args
	#echo "The GK_ARGS are"
	#echo ${GK_ARGS[@]}
	export clst_kernel_merge
	export clst_initramfs_overlay
	# Build our list of kernel packages
	case ${clst_livecd_type} in
		gentoo-release-live*)
			if [ -n "${clst_kernel_merge}" ]
			then
				mkdir -p /usr/livecd
				echo "${clst_kernel_merge}" > /usr/livecd/kernelpkgs.txt
			fi
		;;
	esac
	# Build with genkernel using the set options
	# callback is put here to avoid escaping issues
	if [[ "${clst_VERBOSE}" == "true" ]]
	then
		gk_callback_opts="-vN"
	else
		gk_callback_opts="-qN"
	fi
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
			"${GK_ARGS[@]}" || exit 1
	else
		genkernel "${GK_ARGS[@]}" || exit 1
	fi
	if [ -n "${clst_KERNCACHE}" -a -e /var/tmp/${clst_kname}.config ]
	then
		md5sum /var/tmp/${clst_kname}.config | awk '{print $1}' > \
			/tmp/kerncache/${clst_kname}/${clst_kname}-${clst_version_stamp}.CONFIG
	fi
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
eval eval clst_kernel_gk_kernargs=( \$clst_boot_kernel_${filtered_kname}_gk_kernargs )
eval "clst_ksource=\$clst_boot_kernel_${filtered_kname}_sources"

if [ -z "${clst_ksource}" ]
then
	clst_ksource="virtual/linux-sources"
fi

# Don't use pkgcache here, as the kernel source may get emerged with different
# USE variables (and thus different patches enabled/disabled.) Also, there's no
# real benefit in using the pkgcache for kernel source ebuilds.


# Check if we have a match in kerncach

if [ -n "${clst_KERNCACHE}" ]
then

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
			[ -d /tmp/kerncache/${clst_kname}/ebuilds ] && \
				rm -r /tmp/kerncache/${clst_kname}/ebuilds
			[ -e /tmp/kerncache/${clst_kname}/usr/src/linux/.config ] && \
				rm /tmp/kerncache/${clst_kname}/usr/src/linux/.config
		fi
	fi

	EXTRAVERSION_MATCH=0
	if [ -e /tmp/kerncache/${clst_kname}/${clst_kname}-${clst_version_stamp}.EXTRAVERSION ]
	then
		STR1=`cat /tmp/kerncache/${clst_kname}/${clst_kname}-${clst_version_stamp}.EXTRAVERSION`
		STR2=${clst_kextraversion}
		if [ "${STR1}" = "${STR2}" ]
		then
			#echo "EXTRAVERSION match"
			EXTRAVERSION_MATCH=1
		fi
	fi

	CONFIG_MATCH=0
	if [ -e /tmp/kerncache/${clst_kname}/${clst_kname}-${clst_version_stamp}.CONFIG ]
	then
		if [ ! -e /var/tmp/${clst_kname}.config ]
		then
			CONFIG_MATCH=1
		else
			STR1=`cat /tmp/kerncache/${clst_kname}/${clst_kname}-${clst_version_stamp}.CONFIG`
			STR2=`md5sum /var/tmp/${clst_kname}.config|awk '{print $1}'`
			if [ "${STR1}" = "${STR2}" ]
			then
				CONFIG_MATCH=1
			fi
		fi
	fi

	# install dependencies of kernel sources ahead of time in case
	# package.provided generated below causes them not to be (re)installed
	PKGDIR=${PKGDIR} clst_myemergeopts="--quiet --update --newuse --onlydeps" run_merge "${clst_ksource}" || exit 1

	# Create the kerncache directory if it doesn't exists
	mkdir -p /tmp/kerncache/${clst_kname}

	if [ -e /tmp/kerncache/${clst_kname}/${clst_kname}-${clst_version_stamp}.KERNELVERSION ]
	then
		KERNELVERSION=$(</tmp/kerncache/${clst_kname}/${clst_kname}-${clst_version_stamp}.KERNELVERSION)
		mkdir -p ${clst_port_conf}/profile
		echo "${KERNELVERSION}" > ${clst_port_conf}/profile/package.provided
	else
		rm -f ${clst_port_conf}/profile/package.provided
	fi

	# Don't use package.provided if there's a pending up/downgrade
	if [[ "$(portageq best_visible / ${clst_ksource})" == "${KERNELVERSION}" ]]; then
		echo "No pending updates for ${clst_ksource}"
	else
		echo "Pending updates for ${clst_ksource}, removing package.provided"
		rm -f ${clst_port_conf}/profile/package.provided
	fi

	[ -L /usr/src/linux ] && rm -f /usr/src/linux

	PKGDIR=${PKGDIR} clst_myemergeopts="--quiet --update --newuse" run_merge "${clst_ksource}" || exit 1

	SOURCESDIR="/tmp/kerncache/${clst_kname}/sources"
	if [ -L /usr/src/linux ]
	then

		# A kernel was merged, move it to $SOURCESDIR
		[ -e ${SOURCESDIR} ] && rm -Rf ${SOURCESDIR}

		KERNELVERSION=`portageq best_visible / "${clst_ksource}"`
		echo "${KERNELVERSION}" > /tmp/kerncache/${clst_kname}/${clst_kname}-${clst_version_stamp}.KERNELVERSION

		echo "Moving kernel sources to ${SOURCESDIR} ..."
		mv `readlink -f /usr/src/linux` ${SOURCESDIR}

	fi
	ln -sf ${SOURCESDIR} /usr/src/linux

	# If catalyst has set to a empty string, extraversion wasn't specified so we
	# skip this part
	if [ "${EXTRAVERSION_MATCH}" = "0" ]
	then
		if [ ! "${clst_kextraversion}" = "" ]
		then
			echo "Setting extraversion to ${clst_kextraversion}"
			${clst_sed} -i -e "s:EXTRAVERSION \(=.*\):EXTRAVERSION \1-${clst_kextraversion}:" /usr/src/linux/Makefile
			echo ${clst_kextraversion} > /tmp/kerncache/${clst_kname}/${clst_kname}-${clst_version_stamp}.EXTRAVERSION
		else
			touch /tmp/kerncache/${clst_kname}/${clst_kname}-${clst_version_stamp}.EXTRAVERSION
		fi
	fi

else
	run_merge "${clst_ksource}" || exit 1
	#ensure that there is a /usr/src/linux symlink and it points to the sources we just installed
	echo "Adjusting /usr/src/linux to point to \
$(portageq contents / $(portageq best_visible / "${clst_ksource}" 2>/dev/null) 2>/dev/null | grep --color=never '/usr/src/' | head -n1 2>/dev/null)"
	ln -snf $(portageq contents / $(portageq best_visible / "${clst_ksource}" 2>/dev/null) 2>/dev/null | grep --color=never '/usr/src/' | head -n1 2>/dev/null) \
		/usr/src/linux
	if [ ! "${clst_kextraversion}" = "" ]
	then
		echo "Setting extraversion to ${clst_kextraversion}"
		${clst_sed} -i -e "s:EXTRAVERSION \(=.*\):EXTRAVERSION \1-${clst_kextraversion}:" /usr/src/linux/Makefile
	fi
fi


# Update USE flag in make.conf
[ -e ${clst_make_conf} ] && \
	echo "USE=\"\${USE} ${clst_kernel_use} build\"" >> ${clst_make_conf}

make_destpath


build_kernel
${clst_sed} -i "/USE=\"\${USE} ${clst_kernel_use} \"/d" ${clst_make_conf}
# grep out the kernel version so that we can do our modules magic
VER=`grep ^VERSION\ \= /usr/src/linux/Makefile | awk '{ print $3 };'`
PAT=`grep ^PATCHLEVEL\ \= /usr/src/linux/Makefile | awk '{ print $3 };'`
SUB=`grep ^SUBLEVEL\ \= /usr/src/linux/Makefile | awk '{ print $3 };'`
EXV=`grep ^EXTRAVERSION\ \= /usr/src/linux/Makefile | ${clst_sed} -e "s/EXTRAVERSION =//" -e "s/ //g"`
clst_fudgeuname=${VER}.${PAT}.${SUB}${EXV}

unset USE


if [ -n "${clst_KERNCACHE}" ]
then
	echo ${clst_kernel_use} > /tmp/kerncache/${clst_kname}/${clst_kname}-${clst_version_stamp}.USE
fi
