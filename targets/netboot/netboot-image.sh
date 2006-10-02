#!/bin/bash
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/netboot/netboot-image.sh,v 1.8 2006/10/02 20:41:54 wolf31o2 Exp $

. /tmp/chroot-functions.sh

update_env_settings

echo "Copying files to ${clst_root_path}"
clst_files="/bin/busybox ${clst_files} "
for f in ${clst_files}
do 
	copy_file ${f}
done
echo "Done copying files"
