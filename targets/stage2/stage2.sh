# Copyright 1999-2003 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/stage2/Attic/stage2.sh,v 1.10 2004/03/31 21:56:23 zhen Exp $

case $1 in
enter)
	$clst_CHROOT $clst_chroot_path
	;;
run)
	$clst_CHROOT $clst_chroot_path /bin/bash << EOF
	env-update
	source /etc/profile
	if [ -n "${clst_ENVSCRIPT}" ]
	then
		source /tmp/envscript
		rm -f /tmp/envscript
	fi
	cat /etc/make.profile/make.defaults | grep GRP_STAGE23_USE > /tmp/stage23
	source /tmp/stage23
	export USE="-* \${clst_HOSTUSE} \${GRP_STAGE23_USE}"
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
		export EMERGE_OPTS="--usepkg --buildpkg"
	fi
	if [ -f /usr/portage/profiles/${clst_profile}/parent ]
    then
    	export clst_bootstrap="bootstrap-cascade.sh"
    else
    	export clst_bootstrap=bootstrap.sh
    fi
	/usr/portage/scripts/\${clst_bootstrap} || exit 1
EOF
	[ $? -ne 0 ] && exit 1 
	;;
preclean)
	#preclean runs with bind-mounts active
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
