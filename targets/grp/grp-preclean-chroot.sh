#!/bin/bash
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/grp/grp-preclean-chroot.sh,v 1.11 2006/10/02 20:41:54 wolf31o2 Exp $

. /tmp/chroot-functions.sh
update_env_settings
cleanup_distcc

gconftool-2 --shutdown
