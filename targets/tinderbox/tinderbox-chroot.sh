#!/bin/bash

source /tmp/chroot-functions.sh

# START THE BUILD
setup_pkgmgr

# Backup pristine system

rsync -avx --exclude "/root/" --exclude "/tmp/" --exclude "${clst_portdir}/" / \
	/tmp/rsync-bak/

for x in ${clst_tinderbox_packages}
do
	if [[ "${clst_VERBOSE}" == "true" ]]
	then
		run_merge --usepkg --buildpkg --newuse -vp $x
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
		"${clst_portdir}/" /tmp/rsync-bak/ /
done
