#!/bin/bash
# Copyright 1999-2005 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2

. /tmp/chroot-functions.sh

update_env_settings

# Only run depscan.sh if modules exist
if [ -n "$(ls /lib/modules)" ]
then
	/sbin/depscan.sh
	find /lib/modules -name modules.dep -exec touch {} \;
fi
