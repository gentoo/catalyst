#!/bin/bash
# Copyright 1999-2003 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/stage1/Attic/build.sh,v 1.4 2003/10/30 19:42:56 drobbins Exp $

for x in `cat /usr/portage/profiles/${clst_rel_type}-${clst_mainarch}-${clst_rel_version}/packages.build`
do
	myp=$(grep -E "${x}(-[^[:space:]]*)?[[:space:]]*$" /usr/portage/profiles/${clst_rel_type}-${clst_mainarch}-${clst_rel_version}/packages | grep -v '^#' | sed -e 's:^\*::' | cat )
	if [ "$myp" = "" ]
	then
		#if not in the system profile, include it anyway
		echo $x
	else
		echo $myp
	fi
done

