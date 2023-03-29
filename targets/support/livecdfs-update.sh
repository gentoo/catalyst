#!/bin/bash

RUN_DEFAULT_FUNCS="no"

source /tmp/chroot-functions.sh

# Allow root logins to our CD by default
if [ -e /etc/ssh/sshd_config ]
then
	sed -i \
		-e '/^#PermitRootLogin/c# Allow root login with password on livecds.\nPermitRootLogin Yes' \
		/etc/ssh/sshd_config
fi

# Clean up the time and set to UTC
rm -rf /etc/localtime
cp /usr/share/zoneinfo/UTC /etc/localtime

# Setup the hostname
echo 'hostname="livecd"' > /etc/conf.d/hostname
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

# Tweak the MOTD for Gentoo releases
case ${clst_livecd_type} in
	gentoo-release-universal)
		cat /etc/generic.motd.txt /etc/universal.motd.txt > /etc/motd
		sed -i 's:^##GREETING:Welcome to the Gentoo Linux Universal Installation CD!:' /etc/motd
	;;
	gentoo-release-minimal)
		cat /etc/generic.motd.txt /etc/minimal.motd.txt > /etc/motd
		sed -i 's:^##GREETING:Welcome to the Gentoo Linux Minimal Installation CD!:' /etc/motd
	;;
	gentoo-release-live*)
		cat /etc/generic.motd.txt /etc/livecd.motd.txt > /etc/motd
		sed -i -e 's:^##GREETING:Welcome to the Gentoo Linux LiveCD!:' /etc/motd
	;;
esac

rm -f /etc/generic.motd.txt /etc/universal.motd.txt /etc/minimal.motd.txt /etc/livecd.motd.txt

# Post configuration
case ${clst_livecd_type} in
	gentoo-release-live*)
		# This is my hack to reduce tmpfs usage
		mkdir -p /usr/livecd
		cp -r ${clst_repo_basedir}/${clst_repo_name}/{profiles,eclass} /usr/livecd
		rm -rf /usr/livecd/profiles/{co*,default-{1*,a*,b*,d*,h*,i*,m*,p*,s*,x*},g*,hardened-*,n*,x*}
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
				chown -R ${username}:100 /home/${username}
			done
		fi
		;;
	generic-livecd )
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
