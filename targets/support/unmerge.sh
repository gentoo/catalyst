#!/bin/bash

source /tmp/chroot-functions.sh

update_env_settings

run_emerge -C ${clst_packages}

if [ "${clst_livecd_type}" == "gentoo-release-livecd" ]
then
	mv -f /var/db /usr/livecd
fi

exit 0
