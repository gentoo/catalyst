# Copyright 1999-2003 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/livecd-stage1/Attic/livecd-stage1.sh,v 1.4 2004/01/12 06:35:05 drobbins Exp $

case $1 in
enter)
	$clst_CHROOT $clst_chroot_path
	;;
run)
	shift
	$clst_CHROOT $clst_chroot_path /bin/bash << EOF
	env-update
	source /etc/profile
	if [ -n "${clst_CCACHE}" ]
	then
		export FEATURES="ccache"
		emerge --oneshot --nodeps ccache || exit 1
	fi
	export CONFIG_PROTECT="-*"
	USE="build" emerge portage
	#turn off auto-use:
	export USE_ORDER="env:conf:defaults"	
	for x in "$@" 
	do
		if [ -n "${clst_PKGCACHE}" ]
		then
			emerge --usepkg --buildpkg --noreplace "\$x" || exit 1
		else
			emerge --noreplace "\$x" || exit 1
		fi
	done
EOF
	[ $? -ne 0 ] && exit 1
	;;
*)
	exit 1
	;;
esac
exit 0
