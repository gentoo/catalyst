#!/bin/bash

source /tmp/chroot-functions.sh

## START BUILD
setup_portage

unset DISTDIR

# Don't grab MS core fonts, etc.
export USE="${USE} ${clst_HOSTUSE} ${clst_use}"

if [ "${clst_grp_type}" = "pkgset" ]
then
	unset DISTDIR
	export PKGDIR="/tmp/grp/${clst_grp_target}"

	run_emerge --usepkg --buildpkg --noreplace --newuse ${clst_myemergeopts} \
		${clst_grp_packages} || exit 1
else
	DISTDIR="/tmp/grp/${clst_grp_target}" run_emerge --fetchonly \
		${clst_grp_packages} || exit 1
	unset PKGDIR
fi
