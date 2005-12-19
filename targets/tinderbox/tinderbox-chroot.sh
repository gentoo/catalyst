#!/bin/bash
# Copyright 1999-2005 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/tinderbox/tinderbox-chroot.sh,v 1.16 2005/12/19 19:10:04 wolf31o2 Exp $

. /tmp/chroot-functions.sh

update_env_settings

setup_myfeatures

# Setup the environment
export FEATURES="${clst_myfeatures}"

# START THE BUILD
setup_portage

# Turn off auto-use:
export USE_ORDER="env:pkg:conf:defaults"	
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

	mkdir -p /tmp/packages/$x
	export PORT_LOGDIR="/tmp/packages/$x"
	run_emerge --usepkg --buildpkg --newuse $x

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
