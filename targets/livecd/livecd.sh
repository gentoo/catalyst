# Copyright 1999-2003 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/livecd/Attic/livecd.sh,v 1.1 2003/10/15 05:40:43 zhen Exp $

cp ${SHARE_DIR}/targets/livecd/foundations/${FOUNDATION}/* ${CHROOTDIR}/tmp || die

$CHROOT . /bin/bash << EOF
	env-update
	source /etc/profile
	export CONFIG_PROTECT="-*"
	source /tmp/settings || exit 1
	export USE="\$USE bindist"
	echo "USE is \$USE"
	for x in \$( cat /tmp/base.pkg  | grep -v ^# )
	do
		if [ "\${x:0:1}" = "^" ]
		then
			ACCEPT_KEYWORDS="~${MAINARCH}" emerge -pv --noreplace --buildpkg --usepkg \${x:1} || exit 1
			ACCEPT_KEYWORDS="~${MAINARCH}" emerge --noreplace --buildpkg --usepkg \${x:1} || exit 1
		else
			emerge -pv --noreplace --buildpkg --usepkg \$x || exit 1
			emerge --noreplace --buildpkg --usepkg \$x || exit 1
		fi
	done
	
	cp \$KERNCONFIG /usr/src/linux/.config || exit 1
	cd /usr/src/linux
	#make oldconfig || exit 1
	#make dep || exit 1
	#make -j${jobs} bzImage || exit 1
	#make -j${jobs} modules || exit 1
	#make modules_install || true
	# above, the || true is there to deal with the occasional flaky
	# module.
	for x in \$( cat /tmp/kern.pkg  | grep -v ^# )
	do
		if [ "\${x:0:1}" = "^" ]
		then
			ACCEPT_KEYWORDS="~${MAINARCH}" emerge -pv --noreplace --buildpkg --usepkg \${x:1} || exit 1
			ACCEPT_KEYWORDS="~${MAINARCH}" emerge --noreplace --buildpkg --usepkg \${x:1} || exit 1
		else
			emerge -pv --noreplace --buildpkg --usepkg \$x || exit 1
			emerge --noreplace --buildpkg --usepkg \$x || exit 1
		fi
	done
EOF

[ $? -ne 0 ] && die "LiveCD build failure"

