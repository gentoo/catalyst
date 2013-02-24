#!/bin/bash

source ${clst_shdir}/support/functions.sh

case $1 in
	enter)
	;;

	run)
		cp ${clst_shdir}/stage1/build.py ${clst_chroot_path}/tmp

		# Setup "ROOT in chroot" dir
		install -d ${clst_chroot_path}/${clst_root_path}/etc
		install -d ${clst_chroot_path}/${clst_root_path}${clst_port_conf}

		# Setup make.conf and make.profile link in "ROOT in chroot":
		copy_to_chroot ${clst_chroot_path}${clst_make_conf} ${clst_root_path}${clst_port_conf}

		# Enter chroot, execute our build script
		exec_in_chroot \
			${clst_shdir}/${clst_target}/${clst_target}-chroot.sh \
			|| exit 1
	;;

	preclean)
		exec_in_chroot ${clst_shdir}/${clst_target}/${clst_target}-preclean-chroot.sh || exit 1
	;;

	clean)
		# Clean out man, info and doc files
		rm -rf usr/share/{man,doc,info}/*
		# Zap all .pyc and .pyo files
		find . -iname "*.py[co]" -exec rm -f {} \;
	;;

	*)
		exit 1
	;;
esac
exit $?
