#!/bin/bash

source /tmp/chroot-functions.sh

if [[ $(readlink /etc/portage/make.profile) == *systemd* ]] ; then

# We are using systemd.

# Types of bootable disk images planned for (diskimage/type):
# cloud-init - an image that starts cloud-init for configuration and then can be
#              used out of the box
# console    - an image that has an empty root password and allows passwordless
#              login on the console only
# ssh        - an image that populates /root/.ssh/authorized_keys and starts dhcp
#              as well as sshd; obviously not fit for public distribution
# generic    - an image with no means of logging in... needs postprocessing
#              no services are started

configure_dhcp() {
	echo "Configuring DHCP on all ethernet devices"
	cat > /etc/systemd/network/default.network <<'END'
[Match]
Name=en*

[Network]
DHCP=yes
END
}

configure_sshd() {
	echo "Configuring sshd"
	mkdir -vp /root/.ssh
	chown root:root /root/.ssh
	echo "${clst_diskimage_sshkey}" > /root/.ssh/authorized_keys
}

echo "Generating /etc/locale.gen"
cat > /etc/locale.gen <<END
# en_US ISO-8859-1
# en_US.UTF-8 UTF-8
C.UTF-8 UTF-8
END

echo "Running systemctl preset-all"
systemctl preset-all || die "Running systemctl preset-all failed"

echo "Setting locale"
echo 'LANG="C.UTF-8"' > /etc/locale.conf || die "Failed to set locale"
env-update || die "Failed to run env-update"

echo "Setting keymap"
echo "KEYMAP=us" > /etc/vconsole.conf || die "Failed to set keymap"

echo "Disk image type is ${clst_diskimage_type}"
case ${clst_diskimage_type} in
	generic)
		echo "Setting up generic image (warning, not very useful on its own)"
		echo "Running systemd-firstboot"
		systemd-firstboot --timezone=UTC || die "Failed running systemd-firstboot"
		;;
	console)
		echo "Setting up console log-in image. Please set the root password ASAP."
		echo "Removing root password"
		passwd -d root || die "Failed removing root password"
		echo "Running systemd-firstboot"
		systemd-firstboot --timezone=UTC || die "Failed running systemd-firstboot"
		configure_dhcp
		;;
	ssh)
		echo "Setting up ssh log-in image, using key ${xxx}"
		echo "Running systemd-firstboot"
		systemd-firstboot --timezone=UTC || die "Failed running systemd-firstboot"
		configure_dhcp
		configure_sshd
		echo "Adding sshd service"
		systemctl enable sshd
	*)
		die "As yet unsupported image type"
		;;
esac

else

# We are using OpenRC.

die "OpenRC is as yet unsupported."

fi

# all done
# (we can't install the boot loader here because nothing is mounted)
