# Copyright 1999-2003 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/stage3/Attic/stage3.sh,v 1.11 2004/03/26 17:03:29 zhen Exp $

case $1 in
enter)
	$clst_CHROOT $clst_chroot_path
	;;
run)
	$clst_CHROOT $clst_chroot_path /bin/bash << EOF
	env-update
	source /etc/profile
	if [ -n ${ENVSCRIPT} ]
	then
		source /tmp/envscript
		rm -f /tmp/envscript
	fi
	cat /etc/make.profile/make.defaults | grep GRP_STAGE23_USE > /tmp/stage23
	source /tmp/stage23
	export USE="-* \${clst_HOSTUSE} \${GRP_STAGE23_USE}"
	rm -f /tmp/stage23
	export CONFIG_PROTECT="-*"
	
	#portage needs to be merged manually with USE="build" set to avoid frying our
	#make.conf. emerge system could merge it otherwise.
	USE="build" emerge portage
	if [ -n "${clst_CCACHE}" ]
	then
		export FEATURES="ccache"
		emerge --oneshot --nodeps ccache || exit 1
	fi
	if [ -n "${clst_DISTCC}" ]
        then   
                export FEATURES="distcc"
                export DISTCC_HOSTS="${clst_distcc_hosts}"
                USE="-gnome -gtk" emerge --oneshot --nodeps distcc || exit 1
                echo "distcc:x:240:2:distccd:/dev/null:/bin/false" >> /etc/passwd
                /usr/bin/distcc-config --install 2>&1 > /dev/null
                /usr/bin/distccd 2>&1 > /dev/null
        fi
	if [ -n "${clst_PKGCACHE}" ]
	then
		emerge system --usepkg --buildpkg || exit 1
	else
		emerge system || exit 1
	fi
EOF
	[ $? -ne 0 ] && exit 1
	;;
preclean)
	$clst_CHROOT $clst_chroot_path /bin/bash << EOF
	env-update
	source /etc/profile
	if [ -n "${clst_CCACHE}" ]
	then
		emerge -C dev-util/ccache || exit 1
	fi
	if [ -n "${clst_DISTCC}" ]
	then
		emerge -C sys-devel/distcc || exit 1
		userdel distcc
	fi
EOF
	[ $? -ne 0 ] && exit 1
	;;
clean)
	exit 0
	;;
*)
	exit 1
	;;
esac
exit 0
