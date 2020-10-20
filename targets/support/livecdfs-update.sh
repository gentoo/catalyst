#!/bin/bash

RUN_DEFAULT_FUNCS="no"

source /tmp/chroot-functions.sh

# Allow root logins to our CD by default
if [ -e /etc/ssh/sshd_config ]
then
	sed -i 's:^#PermitRootLogin\ yes:PermitRootLogin\ yes:' \
		/etc/ssh/sshd_config
fi

# Clean up the time and set to UTC
rm -rf /etc/localtime
cp /usr/share/zoneinfo/UTC /etc/localtime

# Setup the hostname
echo 'HOSTNAME="livecd"' > /etc/conf.d/hostname
echo "127.0.0.1 livecd.gentoo livecd localhost" > /etc/hosts

# Since we're an official Gentoo release, we do things the official Gentoo way.
# As such, we override livecd/users.
case ${clst_livecd_type} in
	gentoo-release-live*)
		user_comment="Gentoo default user"
		clst_livecd_users="gentoo"
	;;
esac

# Add any users
if [ -n "${clst_livecd_users}" ]
then
	first_user=$(echo ${clst_livecd_users} | cut -d' ' -f1)
	default_comment="Default LiveCD User"
	[ -z "${user_comment}" ] && user_comment=${default_comment}

	if [ "$(getent group games | cut -d: -f1)" != "games" ]
	then
		echo "Adding games group"
		groupadd -g 35 games
	fi
	if [ "$(getent group plugdev | cut -d: -f1)" != "plugdev" ]
	then
		echo "Adding plugdev group"
		groupadd plugdev
	fi
	for x in ${clst_livecd_users}
	do
		useradd -G users,wheel,audio,plugdev,games,cdrom,disk,floppy,usb \
			-g 100 -c "${user_comment}" -m ${x}
		chown -R ${x}:users /home/${x}
		if [ -n "${clst_livecd_xdm}" -a -n "${clst_livecd_xsession}" ]
		then
			echo "[Desktop]" > /home/${x}/.dmrc
			echo "Session=${clst_livecd_xsession}" >> /home/${x}/.dmrc
			chown -R ${x}:users /home/${x}
		fi
	done
fi

# Setup sudoers
if [ -f /etc/sudoers ]
then
	sed -i '/NOPASSWD: ALL/ s/^# //' /etc/sudoers
fi

# Setup links for ethernet devices
cd /etc/init.d
for i in {1..4}; do
	ln -sf net.lo net.eth${i}
done

# Add this for hwsetup/mkx86config
mkdir -p /etc/sysconfig

cat <<EOF > /etc/fstab
####################################################
## ATTENTION: THIS IS THE FSTAB ON THE LIVECD     ##
## PLEASE EDIT THE FSTAB at /mnt/gentoo/etc/fstab ##
####################################################

# fstab tweaks
tmpfs	/					tmpfs	defaults	0 0
EOF

mv ${clst_make_conf} ${clst_make_conf}.old
cat <<EOF > ${clst_make_conf}
####################################################
## ATTENTION: THIS IS THE MAKE.CONF ON THE LIVECD ##
## PLEASE EDIT /mnt/gentoo${clst_make_conf} INSTEAD  ##
####################################################
EOF
cat ${clst_make_conf}.old >> ${clst_make_conf}

# devfs tweaks
[ -e /etc/devfsd.conf ] && sed -i '/dev-state/ s:^:#:' /etc/devfsd.conf

# Add some helpful aliases
cat <<EOF >> /etc/profile
alias cp='cp -i'
alias mv='mv -i'
alias rm='rm -i'
alias ls='ls --color=auto'
alias ll='ls -l'
alias grep='grep --color=auto'
EOF

# Make sure we have the latest pci,usb and hotplug ids.  Older versions of
# pciutils and usbutils used /sbin, where newer versions use /usr/sbin.
[ -x /sbin/update-pciids ] && /sbin/update-pciids
[ -x /sbin/update-usbids ] && /sbin/update-usbids
[ -x /usr/sbin/update-pciids ] && /usr/sbin/update-pciids
[ -x /usr/sbin/update-usbids ] && /usr/sbin/update-usbids
if [ -d /usr/share/hwdata ]
then
	# If we have uncompressed pci and usb ids files, symlink them.
	[ -f /usr/share/misc/pci.ids ] && [ -f /usr/share/hwdata/pci.ids ] && \
		rm -f /usr/share/hwdata/pci.ids && ln -s /usr/share/misc/pci.ids \
		/usr/share/hwdata/pci.ids
	[ -f /usr/share/misc/usb.ids ] && [ -f /usr/share/hwdata/usb.ids ] && \
		rm -f /usr/share/hwdata/usb.ids && ln -s /usr/share/misc/usb.ids \
		/usr/share/hwdata/usb.ids
	# If we have compressed pci and usb files, we download our own copies.
	[ -f /usr/share/misc/pci.ids.gz ] && [ -f /usr/share/hwdata/pci.ids ] && \
		rm -f /usr/share/hwdata/pci.ids && wget -O /usr/share/hwdata/pci.ids \
		http://pciids.sourceforge.net/v2.2/pci.ids
	[ -f /usr/share/misc/usb.ids.gz ] && [ -f /usr/share/hwdata/usb.ids ] && \
		rm -f /usr/share/hwdata/usb.ids && wget -O /usr/share/hwdata/usb.ids \
		http://www.linux-usb.org/usb.ids
fi

# Setup opengl in /etc (if configured)
[ -x /usr/sbin/openglify ] && /usr/sbin/openglify

# Setup configured display manager
if [ -n "${clst_livecd_xdm}" ]
then
	sed -i \
		-e "s:^#\\?DISPLAYMANAGER=.\+$:DISPLAYMANAGER=\"${clst_livecd_xdm}\":" \
		/etc/rc.conf
	sed -i \
		-e "s:^#\\?DISPLAYMANAGER=.\+$:DISPLAYMANAGER=\"${clst_livecd_xdm}\":" \
		/etc/conf.d/xdm
fi

# Setup configured default X Session
if [ -n "${clst_livecd_xsession}" ]
then
	echo "XSESSION=\"${clst_livecd_xsession}\"" > /etc/env.d/90xsession
fi

# touch /etc/asound.state
touch /etc/asound.state

# Tweak the MOTD for Gentoo releases
case ${clst_livecd_type} in
	gentoo-release-universal)
		cat /etc/generic.motd.txt /etc/universal.motd.txt \
			/etc/minimal.motd.txt > /etc/motd
		sed -i 's:^##GREETING:Welcome to the Gentoo Linux Universal Installation CD!:' /etc/motd
	;;
	gentoo-release-minimal)
		cat /etc/generic.motd.txt /etc/minimal.motd.txt > /etc/motd
		sed -i 's:^##GREETING:Welcome to the Gentoo Linux Minimal Installation CD!:' /etc/motd
	;;
	gentoo-release-live*)
		cat /etc/generic.motd.txt \
			/etc/minimal.motd.txt /etc/livecd.motd.txt > /etc/motd
		sed -i -e 's:^##GREETING:Welcome to the Gentoo Linux LiveCD!:' \
			-e "s:##DISPLAY_MANAGER:${clst_livecd_xdm}:" /etc/motd
	;;
esac

rm -f /etc/generic.motd.txt /etc/universal.motd.txt /etc/minimal.motd.txt /etc/livecd.motd.txt

# Post configuration
case ${clst_livecd_type} in
	gentoo-release-live*)
		# Setup Gnome theme
		if [ "${clst_livecd_xsession}" == "gnome" ]
		then
			gconftool-2 --direct \
				--config-source xml:readwrite:/etc/gconf/gconf.xml.defaults \
				--type string --set /desktop/gnome/interface/font_name "Sans 9"
		fi

		# Remove locking on screensaver
		gconftool-2 --direct \
			--config-source=xml:readwrite:/etc/gconf/gconf.xml.defaults -s \
			-t bool /apps/gnome-screensaver/lock_enabled false >/dev/null

		# Setup GDM
		if [ "${clst_livecd_xdm}" == "gdm" ]
		then
			if [ ! -e /etc/X11/gdm/gdm.conf ] && [ -e /usr/share/gdm/defaults.conf ]
			then
				if [ -n "${clst_livecd_users}" ] && [ -n "${first_user}" ]
				then
					sedxtra="\nTimedLogin=${first_user}"
				else
					sedxtra=""
				fi

				cp -f /etc/X11/gdm/custom.conf /etc/X11/gdm/custom.conf.old

				sed	-i \
					-e "s:\(\[daemon\]\)$:\1\nTimedLoginEnable=true\nTimedLoginDelay=10${sedxtra}:" \
					-e 's:\(\[greeter\]\)$:\1\nGraphicalTheme=gentoo-emergence:' \
					/etc/X11/gdm/custom.conf
			else
				cp -f /etc/X11/gdm/gdm.conf /etc/X11/gdm/gdm.conf.old
				sed -i \
					-e 's:TimedLoginEnable=false:TimedLoginEnable=true:' \
					-e 's:TimedLoginDelay=30:TimedLoginDelay=10:' \
					-e 's:AllowRemoteRoot=true:AllowRemoteRoot=false:' \
					-e ':^#GraphicalTheme=: s:^#::' \
					-e 's:^GraphicalTheme=.*$:GraphicalTheme=gentoo-emergence:' \
					/etc/X11/gdm/gdm.conf

				if [ -n "${clst_livecd_users}" ] && [ -n "${first_user}" ]
				then
					sed -i \
						-e "s:TimedLogin=:TimedLogin=${first_user}:" \
						/etc/X11/gdm/gdm.conf
				fi
			fi
		fi

		# This gives us our list of system packages for the installer
		mkdir -p /usr/livecd
		### XXX: Andrew says we don't need this anymore
		USE="-* $(cat /var/db/pkg/sys-libs/glibc*/USE)" emerge -eqp @system | grep -e '^\[ebuild' | sed -e 's:^\[ebuild .\+\] ::' -e 's: .\+$::' > /usr/livecd/systempkgs.txt

		# This is my hack to reduce tmpfs usage
		cp -r ${clst_repo_basedir}/${clst_repo_name}/{profiles,eclass} /usr/livecd
		rm -rf /usr/livecd/profiles/{co*,default-{1*,a*,b*,d*,h*,i*,m*,p*,s*,x*},g*,hardened-*,n*,x*}
		mv -f /etc/gconf /usr/livecd
		ln -sf /usr/livecd/gconf /etc/gconf
		mv -f /var/db /usr/livecd
		ln -sf /usr/livecd/db /var/db

		# Clear out lastlog
		rm -f /var/log/lastlog && touch /var/log/lastlog

		create_handbook_icon() {
			cat <<-EOF > /usr/share/applications/gentoo-handbook.desktop
				[Desktop Entry]
				Encoding=UTF-8
				Version=1.0
				Type=Link
				URL=file:///mnt/cdrom/docs/handbook/html/index.html
				Terminal=false
				Name=Gentoo Linux Handbook
				GenericName=Gentoo Linux Handbook
				Comment=This is a link to the local copy of the Gentoo Linux Handbook.
				Icon=text-editor
			EOF
		}

		# Create our Handbook icon
		[ -e /docs/handbook/index.html ] && create_handbook_icon
		[ -n "${clst_livecd_overlay}" ] && [ -e ${clst_livecd_overlay}/docs/handbook/index.html ] && create_handbook_icon

		# Copy our icons into place and build home directories
		if [ -n "${clst_livecd_users}" ]
		then
			for username in ${clst_livecd_users}
			do
				mkdir -p /home/${username}/Desktop
				# Copy our Handbook icon
				[ -e /usr/share/applications/gentoo-handbook.desktop ] && \
					cp -f /usr/share/applications/gentoo-handbook.desktop \
					/home/${username}/Desktop
				# Copy our installer icons
				if [ -e /usr/share/applications/installer-gtk.desktop ]
				then
					cp -f /usr/share/applications/installer-{gtk,dialog}.desktop /home/${username}/Desktop
					sed -i -e \
						's:Exec=installer-dialog:Exec=sudo installer-dialog:' \
						/home/${username}/Desktop/installer-dialog.desktop
					sed -i -e 's:Exec=installer-gtk:Exec=installer:' \
						/home/${username}/Desktop/installer-gtk.desktop
				fi
				chown -R ${username}:100 /home/${username}
			done
		fi
		;;
	generic-livecd )
		# This is my hack to reduce tmpfs usage
		mkdir -p /usr/livecd

		if [ -d /etc/gconf ]
		then
			mv -f /etc/gconf /usr/livecd
			ln -sf /usr/livecd/gconf /etc/gconf
		fi

		touch /etc/startx
		;;
esac

# We want the first user to be used when auto-starting X
if [ -e /etc/startx ]
then
	sed -i "s:##STARTX:echo startx | su - '${first_user}':" /root/.bashrc
fi

if [ -e /lib/rcscripts/addons/udev-start.sh ]
then
	sed -i "s:\t\[\[ -x /sbin/evms_activate:\t\[\[ -x \${CDBOOT} \]\] \&\& \[\[ -x /sbin/evms_activate:" /lib/rcscripts/addons/udev-start.sh
fi

env-update
