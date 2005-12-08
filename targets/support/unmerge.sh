# Copyright 1999-2005 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/support/unmerge.sh,v 1.1 2005/12/08 15:16:48 rocket Exp $


source /tmp/chroot-functions.sh

check_portage_version
update_env_settings

run_emerge -C "${clst_packages}"

exit 0
