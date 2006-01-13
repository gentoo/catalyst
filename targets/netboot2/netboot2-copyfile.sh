#!/bin/bash
# Copyright 1999-2005 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/netboot2/netboot2-copyfile.sh,v 1.1 2006/01/13 15:09:07 rocket Exp $

. /tmp/chroot-functions.sh

update_env_settings

echo ">>> Copying initramfs files to ${clst_merge_path} (in chroot) ..."
[ ! -d "${clst_merge_path}" ] && mkdir -p ${clst_merge_path}
for f in ${clst_files}
do 
	cp -af --parents ${f} ${clst_merge_path}
done
echo ""
