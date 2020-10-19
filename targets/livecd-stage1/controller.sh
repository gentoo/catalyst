#!/bin/bash

source ${clst_shdir}/support/functions.sh

## START RUNSCRIPT

case $1 in
	build_packages)
		shift
		export clst_packages="$*"
		mkdir -p ${clst_chroot_path}/usr/livecd ${clst_chroot_path}/tmp
		exec_in_chroot \
			${clst_shdir}/${clst_target}/chroot.sh
		;;
esac
exit $?
