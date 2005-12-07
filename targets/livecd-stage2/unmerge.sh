# Copyright 1999-2005 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/livecd-stage2/Attic/unmerge.sh,v 1.10 2005/12/07 21:57:59 wolf31o2 Exp $

${clst_CHROOT} ${clst_chroot_path} /bin/bash << EOF
	EMERGE_WARNING_DELAY=0 emerge -C $*
EOF

exit 0
