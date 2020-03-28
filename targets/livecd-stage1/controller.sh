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
		echo "${clst_packages}" > ${clst_chroot_path}/tmp/packages.txt
		;;

	clean)
		find ${clst_chroot_path}/usr/lib -iname "*.pyc" -exec rm -f {} \;
		;;
esac
exit $?
