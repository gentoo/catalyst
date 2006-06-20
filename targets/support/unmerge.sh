# Copyright 1999-2005 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/support/unmerge.sh,v 1.4 2006/06/20 19:32:31 wolf31o2 Exp $


source /tmp/chroot-functions.sh

update_env_settings

# Add a fun loop, so we have to init portage every single time, causing it to
# run much slower to work around unexpected changes in portage 2.1 with respect
# to how it processes unmerge for non-existent packages.  A word to other
# developers out there.  Don't change behavior that people rely on without
# documenting the change.  It really sucks when you do.
for package in ${clst_packages}
do
	run_emerge -C "${package}"
done
exit 0
