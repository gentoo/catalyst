#!/bin/bash
# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/stage1/Attic/stage1-preclean2-chroot.sh,v 1.2 2004/05/17 01:21:17 zhen Exp $
		
#now, some finishing touches to initialize gcc-config....
unset ROOT

if [ -e /usr/bin/gcc-config ]
then
	mythang=$( cd /etc/env.d/gcc; ls ${clst_CHOST}-* )
	echo $mythang; sleep 20
	gcc-config ${mythang}; /usr/sbin/env-update; source /etc/profile
fi

#stage1 is not going to have anything in zoneinfo, so save our Factory timezone
rm -f /etc/localtime
cp /usr/share/zoneinfo/Factory /etc/localtime
