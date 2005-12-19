#!/bin/bash
# Copyright 1999-2005 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2

. /tmp/chroot-functions.sh

update_env_settings

setup_myfeatures
setup_myemergeopts

# Setup the environment
export FEATURES="${clst_myfeatures}"

## START BUILD
setup_portage
# Turn off auto-use:
export USE_ORDER="env:pkg:conf:defaults"	

echo "Bringing system up to date using profile specific use flags"
export USE="${USE} ${clst_HOSTUSE}"
run_emerge -u system

echo "Emerging packages using stage4 use flags"
if [ -n "${clst_use}" ]
then 
	export USE="${USE} ${clst_HOSTUSE}"
else	
	USE="${clst_use}"
fi

run_emerge "${clst_packages}"
