#!/bin/bash
# Copyright 1999-2003 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/stage1/Attic/build.sh,v 1.3 2003/10/15 05:22:53 zhen Exp $

for x in `cat /usr/portage/profiles/${REL_TYPE}-${MAINARCH}-${REL_VERSION}/packages.build`
do
	myp=$(grep -E "${x}(-[^[:space:]]*)?[[:space:]]*$" /usr/portage/profiles/${REL_TYPE}-i${MAINARCH}-${REL_VERSION}/packages | grep -v '^#' | sed -e 's:^\*::' | cat )
	if [ "$myp" = "" ]
	then
		#if not in the system profile, include it anyway
		echo $x
	else
		echo $myp
	fi
done

