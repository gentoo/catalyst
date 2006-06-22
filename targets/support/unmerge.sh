# Copyright 1999-2005 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/support/unmerge.sh,v 1.5 2006/06/22 11:43:34 wolf31o2 Exp $


source /tmp/chroot-functions.sh

update_env_settings

run_emerge -C ${clst_packages}

exit 0
