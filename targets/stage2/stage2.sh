# Copyright 1999-2003 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/stage2/Attic/stage2.sh,v 1.1 2003/10/15 05:23:14 zhen Exp $

$CHROOT . /bin/bash << EOF
	env-update
	source /etc/profile
	mkdir -p /usr/portage/packages/All
	export EMERGE_OPTS="--usepkg --buildpkg"
	if [ ${CCACHE} -eq 1 ]
	then
		emerge --oneshot --nodeps ccache || exit 1
	fi

	/usr/portage/scripts/bootstrap.sh || exit 1
EOF

[ $? -ne 0 ] && die "Stage 2 build failure"

