#!/bin/bash
# Copyright 1999-2005 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2

/usr/sbin/env-update
source /etc/profile

case ${clst_mainarch} in
   mips)   ;;
   *)
	/sbin/depscan.sh
	find /lib/modules -name modules.dep -exec touch {} \;
	;;
esac
