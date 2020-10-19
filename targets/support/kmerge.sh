#!/bin/bash

source /tmp/chroot-functions.sh

install -d /tmp/kerncache

setup_gk_args() {
	# default genkernel args
	GK_ARGS=(
		"${kernel_gk_kernargs[@]}"
		--cachedir=/tmp/kerncache/${kname}-genkernel_cache-${clst_version_stamp}
		--no-mountboot
		--kerneldir=/usr/src/linux
		--modulespackage=/tmp/kerncache/${kname}-modules-${clst_version_stamp}.tar.bz2
		--minkernpackage=/tmp/kerncache/${kname}-kernel-initrd-${clst_version_stamp}.tar.bz2 all
	)
	# extra genkernel options that we have to test for
	if [ -n "${clst_gk_mainargs}" ]
	then
		GK_ARGS+=(${clst_gk_mainargs})
	fi
	if [ -n "${clst_KERNCACHE}" ]
	then
		GK_ARGS+=(--kerncache=/tmp/kerncache/${kname}-kerncache-${clst_version_stamp}.tar.bz2)
	fi
	if [ -e /var/tmp/${kname}.config ]
	then
		GK_ARGS+=(--kernel-config=/var/tmp/${kname}.config)
	fi

	if [ -d "/tmp/initramfs_overlay/${initramfs_overlay}" ]
	then
		GK_ARGS+=(--initramfs-overlay=/tmp/initramfs_overlay/${initramfs_overlay})
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

	if [ "${clst_target}" == "netboot" ]
	then
		GK_ARGS+=(--netboot)

		if [ -n "${clst_merge_path}" ]
		then
			GK_ARGS+=(--initramfs-overlay="${clst_merge_path}")
		fi
	fi

	if [ -n "${clst_VERBOSE}" ]
	then
		GK_ARGS+=(--loglevel=2)
	fi
}

genkernel_compile(){
	setup_gk_args

	# Build our list of kernel packages
	case ${clst_livecd_type} in
		gentoo-release-live*)
			if [ -n "${kernel_merge}" ]
			then
				mkdir -p /usr/livecd
				echo "${kernel_merge}" > /usr/livecd/kernelpkgs.txt
			fi
		;;
	esac
	# Build with genkernel using the set options
	# callback is put here to avoid escaping issues
	if [ -n "${clst_VERBOSE}" ]
	then
		gk_callback_opts=(-vN)
	else
		gk_callback_opts=(-qN)
	fi
	if [ -n "${clst_KERNCACHE}" ]
	then
		gk_callback_opts+=(-kb)
	fi
	if [ -n "${clst_FETCH}" ]
	then
		gk_callback_opts+=(-f)
	fi
	if [ "${kernel_merge}" != "" ]
	then
		genkernel --callback="emerge ${gk_callback_opts[@]} ${kernel_merge}" \
			"${GK_ARGS[@]}" || exit 1
	else
		genkernel "${GK_ARGS[@]}" || exit 1
	fi
	if [ -n "${clst_KERNCACHE}" -a -e /var/tmp/${kname}.config ]
	then
		md5sum /var/tmp/${kname}.config | awk '{print $1}' > \
			/tmp/kerncache/${kname}/${kname}-${clst_version_stamp}.CONFIG
	fi
}

[ -n "${clst_ENVSCRIPT}" ] && source /tmp/envscript
export CONFIG_PROTECT="-*"

# Set the timezone for the kernel build
rm /etc/localtime
cp -f /usr/share/zoneinfo/UTC /etc/localtime

eval "initramfs_overlay=\$clst_boot_kernel_${kname}_initramfs_overlay"
eval "kernel_merge=\$clst_boot_kernel_${kname}_packages"
eval "kernel_use=\$clst_boot_kernel_${kname}_use"
eval eval kernel_gk_kernargs=( \$clst_boot_kernel_${kname}_gk_kernargs )
eval "ksource=\$clst_boot_kernel_${kname}_sources"

if [ -z "${ksource}" ]
then
	ksource="virtual/linux-sources"
fi

# Check if we have a match in kerncach

if [ -n "${clst_KERNCACHE}" ]
then
	USE_MATCH=0
	if [ -e /tmp/kerncache/${kname}/${kname}-${clst_version_stamp}.USE ]
	then
		STR1=$(for i in `cat /tmp/kerncache/${kname}/${kname}-${clst_version_stamp}.USE`; do echo $i; done|sort)
		STR2=$(for i in ${kernel_use}; do echo $i; done|sort)
		if [ "${STR1}" = "${STR2}" ]
		then
			USE_MATCH=1
		else
			[ -e /tmp/kerncache/${kname}/usr/src/linux/.config ] && \
				rm /tmp/kerncache/${kname}/usr/src/linux/.config
		fi
	fi

	EXTRAVERSION_MATCH=0
	if [ -e /tmp/kerncache/${kname}/${kname}-${clst_version_stamp}.EXTRAVERSION ]
	then
		STR1=`cat /tmp/kerncache/${kname}/${kname}-${clst_version_stamp}.EXTRAVERSION`
		STR2=${clst_kextraversion}
		if [ "${STR1}" = "${STR2}" ]
		then
			EXTRAVERSION_MATCH=1
		fi
	fi

	CONFIG_MATCH=0
	if [ -e /tmp/kerncache/${kname}/${kname}-${clst_version_stamp}.CONFIG ]
	then
		if [ ! -e /var/tmp/${kname}.config ]
		then
			CONFIG_MATCH=1
		else
			STR1=`cat /tmp/kerncache/${kname}/${kname}-${clst_version_stamp}.CONFIG`
			STR2=`md5sum /var/tmp/${kname}.config|awk '{print $1}'`
			if [ "${STR1}" = "${STR2}" ]
			then
				CONFIG_MATCH=1
			fi
		fi
	fi

	# install dependencies of kernel sources ahead of time in case
	# package.provided generated below causes them not to be (re)installed
	run_merge --onlydeps "${ksource}"

	# Create the kerncache directory if it doesn't exists
	mkdir -p /tmp/kerncache/${kname}

	if [ -e /tmp/kerncache/${kname}/${kname}-${clst_version_stamp}.KERNELVERSION ]
	then
		KERNELVERSION=$(</tmp/kerncache/${kname}/${kname}-${clst_version_stamp}.KERNELVERSION)
		mkdir -p ${clst_port_conf}/profile
		echo "${KERNELVERSION}" > ${clst_port_conf}/profile/package.provided
	else
		rm -f ${clst_port_conf}/profile/package.provided
	fi

	# Don't use package.provided if there's a pending up/downgrade
	if [[ "$(portageq best_visible / ${ksource})" == "${KERNELVERSION}" ]]; then
		echo "No pending updates for ${ksource}"
	else
		echo "Pending updates for ${ksource}, removing package.provided"
		rm -f ${clst_port_conf}/profile/package.provided
	fi

	[ -L /usr/src/linux ] && rm -f /usr/src/linux

	run_merge "${ksource}"

	SOURCESDIR="/tmp/kerncache/${kname}/sources"
	if [ -L /usr/src/linux ]
	then
		# A kernel was merged, move it to $SOURCESDIR
		[ -e ${SOURCESDIR} ] && rm -Rf ${SOURCESDIR}

		KERNELVERSION=`portageq best_visible / "${ksource}"`
		echo "${KERNELVERSION}" > /tmp/kerncache/${kname}/${kname}-${clst_version_stamp}.KERNELVERSION

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
			sed -i -e "s:EXTRAVERSION \(=.*\):EXTRAVERSION \1-${clst_kextraversion}:" /usr/src/linux/Makefile
			echo ${clst_kextraversion} > /tmp/kerncache/${kname}/${kname}-${clst_version_stamp}.EXTRAVERSION
		else
			touch /tmp/kerncache/${kname}/${kname}-${clst_version_stamp}.EXTRAVERSION
		fi
	fi
else
	run_merge "${ksource}"
	#ensure that there is a /usr/src/linux symlink and it points to the sources we just installed
	echo "Adjusting /usr/src/linux to point to \
$(portageq contents / $(portageq best_visible / "${ksource}" 2>/dev/null) 2>/dev/null | grep --color=never '/usr/src/' | head -n1 2>/dev/null)"
	ln -snf $(portageq contents / $(portageq best_visible / "${ksource}" 2>/dev/null) 2>/dev/null | grep --color=never '/usr/src/' | head -n1 2>/dev/null) \
		/usr/src/linux
	if [ ! "${clst_kextraversion}" = "" ]
	then
		echo "Setting extraversion to ${clst_kextraversion}"
		sed -i -e "s:EXTRAVERSION \(=.*\):EXTRAVERSION \1-${clst_kextraversion}:" /usr/src/linux/Makefile
	fi
fi

# Update USE flag in make.conf
[ -e ${clst_make_conf} ] && \
	echo "USE=\"\${USE} ${kernel_use} build\"" >> ${clst_make_conf}

make_destpath

genkernel_compile

sed -i "/USE=\"\${USE} ${kernel_use} \"/d" ${clst_make_conf}
unset USE

if [ -n "${clst_KERNCACHE}" ]
then
	echo ${kernel_use} > /tmp/kerncache/${kname}/${kname}-${clst_version_stamp}.USE
fi
