# Copyright 1999-2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/livecd-stage2/Attic/unmerge.sh,v 1.5 2004/10/22 04:23:16 wolf31o2 Exp $

$clst_CHROOT $clst_chroot_path /bin/bash << EOF
	EMERGE_WARNING_DELAY=0 emerge -C $*
EOF
exit 0
