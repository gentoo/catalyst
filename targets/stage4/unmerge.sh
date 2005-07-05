# Copyright 1999-2005 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/stage4/Attic/unmerge.sh,v 1.2 2005/07/05 21:53:41 wolf31o2 Exp $

${clst_CHROOT} ${clst_chroot_path} /bin/bash << EOF
	EMERGE_WARNING_DELAY=0 emerge -C $*
EOF

exit 0
