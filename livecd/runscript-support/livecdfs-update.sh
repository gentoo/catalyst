#!/bin/bash
# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/livecd/runscript-support/Attic/livecdfs-update.sh,v 1.4 2004/06/04 14:24:53 zhen Exp $

/usr/sbin/env-update
source /etc/profile

if [ -e /etc/sshd/sshd_config ]
then
	#allow root logins to the livecd by default
	sed -e "s/^#PermitRootLogin\ yes/PermitRootLogin\ yes/" /etc/ssh/sshd_config > /etc/ssh/sshd_config1
	mv /etc/ssh/sshd_config1 /etc/ssh/sshd_config
fi

# fix /etc/issue for mingetty and friends
echo "This is \n.gentoo (\s \m \r) \t" > /etc/issue
		
rc-update del iptables default
rc-update del netmount default
#rc-update add hotplug default
#rc-update add kudzu default
rc-update add autoconfig default
rc-update del keymaps
rc-update del consolefont
rc-update add metalog default
rc-update add modules default
[ -e /etc/init.d/bootsplash ] && rc-update add bootsplash default

rm -rf /etc/localtime
cp /usr/share/zoneinfo/GMT /etc/localtime
echo "livecd" > /etc/hostname

sed -i -e '/\/dev\/[RBS]*/ s/^/#/' /etc/fstab
echo "tmpfs		/	tmpfs	defaults	0 0" >> /etc/fstab
sed -i -e '/dev-state/ s/^/#/' /etc/devfsd.conf

echo "alias cp='cp -i'" >> /etc/profile
echo "alias ls='ls --color'" >> /etc/profile
echo "alias mv='mv -i'" >> /etc/profile
echo "alias pico='nano -w'" >> /etc/profile
echo "alias rm='rm -i'" >> /etc/profile

# make sure we have the latest pci and hotplug ids
if [ -d /usr/share/hwdata ]
then
	rm -f /usr/share/hwdata/pci.ids
	rm -f /usr/share/hwdata/usb.ids
	ln -s /usr/share/misc/pci.ids /usr/share/hwdata/pci.ids
	ln -s /usr/share/misc/usb.ids /usr/share/hwdata/usb.ids
fi

# tweak the motd for gentoo releases 
if [ "${clst_livecd_type}" = "gentoo-release-universal" ]
then
	sed -i -e 's/^##GREETING/Welcome to the Gentoo Linux Universal Installation LiveCD!/' /etc/motd
fi

if [ "${clst_livecd_type}" = "gentoo-release-minimal" ]
then
	sed -i -e 's/^##GREETING/Welcome to the Gentoo Linux Minimal Installation LiveCD!/' /etc/motd
fi

# setup bootsplash (if called for)
if [ -n ${clst_livecd_bootsplash} ]
then
	if [ -d /etc/bootsplash/${clst_livecd_bootsplash} ]
	then
		sed -i 's/BOOTSPLASH_THEME=\"gentoo\"/\"${clst_livecd_bootsplash}\"/' /etc/conf.d/bootsplash
		rm /etc/bootsplash/default
		ln -s /etc/bootsplash/${clst_livecd_bootsplash} /etc/bootsplash/default
	else
		exit 1
	fi
fi
