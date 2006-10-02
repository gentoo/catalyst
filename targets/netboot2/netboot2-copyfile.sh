#!/bin/bash
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/netboot2/netboot2-copyfile.sh,v 1.4 2006/10/02 20:41:54 wolf31o2 Exp $

. /tmp/chroot-functions.sh

update_env_settings

echo ">>> Copying initramfs files to ${clst_merge_path} (in chroot) ..."
[ ! -d "${clst_merge_path}" ] && mkdir -p ${clst_merge_path}
for f in ${clst_files}
do 
	# copy it to the merge path
	cp -pPRf --parents ${f} ${clst_merge_path}

	# if the file is an ELF binary, strip unneeded stuff from it
	if [ -x "${f}" ] && [ ! -L "${f}" ]; then
		if [ "$(head -c 4 ${f} 2>/dev/null | tail -c 3)" = "ELF" ]; then
			strip -R .comment -R .note ${clst_merge_path}${f}
		fi
	fi
done
echo ""
