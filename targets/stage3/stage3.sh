# Copyright 1999-2003 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/stage3/Attic/stage3.sh,v 1.2 2003/10/28 22:09:23 drobbins Exp $

case $1 in
enter)
	$CHROOT $chroot_path
	;;
run)
	$CHROOT $chroot_path /bin/bash << EOF
	env-update
	source /etc/profile
	if [ -n "${CCACHE}" ]
	then
		emerge --oneshot --nodeps --usepkg --buildpkg ccache || exit 1
	fi
	if [ ${rel_type} = "hardened" ]
	then
		emerge --oneshot --nodeps hardened-gcc || exit 1
	fi
	export CONFIG_PROTECT="-*"
	emerge system --usepkg --buildpkg || exit 1
EOF
	[ $? -ne 0 ] && exit 1
	;;
clean)
	$CHROOT $chroot_path /bin/bash << EOF
	env-update
	source /etc/profile
	if [ -n "${CCACHE}" ]
	then
		emerge -C ccache || exit 1
	fi
EOF
	[ $? -ne 0 ] && exit 1
	;;
*)
	exit 1
	;;
esac
