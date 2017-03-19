#!/bin/bash

source ${clst_shdir}/support/functions.sh

# Only put commands in this section that you want every target to execute.
# This is a global default file and will affect every target
case $1 in
	enter)
		${clst_CHROOT} ${clst_chroot_path}
	;;

	run)
		shift
		export clst_packages="$*"
		exec_in_chroot \
			${clst_shdir}/${clst_target}/${clst_target}-chroot.sh
	;;

	preclean)
		clear_portage
		exec_in_chroot ${clst_shdir}/${clst_target}/${clst_target}-preclean-chroot.sh
	;;

	clean)
		exit 0
	;;

	*)
		exit 1
	;;
esac
exit $?
