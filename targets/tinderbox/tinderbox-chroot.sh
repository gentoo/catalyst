#!/bin/bash

source /tmp/chroot-functions.sh

# START THE BUILD
setup_pkgmgr

# Backup pristine system

rsync -avx --exclude "/root/" --exclude "/tmp/" --exclude "/usr/portage/" / \
	/tmp/rsync-bak/

for x in ${clst_tinderbox_packages}
do
	if [ -n "${clst_VERBOSE}" ]
	then
		run_merge --usepkg --buildpkg --newuse -vp $x
		echo "Press any key within 15 seconds to pause the build..."
		read -s -t 15 -n 1
		if [ $? -eq 0 ]
		then
			echo "Press any key to continue..."
			read -s -n 1
		fi
	fi

	mkdir -p /tmp/packages/$x
	export PORT_LOGDIR="/tmp/packages/$x"
	run_merge $x

	if [ "$?" != "0" ]
	then
		echo "! $x" >> /tmp/tinderbox.log
	else
		echo "$x" >> /tmp/tinderbox.log
	fi
	echo "Syncing from original pristine tinderbox snapshot..."
	rsync -avx --delete --exclude "/root/*" --exclude "/tmp/" --exclude \
		"/usr/portage/" /tmp/rsync-bak/ /
done
