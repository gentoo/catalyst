# Copyright 1999-2003 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/embedded/Attic/embedded.sh,v 1.2 2004/04/04 16:58:15 zhen Exp $

case $1 in
enter)
	$clst_CHROOT $clst_chroot_path
	;;
run)
	$clst_CHROOT $clst_chroot_path /bin/bash << EOF
	/usr/sbin/env-update
	source /etc/profile
	export USE="\${clst_embedded_use}"
	rm -f /tmp/stage23
	if [ -n "${clst_CCACHE}" ]
	then
		export FEATURES="ccache"
		emerge --oneshot --nodeps ccache || exit 1
	fi
	export CONFIG_PROTECT="-*"
	
	#portage needs to be merged manually with USE="build" set to avoid frying our
	#make.conf. emerge system could merge it otherwise.
	#USE="build" emerge portage

	if [ ! -d "/tmp/mergeroot" ]
	then
		install -d /tmp/mergeroot
	fi
	
	if [ -n "${clst_PKGCACHE}" ]
	then
		ROOT=/tmp/mergeroot emerge -O $clst_embedded_packages --usepkg --buildpkg || exit 1
	else
		ROOT=/tmp/mergeroot emerge -O $clst_embedded_packages || exit 1
	fi
EOF
	[ $? -ne 0 ] && exit 1
	;;
preclean)
	$clst_CHROOT $clst_chroot_path /bin/bash << EOF
	env-update
	source /etc/profile
	if [ -n "${clst_CCACHE}" ]
	then
		emerge -C dev-util/ccache || exit 1
	fi
EOF
	[ $? -ne 0 ] && exit 1
	;;
clean)
	exit 0
	;;
*)
	exit 1
	;;
esac
exit 0
