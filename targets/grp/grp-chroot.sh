#!/bin/bash
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/grp/grp-chroot.sh,v 1.26 2006/10/02 20:41:54 wolf31o2 Exp $

. /tmp/chroot-functions.sh

update_env_settings

[ -f /tmp/envscript ] && source /tmp/envscript

setup_myfeatures

# Setup the environment
export FEATURES="${clst_myfeatures}"
## START BUILD
setup_portage

unset DISTDIR

# Don't grab MS core fonts, etc.
export USE="${USE} ${clst_HOSTUSE} ${clst_use}"

if [ "${clst_grp_type}" = "pkgset" ]
then
	unset DISTDIR
	export PKGDIR="/tmp/grp/${clst_grp_target}"

	if [ -n "${clst_FETCH}" ]
	then
		export clst_myemergeopts="${clst_myemergeopts} -f"
	fi

	if [ -n "${clst_VERBOSE}" ]
	then
		emerge --usepkg --buildpkg --noreplace --newuse -vp \
			${clst_myemergeopts} ${clst_grp_packages} || exit 1
		echo "Press any key within 15 seconds to pause the build..."
		read -s -t 15 -n 1
		if [ $? -eq 0 ]
		then
			echo "Press any key to continue..."
			read -s -n 1
		fi
	fi
	emerge --usepkg --buildpkg --noreplace --newuse ${clst_myemergeopts} \
		${clst_grp_packages} || exit 1
else
	DISTDIR="/tmp/grp/${clst_grp_target}" emerge --fetchonly \
		${clst_grp_packages} || exit 1
	unset PKGDIR
fi
