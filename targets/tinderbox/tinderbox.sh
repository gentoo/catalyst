# Copyright 1999-2003 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/tinderbox/Attic/tinderbox.sh,v 1.4 2004/03/26 17:03:29 zhen Exp $

case $1 in
run)
	shift
	export clst_tinderbox_packages="$*"
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
		USE="-gnome -gtk" emerge --oneshot --nodeps distcc || exit 1
		echo "distcc:x:240:2:distccd:/dev/null:/bin/false" >> /etc/passwd
		/usr/bin/distcc-config --install 2>&1 > /dev/null
		/usr/bin/distccd 2>&1 > /dev/null
	fi
	export CONFIG_PROTECT="-*"
	
	USE="build" emerge portage
	#turn off auto-use:
	export USE_ORDER="env:conf:defaults"	
	#back up pristine system
	rsync -avx --exclude "/root/" --exclude "/tmp/" --exclude "/usr/portage/" / /tmp/rsync-bak/ 
	for x in $clst_tinderbox_packages
	do
		emerge --usepkg --buildpkg \$x
		if [ "\$?" != "0" ]
		then
			echo "! \$x" >> /tmp/tinderbox.log	
		else
			echo "\$x" >> /tmp/tinderbox.log
		fi
		echo "Syncing from original pristine tinderbox snapshot..."
		rsync -avx --delete --exclude "/root/*" --exclude "/tmp/" --exclude "/usr/portage/*" /tmp/rsync-bak/ /
	done
EOF
	[ $? -ne 0 ] && exit 1
	;;
*)
	exit 1
	;;
esac
exit 0
