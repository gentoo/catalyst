#!/bin/bash

source ${clst_shdir}/support/functions.sh

case $1 in
	run)
		shift
		export clst_packages="$*"
		exec_in_chroot ${clst_shdir}/${clst_target}/chroot.sh
	;;

	preclean)
		exec_in_chroot ${clst_shdir}/${clst_target}/preclean-chroot.sh
	;;

	clean)
		exit 0
	;;

	*)
		exit 1
	;;
esac
exit $?
