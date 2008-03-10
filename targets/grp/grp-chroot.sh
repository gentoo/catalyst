#!/bin/bash

source /tmp/chroot-functions.sh

## START BUILD
setup_pkgmgr

export DISTDIR="/tmp/grp/${clst_grp_target}"
export PKGDIR="/tmp/grp/${clst_grp_target}"

if [ "${clst_grp_type}" != "pkgset" ]
then
	export clst_FETCH=1
	# This is necessary since we're setting the above variable and the emerge
	# opts have already been set
	setup_myemergeopts
fi

run_merge --noreplace ${clst_grp_packages} || exit 1
