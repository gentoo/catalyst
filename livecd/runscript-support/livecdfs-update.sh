#!/bin/bash
# Copyright 1999-2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/livecd/runscript-support/Attic/livecdfs-update.sh,v 1.22 2004/12/08 19:47:55 wolf31o2 Exp $

/usr/sbin/env-update
source /etc/profile

if [ -e /etc/sshd/sshd_config ]
then
	#allow root logins to the livecd by default
	sed -i "s/^#PermitRootLogin\ yes/PermitRootLogin\ yes/" /etc/ssh/sshd_config
fi

sed -i 's/RC_DEVICE_TARBALL="yes"/RC_DEVICE_TARBALL="no"/' /etc/conf.d/rc

# fix /etc/issue for mingetty and friends
echo "This is \n.gentoo (\s \m \r) \t" > /etc/issue

# default programs that we always want to start
rc-update del iptables default
rc-update del netmount default
# rc-update add hotplug default
# rc-update add kudzu default
rc-update add autoconfig default
rc-update del keymaps
rc-update del consolefont
rc-update add metalog default
rc-update add modules default
rc-update add pwgen default
[ -e /etc/init.d/bootsplash ] && rc-update add bootsplash default
[ -e /etc/init.d/splash ] && rc-update add splash default

# switch the order of rcadd/ rcdel
if [ -n "${clst_livecd_rcadd}" ] || [ -n "${clst_livecd_rcdel}" ]
then
	if [ -n "${clst_livecd_rcadd}" ]
	then
		for x in ${clst_livecd_rcadd}
		do
			rc-update add "${x%%:*}" "${x##*:}"
		done
	fi
	
	if [ -n "${clst_livecd_rcdel}" ]
	then
		for x in ${clst_livecd_rcdel}
		do
			rc-update del "${x%%:*}" "${x##*:}"
		done
	fi
fi
	
rm -rf /etc/localtime
cp /usr/share/zoneinfo/GMT /etc/localtime
echo "livecd" > /etc/hostname
echo "gentoo" > /etc/dnsdomainname
sed -i -e "s:localhost:livecd.gentoo localhost:" /etc/hosts

# gpm fixes
[ -e /etc/conf.d/gpm ] && sed -i -e 's/#MOUSE=imps2/MOUSE=imps2/' \
	-e 's:#MOUSEDEV=/dev/input/mice:MOUSEDEV=/dev/input/mice:' \
	/etc/conf.d/gpm

# fstab tweaks
#sed -i -e '/\/dev\/[RBS]*/ s/^/#/' /etc/fstab
echo "tmpfs		/				tmpfs	defaults	0 0" > /etc/fstab
echo "tmpfs		/usr/lib/hotplug/firmware	tmpfs	defaults	0 0" >> /etc/fstab
sed -i -e '/dev-state/ s/^/#/' /etc/devfsd.conf

# tweak the livecd fstab so that users know not to edit it
# http://bugs.gentoo.org/show_bug.cgi?id=60887
mv /etc/fstab /etc/fstab.old
echo "####################################################" >> /etc/fstab
echo "## ATTENTION: THIS IS THE FSTAB ON THE LIVECD     ##" >> /etc/fstab     
echo "## PLEASE EDIT THE FSTAB at /mnt/gentoo/etc/fstab ##" >> /etc/fstab     
echo "####################################################" >> /etc/fstab
cat /etc/fstab.old >> /etc/fstab
rm /etc/fstab.old

echo "alias cp='cp -i'" >> /etc/profile
echo "alias mv='mv -i'" >> /etc/profile
echo "alias rm='rm -i'" >> /etc/profile
echo "alias ls='ls --color=auto'" >> /etc/profile
echo "alias grep='grep --color=auto'" >> /etc/profile

# make sure we have the latest pci and hotplug ids
if [ -d /usr/share/hwdata ]
then
	[ -f /usr/share/hwdata/pci.ids ] && rm -f /usr/share/hwdata/pci.ids
	[ -f /usr/share/hwdata/usb.ids ] && rm -f /usr/share/hwdata/usb.ids
	ln -s /usr/share/misc/pci.ids /usr/share/hwdata/pci.ids
	ln -s /usr/share/misc/usb.ids /usr/share/hwdata/usb.ids
fi

# tweak the motd for gentoo releases 
if [ "${clst_livecd_type}" = "gentoo-release-universal" ]
then
	cat /etc/generic.motd.txt /etc/universal.motd.txt \
		/etc/minimal.motd.txt > /etc/motd
	sed -i -e 's/^##GREETING/Welcome to the Gentoo Linux Universal Installation LiveCD!/' /etc/motd
fi

if [ "${clst_livecd_type}" = "gentoo-release-minimal" ]
then
	cat /etc/generic.motd.txt > /etc/motd
	sed -i -e 's/^##GREETING/Welcome to the Gentoo Linux Minimal Installation LiveCD!/' /etc/motd
fi

if [ "${clst_livecd_type}" = "gentoo-gamecd" ]
then
	cat /etc/generic.motd.txt /etc/gamecd.motd.txt > /etc/motd
	sed -i -e 's/^##GREETING/Welcome to the Gentoo Linux ##GAME_NAME GameCD!/' /etc/motd
fi

rm -f /etc/generic.motd.txt /etc/universal.motd.txt /etc/minimal.motd.txt /etc/gamecd.motd.txt

# setup splash/bootsplash (if called for)
if [ "${clst_livecd_splash_type}" == "bootsplash" -a -n "${clst_livecd_splash_theme}" ]
then
	if [ -d /etc/bootsplash/${clst_livecd_splash_theme} ]
	then
		sed -i 's/BOOTSPLASH_THEME=\"gentoo\"/BOOTSPLASH_THEME=\"${clst_livecd_splash_theme}\"/' /etc/conf.d/bootsplash
		rm /etc/bootsplash/default
		ln -s "/etc/bootsplash/${clst_livecd_splash_theme}" /etc/bootsplash/default
	else
		echo "Error, cannot setup bootsplash theme ${clst_livecd_splash_theme}"
		exit 1
	fi

elif [ "${clst_livecd_splash_type}" == "gensplash" -a -n "${clst_livecd_splash_theme}" ]
then
	if [ -d /etc/splash/${clst_livecd_splash_theme} ]
	then
		sed -i 's/# SPLASH_THEME="gentoo"/SPLASH_THEME=\"${clst_livecd_splash_theme}\"/' /etc/conf.d/splash
		rm /etc/splash/default
		ln -s /etc/splash/${clst_livecd_splash_theme} /etc/splash/default
	else
		echo "Error, cannot setup splash theme ${clst_livecd_splash_theme}"
		exit 1
	fi
fi

# tar up the firmware so that it does not get clobbered by the livecd mounts
[ -n "$(ls /usr/lib/hotplug/firmware)" ] && tar cvjpf /usr/lib/hotplug/firmware.tar.bz2 /usr/lib/hotplug/firmware/* && rm -f /usr/lib/hotplug/firmware/*
ln -sf /lib/firmware /usr/lib/hotplug/firmware
