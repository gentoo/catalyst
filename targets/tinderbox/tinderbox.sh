# Copyright 1999-2003 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/tinderbox/Attic/tinderbox.sh,v 1.1 2003/11/30 01:51:44 drobbins Exp $

case $1 in
run)
	shift
	export clst_tinderbox_packages="$*"
	$clst_CHROOT $clst_chroot_path /bin/bash << EOF
	env-update
	source /etc/profile
	if [ -n "${clst_CCACHE}" ]
	then
		export FEATURES="ccache"
		emerge --oneshot --nodeps ccache || exit 1
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
			echo "$x" >> /tmp/tinderbox.log
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
