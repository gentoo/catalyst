#!/bin/bash
# Copyright 1999-2003 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/stage1/Attic/build.sh,v 1.6 2004/03/30 19:45:14 zhen Exp $

for x in `cat /etc/make.profile/packages.build | grep -v '^#'`
do
	myp=$(grep -E "${x}(-[^[:space:]]*)?[[:space:]]*$" /etc/make.profile/packages | grep -v '^#' | sed -e 's:^\*::' | cat )
	if [ "$myp" = "" ]
	then
		#if not in the system profile, include it anyway
		echo $x
	else
		echo $myp
	fi
done

