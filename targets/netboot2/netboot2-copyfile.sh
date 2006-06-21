#!/bin/bash
# Copyright 1999-2005 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/netboot2/netboot2-copyfile.sh,v 1.2 2006/06/21 22:11:54 wolf31o2 Exp $

. /tmp/chroot-functions.sh

update_env_settings

echo ">>> Copying initramfs files to ${clst_merge_path} (in chroot) ..."
[ ! -d "${clst_merge_path}" ] && mkdir -p ${clst_merge_path}
for f in ${clst_files}
do 
	# copy it to the merge path
	cp -af --parents ${f} ${clst_merge_path}

	# if the file is an ELF binary, strip unneeded stuff from it
	if [ -x "${f}" ] && [ ! -L "${f}" ]; then
		if [ "$(head -c 4 ${f} 2>/dev/null | tail -c 3)" = "ELF" ]; then
			strip -R .comment -R .note ${clst_merge_path}${f}
		fi
	fi
done
echo ""
