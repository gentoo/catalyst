#!/bin/bash
# Copyright 1999-2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/netboot/netboot-image.sh,v 1.5 2005/04/04 17:48:33 rocket Exp $

. /tmp/chroot-functions.sh

update_env_settings


echo "copying files to ${clst_root_path}"
clst_files="/bin/busybox ${clst_files} "
for f in ${clst_files}
do 
	copy_file ${f}
done
echo "done copying files"
