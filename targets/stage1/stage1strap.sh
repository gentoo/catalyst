# Copyright 1999-2003 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/stage1/Attic/stage1strap.sh,v 1.2 2003/10/15 05:22:53 zhen Exp $

cp ${SHAREDIR}/bin/stage1.sh ${CHROOTDIR}/tmp
cp ${SHAREDIR}/bin/build.sh ${CHROOTDIR}/tmp

## We shouldn't need to export anything in catalyst, since the
## main program does that for us.

#CHOST is for the gcc-config initialization step
#export MAINVERSION MAINARCH CHOST BUILDTYPE
#get our make.conf instide our new tree
#good idea because make.conf should be there.
#also necessary because the "stage1" script runs gcc-config, which
#uses portage, which requires /etc/make.conf to exist.

makeconf ${CHROOTDIR}/tmp/stage1root
$CHROOT . /tmp/stage1.sh build /tmp/stage1root
[ $? -ne 0 ] && die "Stage 1 build failure"

