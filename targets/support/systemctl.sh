#!/bin/bash

# This script only runs when livecd/systemd: yes is set in the spec

# Configure autologin on tty1 for systemd live media
mkdir -p /etc/systemd/system/getty@tty1.service.d
cat > /etc/systemd/system/getty@tty1.service.d/autologin.conf <<EOF
[Service]
ExecStart=
ExecStart=-/sbin/agetty --autologin root --noclear %I \$TERM
EOF
systemctl enable getty@tty1.service

# This section is controlled by the user in the specfile via:
#   livecd/rcadd: NetworkManager
#   livecd/rcdel: gpm

if [ -n "${clst_rcadd}" ]
then
	for svc in ${clst_rcadd}
	do
		echo "Enabling service: ${svc}"
		systemctl enable "${svc}"
	done
fi

if [ -n "${clst_rcdel}" ]
then
	for svc in ${clst_rcdel}
	do
		echo "Disabling service: ${svc}"
		systemctl disable "${svc}"
	done
fi
