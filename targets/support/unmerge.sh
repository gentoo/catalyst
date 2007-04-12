#!/bin/bash

source /tmp/chroot-functions.sh

update_env_settings

run_emerge -C ${clst_packages}

case ${clst_livecd_type} in
	gentoo-release-livecd ) mv -f /var/db /usr/livecd ;;
esac

exit 0
