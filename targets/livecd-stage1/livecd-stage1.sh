# Copyright 1999-2003 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/livecd-stage1/Attic/livecd-stage1.sh,v 1.7 2004/02/11 03:31:55 zhen Exp $

case $1 in
enter)
	$clst_CHROOT $clst_chroot_path
	;;
run)
	shift
	$clst_CHROOT $clst_chroot_path /bin/bash << EOF
	env-update
	source /etc/profile
	if [ -n "${clst_ENVSCRIPT}" ]
	then
		source /tmp/envscript
		rm -f /tmp/envscript
	fi
	if [ -n "${clst_CCACHE}" ]
	then
		export FEATURES="ccache"
		emerge --oneshot --nodeps ccache || exit 1
	fi
	if [ -n "${clst_DISTCC}" ]
	then   
		export FEATURES="distcc"
		export DISTCC_HOSTS="${clst_distcc_hosts}"
		emerge --oneshot --nodeps distcc || exit 1
		echo "distcc:x:240:2:distccd:/dev/null:/bin/false" >> /$
		/usr/bin/distcc-config --install 2>&1 > /dev/null
		/usr/bin/distccd 2>&1 > /dev/null
	fi
	export CONFIG_PROTECT="-*"
	USE="build" emerge portage
	#turn off auto-use:
	export USE_ORDER="env:conf:defaults"	
	for x in $*
	do
		if [ -n "${clst_PKGCACHE}" ]
		then
			emerge --usepkg --buildpkg "\$x" || exit 1
			if [ "\$?" -ne 0 ]
			then
				echo "\$x failed to build."
				exit 1
			fi
		else
			emerge "\$x"
			if [ "\$?" -ne 0 ]
			then
				echo "\$x failed to build."
				exit 1
			fi
		fi
	done
EOF
	[ $? -ne 0 ] && exit 1
	;;
*)
	exit 1
	;;
esac
exit 0
