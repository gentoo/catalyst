# Copyright 1999-2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/livecd-stage2/Attic/unmerge.sh,v 1.8 2005/04/04 17:48:33 rocket Exp $

${clst_CHROOT} ${clst_chroot_path} /bin/bash << EOF
	EMERGE_WARNING_DELAY=0 emerge -C $*
EOF

if [ -d /usr/livecd/profiles ]
then
	mkdir -p /usr/portage/profiles
	ln -sf /usr/livecd/profiles /usr/portage/profiles
fi

exit 0
