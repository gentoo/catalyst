#!/bin/bash
# Copyright 1999-2005 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/netboot/netboot-image.sh,v 1.7 2005/12/19 15:03:25 wolf31o2 Exp $

. /tmp/chroot-functions.sh

update_env_settings

echo "Copying files to ${clst_root_path}"
clst_files="/bin/busybox ${clst_files} "
for f in ${clst_files}
do 
	copy_file ${f}
done
echo "Done copying files"
