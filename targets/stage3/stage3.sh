# Copyright 1999-2003 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/stage3/Attic/stage3.sh,v 1.1 2003/10/15 05:33:03 zhen Exp $

$CHROOT . /bin/bash << EOF
	env-update
	source /etc/profile
	if [ ${CCACHE} -eq 1 ]
	then
		emerge --oneshot --nodeps --usepkg --buildpkg ccache || exit 1
	fi
	if [ ${REL_TYPE} = "hardened" ]
	then
		emerge --oneshot --nodeps hardened-gcc || exit 1
	fi
	export CONFIG_PROTECT="-*"
	emerge system --usepkg --buildpkg || exit 1
EOF

[ $? -ne 0 ] && die "Stage 3 build failure"

