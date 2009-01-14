#!/bin/bash

. ${clst_sharedir}/targets/support/functions.sh

case $1 in
	enter)
	;;
	run)
		# Setup "ROOT in chroot" dir
		install -d ${clst_chroot_path}/${clst_root_path}/etc

		# Setup make.conf and make.profile link in "ROOT in chroot":
		for i in make.conf make.globals make.profile; do
			copy_to_chroot ${clst_chroot_path}/etc/${i} /${clst_root_path}/etc
		done

		# Enter chroot, execute our build script
		exec_in_chroot \
			${clst_sharedir}/targets/${clst_target}/${clst_target}-chroot.sh \
			|| exit 1
	;;
	preclean)
		exec_in_chroot ${clst_sharedir}/targets/${clst_target}/${clst_target}-preclean-chroot.sh /${clst_root_path} || exit 1
	;;
	clean)
	;;
	*)
		exit 1
	;;
esac
exit $?
