# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/livecd-stage2/Attic/unmerge.sh,v 1.3 2004/09/16 05:53:50 zhen Exp $

$clst_CHROOT $clst_chroot_path /bin/bash << EOF
	emerge -C $*
EOF
exit 0
