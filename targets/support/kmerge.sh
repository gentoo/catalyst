#!/bin/bash

source /tmp/chroot-functions.sh

install -d /tmp/kerncache

genkernel_compile() {
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
	if [[ -n ${clst_gk_mainargs} ]]; then
		GK_ARGS+=(${clst_gk_mainargs})
	fi
	if [[ -n ${clst_KERNCACHE} ]]; then
		GK_ARGS+=(--kerncache=/tmp/kerncache/${kname}-kerncache-${clst_version_stamp}.tar.bz2)
	fi
	if [[ -e /var/tmp/${kname}.config ]]; then
		GK_ARGS+=(--kernel-config=/var/tmp/${kname}.config)
	fi
	if [[ -d /tmp/initramfs_overlay/${initramfs_overlay} ]]; then
		GK_ARGS+=(--initramfs-overlay=/tmp/initramfs_overlay/${initramfs_overlay})
	fi
	if [[ -n ${clst_CCACHE} ]]; then
		GK_ARGS+=(--kernel-cc=/usr/lib/ccache/bin/gcc --utils-cc=/usr/lib/ccache/bin/gcc)
	fi
	if [[ -n ${clst_linuxrc} ]]; then
		GK_ARGS+=(--linuxrc=/tmp/linuxrc)
	fi
	if [[ -n ${clst_busybox_config} ]]; then
		GK_ARGS+=(--busybox-config=/tmp/busy-config)
	fi
	if [[ ${clst_target} == netboot ]]; then
		GK_ARGS+=(--netboot)

		if [[ -n ${clst_merge_path} ]]; then
			GK_ARGS+=(--initramfs-overlay="${clst_merge_path}")
		fi
	fi
	if [[ -n ${clst_VERBOSE} ]]; then
		GK_ARGS+=(--loglevel=2)
	fi

	if [[ -n ${clst_VERBOSE} ]]; then
		gk_callback_opts=(-vN)
	else
		gk_callback_opts=(-qN)
	fi
	if [[ -n ${clst_KERNCACHE} ]]; then
		gk_callback_opts+=(-kb)
	fi
	if [[ -n ${clst_FETCH} ]]; then
		gk_callback_opts+=(-f)
	fi

	if [[ -n ${kernel_merge} ]]; then
		genkernel --callback="emerge ${gk_callback_opts[@]} ${kernel_merge}" \
			"${GK_ARGS[@]}" || exit 1
	else
		genkernel "${GK_ARGS[@]}" || exit 1
	fi
}

[ -n "${clst_ENVSCRIPT}" ] && source /tmp/envscript

# Set the timezone for the kernel build
rm /etc/localtime
cp -f /usr/share/zoneinfo/UTC /etc/localtime

eval "initramfs_overlay=\$clst_boot_kernel_${kname}_initramfs_overlay"
eval "kernel_merge=\$clst_boot_kernel_${kname}_packages"
eval "kernel_use=\$clst_boot_kernel_${kname}_use"
eval eval kernel_gk_kernargs=( \$clst_boot_kernel_${kname}_gk_kernargs )
eval "ksource=\$clst_boot_kernel_${kname}_sources"
[[ -z ${ksource} ]] && ksource="sys-kernel/gentoo-sources"

kernel_version=$(portageq best_visible / "${ksource}")

if [[ -n ${clst_KERNCACHE} ]]; then
	mkdir -p "/tmp/kerncache/${kname}"
	pushd "/tmp/kerncache/${kname}" >/dev/null

	echo "${kernel_use}" > /tmp/USE
	echo "${kernel_version}" > /tmp/VERSION
	echo "${clst_kextraversion}" > /tmp/EXTRAVERSION

	if cmp -s {/tmp/,}USE && \
	   cmp -s {/tmp/,}VERSION && \
	   cmp -s {/tmp/,}EXTRAVERSION && \
	   cmp -s /var/tmp/${kname}.config CONFIG; then
		cached_kernel_found="true"
	fi

	rm -f /tmp/{USE,VERSION,EXTRAVERSION}
	popd >/dev/null
fi

if [[ ! ${cached_kernel_found} ]]; then
	USE=symlink run_merge --update "${ksource}"
fi

if [[ -n ${clst_KERNCACHE} ]]; then
	SOURCESDIR="/tmp/kerncache/${kname}/sources"
	if [[ ! ${cached_kernel_found} ]]; then
		echo "Moving kernel sources to ${SOURCESDIR} ..."

		rm -rf "${SOURCESDIR}"
		mv $(readlink -f /usr/src/linux) "${SOURCESDIR}"
	fi
	ln -snf "${SOURCESDIR}" /usr/src/linux
fi

if [[ -n ${clst_kextraversion} ]]; then
	echo "Setting EXTRAVERSION to ${clst_kextraversion}"

	if [[ -e /usr/src/linux/Makefile.bak ]]; then
		cp /usr/src/linux/Makefile{.bak,}
	else
		cp /usr/src/linux/Makefile{,.bak}
	fi
	sed -i -e "s:EXTRAVERSION \(=.*\):EXTRAVERSION \1-${clst_kextraversion}:" \
		/usr/src/linux/Makefile
fi

genkernel_compile

# Write out CONFIG, USE, VERSION, and EXTRAVERSION files
if [[ -n ${clst_KERNCACHE} && ! ${cached_kernel_found} ]]; then
	pushd "/tmp/kerncache/${kname}" >/dev/null

	cp /var/tmp/${kname}.config CONFIG
	echo "${kernel_use}" > USE
	echo "${kernel_version}" > VERSION
	echo "${clst_kextraversion}" > EXTRAVERSION

	popd >/dev/null
fi

if [[ ! ${cached_kernel_found} ]]; then
	run_merge -C "${ksource}"
	rm /usr/src/linux
fi
