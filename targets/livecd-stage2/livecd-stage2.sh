# Copyright 1999-2003 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/livecd-stage2/Attic/livecd-stage2.sh,v 1.2 2003/12/24 19:28:08 drobbins Exp $

case $1 in
enter)
	$clst_CHROOT $clst_chroot_path
	;;
run)
	shift
	numkernels="$1"
	shift
	count=0
	while [ $count -lt $numkernels ]
	do
		clst_kname="$1"
		shift
		clst_ksource="$1"
		shift
		$clst_CHROOT $clst_chroot_path /bin/bash << EOF
		env-update
		source /etc/profile
		export CONFIG_PROTECT="-*"
		emerge genkernel
		rm -f /usr/src/linux
		export USE="-* build"
		if [ -n "${clst_PKGCACHE}" ]
		then
			emerge --usepkg --buildpkg --noreplace $clst_ksource || exit 1
		else
			emerge --noreplace $clst_ksource || exit 1
		fi
		genkernel --no-bootsplash --kerneldir=/usr/src/linux --kernel-config=/var/tmp/$clst_kname.config --kernelpackage=/var/tmp/$clst_kname.tar.gz all || exit 1
		emerge -C genkernel $clst_ksource
EOF
		[ $? -ne 0 ] && exit 1
		count=$(( $count + 1 ))
	done
	;;
*)
	exit 1
	;;
esac
exit 0
