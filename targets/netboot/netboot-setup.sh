#!/bin/bash
# Copyright 1999-2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/netboot/Attic/netboot-setup.sh,v 1.1 2004/10/11 14:28:27 zhen Exp $

/usr/sbin/env-update
source /etc/profile

[ -f /tmp/envscript ] && source /tmp/envscript

if [ -n "${clst_CCACHE}" ]
then
	emerge -b -k --oneshot --nodeps ccache || exit 1
fi
		
if [ -n "${clst_DISTCC}" ]
then   
	USE="-gtk -gnome" emerge -b -k --oneshot --nodeps distcc || exit 1
fi

mkdir -p ${IMAGE_PATH}
