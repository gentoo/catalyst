# Copyright 1999-2003 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/stage2/Attic/stage2.sh,v 1.2 2003/10/28 22:09:23 drobbins Exp $

case $1 in
run)
	$CHROOT . /bin/bash << EOF
	env-update
	source /etc/profile
	mkdir -p /usr/portage/packages/All
	export EMERGE_OPTS="--usepkg --buildpkg"
	if [ ${CCACHE} -eq 1 ]
	then
		emerge --oneshot --nodeps ccache || exit 1
	fi

	/usr/portage/scripts/bootstrap.sh || exit 1
EOF
	[ $? -ne 0 ] && exit 1 
	;;
clean)
	# we need to have catalyst un-bind-mount things before
	# we clean up.
	$CHROOT . /bin/bash << EOF
	if [ ${CCACHE} -eq 1 ]
	then
		emerge -C ccache
	fi
	rm -rf /usr/portage
	rm -rf /tmp/*
EOF
	[ $? -ne 0 ] && exit 1 
	;;
*)
	exit 1
	;;
esac
