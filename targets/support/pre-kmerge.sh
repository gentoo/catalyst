#!/bin/bash

source /tmp/chroot-functions.sh

case ${clst_hostarch} in
	hppa)
		got_32=0
		got_64=0
		for i in ${clst_boot_kernel}
		do
			if [ "${i: -2}" == "32" ]
			then
				if [ $got_32 -eq 1 ]
				then
					die "Only one 32 bit kernel can be configured"
				fi
				got_32=1
			elif [ "${i: -2}" == "64" ]
			then
				if [ $got_64 -eq 1 ]
				then
					die "Only one 64 bit kernel can be configured"
				fi
				got_64=1
			else
				die "Kernel names must end by either 32 or 64"
			fi
		done
	;;
esac

run_merge --oneshot genkernel
install -d /tmp/kerncache
