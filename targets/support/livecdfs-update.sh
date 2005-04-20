#!/bin/bash
# Copyright 1999-2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/support/livecdfs-update.sh,v 1.8 2005/04/20 19:48:29 wolf31o2 Exp $

/usr/sbin/env-update
source /etc/profile

# allow root logins to the livecd by default
if [ -e /etc/sshd/sshd_config ]
then
	sed -i 's:^#PermitRootLogin\ yes:PermitRootLogin\ yes:' /etc/ssh/sshd_config
fi

# turn off udev tarball
sed -i 's:RC_DEVICE_TARBALL="yes":RC_DEVICE_TARBALL="no":' /etc/conf.d/rc

# Comment out current getty settings
sed -i -e '/^c[0-9]/ s/^/#/' /etc/inittab

# Add our own getty settings
for x in 1 2 3 4 5 6
do
	echo "c${x}:12345:respawn:/sbin/agetty -nl /bin/bashlogin 38400 tty${x} linux" >> /etc/inittab
done

# Do some livecd_type specific inittab changes
case ${clst_livecd_type} in
	gnap)
		sed -i "s/^#c1:/c1:/" /etc/inittab
		sed -i "/^.*bashlogin.*$/ d" /etc/inittab
	;;
esac

# clean up the time and set to UTC
rm -rf /etc/localtime
cp /usr/share/zoneinfo/UTC /etc/localtime

# setup the hostname
case ${clst_livecd_type} in
	gnap)
		echo "gentoo" > /etc/dnsdomainname
		echo "127.0.0.1	livecd.gentoo livecd localhost" > /etc/hosts
		;;
	gentoo-gamecd)
		echo "gamecd" > /etc/hostname
		echo "gentoo" > /etc/dnsdomainname
		echo "127.0.0.1 gamecd.gentoo gamecd localhost" > /etc/hosts
		;;
	gentoo-*)
		echo "livecd" > /etc/hostname
		echo "gentoo" > /etc/dnsdomainname
		echo "127.0.0.1	livecd.gentoo livecd localhost" > /etc/hosts
		;;
esac

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
#[ -x /usr/sbin/openglify ] && /usr/sbin/openglify
mkdir -p /etc/opengl

# touch /etc/asound.state
touch /etc/asound.state

# tweak the motd for gentoo releases 
case ${clst_livecd_type} in
	gentoo-release-universal )
		cat /etc/generic.motd.txt /etc/universal.motd.txt \
			/etc/minimal.motd.txt > /etc/motd
		sed -i 's:^##GREETING:Welcome to the Gentoo Linux Universal Installation CD!:' /etc/motd
	;;
	gentoo-release-minimal )
		cat /etc/generic.motd.txt /etc/minimal.motd.txt > /etc/motd
		sed -i 's:^##GREETING:Welcome to the Gentoo Linux Minimal Installation CD!:' /etc/motd
	;;
	gentoo-release-livecd )
		cat /etc/generic.motd.txt /etc/universal.motd.txt \
			/etc/minimal.motd.txt /etc/livecd.motd.txt > /etc/motd
		sed -i 's:^##GREETING:Welcome to the Gentoo Linux LiveCD!:' /etc/motd
	;;
	gentoo-gamecd )
		cat /etc/generic.motd.txt /etc/gamecd.motd.txt > /etc/motd
		sed -i 's:^##GREETING:Welcome to the Gentoo Linux ##GAME_NAME GameCD!:' /etc/motd
	;;
esac

rm -f /etc/generic.motd.txt /etc/universal.motd.txt /etc/minimal.motd.txt /etc/livecd.motd.txt /etc/gamecd.motd.txt

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
	rm -rf /usr/lib/hotplug/firmware
	ln -sf /lib/firmware /usr/lib/hotplug/firmware
fi

# Post configuration
case ${clst_livecd_type} in
	gentoo-gamecd )
		# we grab our configuration
		if [ -e /tmp/gamecd.conf ]
		then

		    source /tmp/gamecd.conf || exit 1
		    rm /tmp/gamecd.conf

		    # here we replace out game information into several files
		    sed -i -e "s:##GAME_NAME:${GAME_NAME}:" /etc/motd

		    # here we setup our xinitrc
		    echo "exec ${GAME_EXECUTABLE}" > /etc/X11/xinit/xinitrc
		fi

		touch /etc/startx
	;;
	generic-livecd )
		touch /etc/startx
	;;
esac

