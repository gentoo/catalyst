#!/bin/bash
# Copyright 1999-2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/tinderbox/tinderbox-chroot.sh,v 1.11 2005/04/04 17:48:33 rocket Exp $

. /tmp/chroot-functions.sh

update_env_settings

setup_myfeatures

# setup the environment
export FEATURES="${clst_myfeatures}"
export CONFIG_PROTECT="-*"

# START THE BUILD
setup_portage

#turn off auto-use:
export USE_ORDER="env:pkg:conf:defaults"	
#back up pristine system

rsync -avx --exclude "/root/" --exclude "/tmp/" --exclude "/usr/portage/" / /tmp/rsync-bak/ 

for x in ${clst_tinderbox_packages}
do
	if [ -n "${clst_VERBOSE}" ]
	then
		emerge --usepkg --buildpkg -vp $x
		echo "Press any key within 15 seconds to pause the build..."
		read -s -t 15 -n 1
		if [ $? -eq 0 ]
		then
			echo "Press any key to continue..."
			read -s -n 1
		fi
	fi
	
	emerge --usepkg --buildpkg $x
	
	if [ "$?" != "0" ]
	then
		echo "! $x" >> /tmp/tinderbox.log	
	else
		echo "$x" >> /tmp/tinderbox.log
	fi
	echo "Syncing from original pristine tinderbox snapshot..."
	rsync -avx --delete --exclude "/root/*" --exclude "/tmp/" --exclude "/usr/portage/*" /tmp/rsync-bak/ /
done
