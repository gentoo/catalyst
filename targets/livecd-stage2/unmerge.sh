# Copyright 1999-2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/livecd-stage2/Attic/unmerge.sh,v 1.4 2004/10/15 02:46:58 zhen Exp $

$clst_CHROOT $clst_chroot_path /bin/bash << EOF
	emerge -C $*
EOF
exit 0
