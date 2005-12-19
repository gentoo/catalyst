# Copyright 1999-2005 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/support/unmerge.sh,v 1.3 2005/12/19 16:52:01 wolf31o2 Exp $


source /tmp/chroot-functions.sh

update_env_settings

run_emerge -C "${clst_packages}"
exit 0
