# Copyright 1999-2003 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/grp/Attic/grp.sh,v 1.4 2004/01/10 22:23:44 drobbins Exp $

case $1 in
enter)
	$clst_CHROOT $clst_chroot_path
	;;
run)
	shift
	export clst_grp_type=$1
	shift
	export clst_grp_target=$1
	shift
	export clst_grp_packages="$*"
	$clst_CHROOT $clst_chroot_path /bin/bash << EOF
	env-update
	source /etc/profile
	if [ -n "${clst_CCACHE}" ]
	then
		export FEATURES="ccache"
		emerge --oneshot --nodeps ccache || exit 1
	fi
	if [ ${clst_rel_type} = "hardened" ]
	then
		emerge --oneshot --nodeps hardened-gcc || exit 1
	fi
	export CONFIG_PROTECT="-*"
	
	USE="build" emerge portage
	#turn off auto-use:
	export USE_ORDER="env:conf:defaults"	
	if [ "$clst_grp_type" = "pkgset" ]
	then
		unset DISTDIR
		export PKGDIR="/tmp/grp/$clst_grp_target"
		emerge --usepkg --buildpkg --noreplace $clst_grp_packages || exit 1
	else
		export DISTDIR="/tmp/grp/$clst_grp_target"
		unset PKGDIR
		emerge --fetchonly $clst_grp_packages || exit 1
	fi
EOF
	[ $? -ne 0 ] && exit 1
	;;
*)
	exit 1
	;;
esac
exit 0
