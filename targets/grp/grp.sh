# Copyright 1999-2003 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/grp/Attic/grp.sh,v 1.9 2004/02/23 17:53:18 drobbins Exp $

case $1 in
enter)
	$clst_CHROOT $clst_chroot_path
	;;
run)
	shift
	export clst_grp_type=$1
	shift
	export clst_grp_target=$1
	shift
	export clst_grp_packages="$*"
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
                echo "distcc:x:240:2:distccd:/dev/null:/bin/false" >> /etc/passwd
                /usr/bin/distcc-config --install 2>&1 > /dev/null
                /usr/bin/distccd 2>&1 > /dev/null
    fi
	if [ ${clst_rel_type} = "hardened" ]
	then
		emerge --oneshot --nodeps hardened-gcc || exit 1
	fi
	export CONFIG_PROTECT="-*"
	
	USE="build" emerge portage
	#turn off auto-use:
	export USE_ORDER="env:conf:defaults"	
	if [ "$clst_grp_type" = "pkgset" ]
	then
		unset DISTDIR
		export PKGDIR="/tmp/grp/$clst_grp_target"
		emerge --usepkg --buildpkg --noreplace $clst_grp_packages || exit 1
	else
		unset DISTDIR
		#don't grab MS core fonts, etc.
		export USE="\$USE bindist"
		#first grab to the normal distdir
		emerge --fetchonly $clst_grp_packages || exit 1
		export DISTDIR="/tmp/grp/$clst_grp_target"
		export OLD_MIRRORS="\$GENTOO_MIRRORS"
		export GENTOO_MIRRORS="/usr/portage/distfiles"
		#now grab them again, but with /usr/portage/distfiles as the primary mirror (local grab)
		emerge --fetchonly $clst_grp_packages || exit 1
		#restore original GENTOO_MIRRORS setting, if any
		export GENTOO_MIRRORS="\$OLD_MIRRORS"
		unset PKGDIR
	fi
EOF
	[ $? -ne 0 ] && exit 1
	;;
*)
	exit 1
	;;
esac
exit 0
