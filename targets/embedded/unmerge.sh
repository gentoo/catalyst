# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/embedded/unmerge.sh,v 1.1 2004/10/12 18:01:22 zhen Exp $

${clst_CHROOT} ${clst_chroot_path} /bin/bash << EOF
	ROOT=/tmp/mergeroot emerge -C $* || exit 1
EOF
