# $Header: /var/cvsroot/gentoo/src/catalyst/targets/support/unmerge.sh,v 1.6 2006/10/02 20:41:54 wolf31o2 Exp $


source /tmp/chroot-functions.sh

update_env_settings

run_emerge -C ${clst_packages}

exit 0
