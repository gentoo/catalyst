#!/bin/bash
# Copyright 1999-2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/livecd/runscript-support/Attic/gamecdfs-update.sh,v 1.6 2004/12/16 17:51:23 wolf31o2 Exp $

# we grab our configuration
source "${clst_gamecd_conf}" || exit 1

# here we replace out game information into several files
sed -i -e "s:livecd:gamecd:" /etc/hosts
sed -i -e "s:##GAME_NAME:${GAME_NAME}:" /etc/motd

# here we setup our xinitrc
echo "exec ${GAME_EXECUTABLE}" > /etc/X11/xinit/xinitrc

# we add spind to default here since we don't want the CD to spin down
rc-update add spind default
