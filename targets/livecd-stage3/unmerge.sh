# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/livecd-stage3/Attic/unmerge.sh,v 1.1 2004/01/10 22:23:44 drobbins Exp $

$clst_CHROOT $clst_chroot_path /bin/bash << EOF
	emerge -C $*
EOF
exit 0
