# $Header: /var/cvsroot/gentoo/src/catalyst/targets/embedded/unmerge.sh,v 1.4 2006/10/02 20:41:54 wolf31o2 Exp $

${clst_CHROOT} ${clst_chroot_path} /bin/bash << EOF
	ROOT=/tmp/mergeroot emerge -C $* || exit 1
EOF
