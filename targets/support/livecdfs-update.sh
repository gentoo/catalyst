#!/bin/bash
# Copyright 1999-2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/support/livecdfs-update.sh,v 1.1 2005/04/04 17:48:33 rocket Exp $

/usr/sbin/env-update
source /etc/profile

# allow root logins to the livecd by default
if [ -e /etc/sshd/sshd_config ]
then
	sed -i 's:^#PermitRootLogin\ yes:PermitRootLogin\ yes:' /etc/ssh/sshd_config
fi

# turn off udev tarball
sed -i 's:RC_DEVICE_TARBALL="yes":RC_DEVICE_TARBALL="no":' /etc/conf.d/rc

# turn bashlogin shells to actual login shells
sed -i 's:exec -l /bin/bash:exec -l /bin/bash -l:' /bin/bashlogin

# default programs that we always want to start
rc-update del iptables default
rc-update del netmount default
rc-update add autoconfig default
rc-update del keymaps
rc-update del serial
rc-update del consolefont
rc-update add modules default
rc-update add pwgen default
[ -e /etc/init.d/bootsplash ] && rc-update add bootsplash default
[ -e /etc/init.d/splash ] && rc-update add splash default
[ -e /etc/init.d/sysklogd ] && rc-update add sysklogd default
[ -e /etc/init.d/metalog ] && rc-update add metalog default
[ -e /etc/init.d/syslog-ng ] && rc-update add syslog-ng default
[ -e /etc/init.d/alsasound ] && rc-update add alsasound default
[ -e /etc/init.d/hdparm ] && rc-update add hdparm default

# Comment out current getty settings
sed -i -e '/^c[0-9]/ s/^/#/' /etc/inittab

# Add our own getty settings
for x in 1 2 3 4 5 6
do
	echo "c${x}:12345:respawn:/sbin/agetty -nl /bin/bashlogin 38400 tty${x} linux" >> /etc/inittab
done

# perform any rcadd then any rcdel
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

# clean up the time and set to GMT
rm -rf /etc/localtime
cp /usr/share/zoneinfo/GMT /etc/localtime

# setup the hostname
echo "livecd" > /etc/hostname
echo "gentoo" > /etc/dnsdomainname
#sed -i 's:localhost:livecd.gentoo localhost:' /etc/hosts
echo "127.0.0.1	livecd.gentoo livecd localhost" > /etc/hosts

# setup sudoers
sed -i '/NOPASSWD: ALL/ s/^# //' /etc/sudoers

# setup dhcp on all detected ethernet devices
echo "iface_eth0=\"dhcp\""> /etc/conf.d/net
echo "iface_eth1=\"dhcp\"" >> /etc/conf.d/net
echo "iface_eth2=\"dhcp\"" >> /etc/conf.d/net
echo "iface_eth3=\"dhcp\"" >> /etc/conf.d/net
echo "iface_eth4=\"dhcp\"" >> /etc/conf.d/net

# setup links for ethernet devices
cd /etc/init.d
ln -sf net.eth0 net.eth1
ln -sf net.eth0 net.eth2
ln -sf net.eth0 net.eth3
ln -sf net.eth0 net.eth4

# add this for hwsetup/mkx86config
mkdir -p /etc/sysconfig

# fstab tweaks
echo "tmpfs	/					tmpfs	defaults	0 0" > /etc/fstab
echo "tmpfs	/lib/firmware			tmpfs	defaults	0 0" >> /etc/fstab
# if /usr/lib/X11/xkb/compiled then make it tmpfs
if [ -d /usr/lib/X11/xkb/compiled ]
then
	echo "tmpfs	/usr/lib/X11/xkb/compiled	tmpfs	defaults	0 0" >> /etc/fstab
fi

# devfs tweaks
sed -i '/dev-state/ s:^:#:' /etc/devfsd.conf

# tweak the livecd fstab so that users know not to edit it
# http://bugs.gentoo.org/show_bug.cgi?id=60887
mv /etc/fstab /etc/fstab.old
echo "####################################################" >> /etc/fstab
echo "## ATTENTION: THIS IS THE FSTAB ON THE LIVECD     ##" >> /etc/fstab     
echo "## PLEASE EDIT THE FSTAB at /mnt/gentoo/etc/fstab ##" >> /etc/fstab     
echo "####################################################" >> /etc/fstab
cat /etc/fstab.old >> /etc/fstab
rm /etc/fstab.old

# add some helpful aliases
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

# setup opengl in /etc (if configured)
[ -x /usr/sbin/openglify ] && /usr/sbin/openglify

# touch /etc/asound.state if alsa is configured
[ -d /proc/asound/card0 ] && touch /etc/asound.state

# tweak the motd for gentoo releases 
if [ "${clst_livecd_type}" = "gentoo-release-universal" ]
then
	cat /etc/generic.motd.txt /etc/universal.motd.txt \
		/etc/minimal.motd.txt > /etc/motd
	sed -i 's:^##GREETING:Welcome to the Gentoo Linux Universal Installation CD!:' /etc/motd
fi

if [ "${clst_livecd_type}" = "gentoo-release-minimal" ]
then
	cat /etc/generic.motd.txt /etc/minimal.motd.txt > /etc/motd
	sed -i 's:^##GREETING:Welcome to the Gentoo Linux Minimal Installation CD!:' /etc/motd
fi

if [ "${clst_livecd_type}" = "gentoo-release-environmental" ]
then
	cat /etc/generic.motd.txt /etc/universal.motd.txt \
		/etc/minimal.motd.txt /etc/environmental.motd.txt > /etc/motd
	sed -i 's:^##GREETING:Welcome to the Gentoo Linux LiveCD Environment!:' /etc/motd
fi

if [ "${clst_livecd_type}" = "gentoo-gamecd" ]
then
	cat /etc/generic.motd.txt /etc/gamecd.motd.txt > /etc/motd
	sed -i 's:^##GREETING:Welcome to the Gentoo Linux ##GAME_NAME GameCD!:' /etc/motd
fi

rm -f /etc/generic.motd.txt /etc/universal.motd.txt /etc/minimal.motd.txt /etc/environmental.motd.txt /etc/gamecd.motd.txt

# setup splash/bootsplash (if called for)
if [ "${clst_livecd_splash_type}" == "bootsplash" -a -n "${clst_livecd_splash_theme}" ]
then
	if [ -d /etc/bootsplash/${clst_livecd_splash_theme} ]
	then
		sed -i 's:BOOTSPLASH_THEME=\"gentoo\":BOOTSPLASH_THEME=\"${clst_livecd_splash_theme}\":' /etc/conf.d/bootsplash
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
		sed -i 's:# SPLASH_THEME="gentoo":SPLASH_THEME=\"${clst_livecd_splash_theme}\":' /etc/conf.d/splash
		rm /etc/splash/default
		ln -s /etc/splash/${clst_livecd_splash_theme} /etc/splash/default
	else
		echo "Error, cannot setup splash theme ${clst_livecd_splash_theme}"
		exit 1
	fi
fi

# Create firmware directory if it does not exist
[ ! -d /lib/firmware ] && mkdir -p /lib/firmware

# tar up the firmware so that it does not get clobbered by the livecd mounts
if [ -n "$(ls /lib/firmware)" ]
then
	cd /lib/firmware
	if [ -n "$(ls /usr/lib/hotplug/firmware)" ]
	then
		cp /usr/lib/hotplug/firmware/* /lib/firmware
	fi
	tar cvjpf /lib/firmware.tar.bz2 .
	rm -f /lib/firmware/*
	mkdir -p /usr/lib/hotplug
	ln -sf /lib/firmware /usr/lib/hotplug/firmware
fi
