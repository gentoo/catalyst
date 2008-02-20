#!/bin/bash

source /tmp/chroot-functions.sh

# START THE BUILD
setup_portage

# Backup pristine system

rsync -avx --exclude "/root/" --exclude "/tmp/" --exclude "/usr/portage/" / \
	/tmp/rsync-bak/ 

for x in ${clst_tinderbox_packages}
do
	if [ -n "${clst_VERBOSE}" ]
	then
		run_emerge --usepkg --buildpkg --newuse -vp $x
		echo "Press any key within 15 seconds to pause the build..."
		read -s -t 15 -n 1
		if [ $? -eq 0 ]
		then
			echo "Press any key to continue..."
			read -s -n 1
		fi
	fi

	mkdir -source /tmp/packages/$x
	export PORT_LOGDIR="/tmp/packages/$x"
	run_emerge $x

	if [ "$?" != "0" ]
	then
		echo "! $x" >source /tmp/tinderbox.log	
	else
		echo "$x" >source /tmp/tinderbox.log
	fi
	echo "Syncing from original pristine tinderbox snapshot..."
	rsync -avx --delete --exclude "/root/*" --exclude "/tmp/" --exclude \
		"/usr/portage/source /tmp/rsync-bak/ /
done
