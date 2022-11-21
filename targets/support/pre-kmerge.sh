#!/bin/bash

RUN_DEFAULT_FUNCS="yes"

source /tmp/chroot-functions.sh

if [[ ${clst_hostarch} == hppa ]]; then
	for i in ${clst_boot_kernel}; do
		case ${i} in
			*32)
				let num32++
				;;
			*64)
				let num64++
				;;
			*)
				die "Kernel names must end with either \"32\" or \"64\""
				;;
		esac
	done
	[[ $num32 -gt 1 ]] && die "Only one 32-bit kernel can be configured"
	[[ $num64 -gt 1 ]] && die "Only one 64-bit kernel can be configured"
fi

run_merge --oneshot sys-kernel/genkernel
install -d /tmp/kerncache
