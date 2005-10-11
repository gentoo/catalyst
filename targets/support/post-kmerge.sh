#!/bin/bash
# Copyright 1999-2005 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2

/usr/sbin/env-update
source /etc/profile

# Only run depscan.sh if modules exist
if [ -n "$(ls /lib/modules)" ]
then
	/sbin/depscan.sh
	find /lib/modules -name modules.dep -exec touch {} \;
fi

#case ${clst_mainarch} in
#   mips)   ;;
#   *)
#	/sbin/depscan.sh
#	find /lib/modules -name modules.dep -exec touch {} \;
#	;;
#esac
