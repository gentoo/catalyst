#!/bin/bash

source /tmp/chroot-functions.sh

## START BUILD
setup_pkgmgr

if [ "${clst_grp_type}" = "pkgset" ]
then
	export PKGDIR="/tmp/grp/${clst_grp_target}"

	run_merge --usepkg --buildpkg --noreplace --newuse ${clst_myemergeopts} \
		${clst_grp_packages} || exit 1
else
	DISTDIR="/tmp/grp/${clst_grp_target}" run_merge --fetchonly \
		${clst_grp_packages} || exit 1
fi
