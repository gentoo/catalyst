#!/bin/bash
# Copyright 1999-2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/livecd/runscript-support/Attic/gamecdfs-update.sh,v 1.4 2004/11/15 01:32:15 wolf31o2 Exp $

# These variables are to be used for creating the menu entry and also to tell
# the CD what to execute
GAME_NAME="Unreal Tournament 2004 Demo"
GAME_SHORT_NAME="UT2004 Demo"
GAME_EXECUTABLE="/usr/games/bin/ut2004demo"

sed -i -e "s:localhost:livecd.gentoo localhost:" /etc/hosts
sed -i -e "s:##GAME_NAME:${GAME_NAME}:" /etc/motd
sed -i -e "s:GAME_EXECUTABLE:${GAME_EXECUTABLE}:" /etc/X11/xinit/xinitrc

[ -x /sbin/openglify ] && /sbin/openglify
touch /etc/asound.state /etc/startx

cat > /usr/share/fluxbox/menu << EOF

[begin] (Gentoo)
	[exec] (GAME_SHORT_NAME) {GAME_EXECUTABLE}
	[exec] (Mozilla Firefox) {firefox http://www.gentoo.org}
	[exec] (Volume) {xterm -e "alsamixer"}

[submenu] (Setup Network)
	[exec] (net-setup eth0) {xterm -e "net-setup eth0"}
	[exec] (net-setup eth1) {xterm -e "net-setup eth1"}

[end]

[submenu] (Terminals)
	[exec] (xterm) {xterm -fg white -bg black}
[end]

[submenu] (Settings)
	[workspaces]   (Workspace List)
[submenu] (Styles) {Choose a style...}
	[stylesdir] (/usr/share/fluxbox/styles)
[end]

	[config] (Configure)
	[reconfig] (Reload config)
[end]

	[restart] (Restart)
[end]
EOF

sed -i -e 's:GAME_SHORT_NAME:${GAME_SHORT_NAME}:' \
    -i -e 's:GAME_EXECUTABLE:${GAME_EXECUTABLE}:' \
    /usr/share/fluxbox/menu
