#!/bin/bash
# Copyright 1999-2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/stage1/Attic/stage1-preclean2-chroot.sh,v 1.8 2005/02/28 23:21:09 wolf31o2 Exp $
		
# now, some finishing touches to initialize gcc-config....
unset ROOT

if [ -x /usr/bin/gcc-config ]
then
	mythang=$( cd /etc/env.d/gcc; ls ${clst_CHOST}-* | head -n 1 )
	gcc-config ${mythang}; /usr/sbin/env-update; source /etc/profile
fi

# stage1 is not going to have anything in zoneinfo, so save our Factory timezone
if [ -d /usr/share/zoneinfo ] ; then
	rm -f /etc/localtime
	cp /usr/share/zoneinfo/Factory /etc/localtime
else
	echo UTC > /etc/TZ
fi

# this cleans out /var/db, but leaves behind files portage needs for removal
find /var/db/pkg -type f | grep -v '\(COUNTER\|CONTENTS\|ebuild\)' | xargs rm -f
