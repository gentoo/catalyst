# $Header: /var/cvsroot/gentoo/src/catalyst/targets/livecd-stage1/livecd-stage1-controller.sh,v 1.12 2006/10/02 20:41:54 wolf31o2 Exp $

. ${clst_sharedir}/targets/support/functions.sh

## START RUNSCRIPT

case $1 in
	build_packages)
		shift
		export clst_packages="$*"
		mkdir -p ${clst_chroot_path}/usr/livecd
		echo "${clst_packages}" > ${clst_chroot_path}/usr/livecd/grppkgs.txt
		exec_in_chroot \
			${clst_sharedir}/targets/${clst_target}/${clst_target}-chroot.sh
		;;
	clean)
		find ${clst_chroot_path}/usr/lib -iname "*.pyc" -exec rm -f {} \;
		;;
esac
exit $?
