#!/bin/bash
# Copyright 1999-2005 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2

if [ "${clst_spec_prefix}" == "livecd" ]
then
	# default programs that we always want to start
	rc-update del iptables default
	rc-update del netmount default
	rc-update add autoconfig default
	rc-update del keymaps
	rc-update del serial
	rc-update del consolefont
	rc-update add modules boot
	rc-update add pwgen default
	[ -e /etc/init.d/bootsplash ] && rc-update add bootsplash default
	[ -e /etc/init.d/splash ] && rc-update add splash default
	[ -e /etc/init.d/sysklogd ] && rc-update add sysklogd default
	[ -e /etc/init.d/metalog ] && rc-update add metalog default
	[ -e /etc/init.d/syslog-ng ] && rc-update add syslog-ng default
	[ -e /etc/init.d/alsasound ] && rc-update add alsasound default
	[ -e /etc/init.d/hdparm ] && rc-update add hdparm default

	# Do some livecd_type specific rc-update changes
	case ${clst_livecd_type} in
		gentoo-gamecd )
			rc-update add spind default
			rc-update add x-setup default
			;;
		gentoo-release-livecd )
			rc-update add spind default
			rc-update add x-setup default
			rc-update add xdm default
			;;
		generic-livecd )
			rc-update add spind default
			rc-update add x-setup default
			;;
		*)
			;;
	esac
fi

if [ -n "${clst_livecd_xdm}" ]
then
	rc-update add xdm default
fi

# perform any rcadd then any rcdel
if [ -n "${clst_rcadd}" ] || [ -n "${clst_rcdel}" ]
then
	if [ -n "${clst_rcadd}" ]
	then
	for x in ${clst_rcadd}
	do
		echo "Adding ${x%%|*} to ${x##*|}"
		if [ ! -d /etc/runlevels/${x%%|*} ]
		then
		echo "Runlevel ${x##*|} doesn't exist .... creating it"
		mkdir -p "/etc/runlevels/${x##*|}"
		fi
		rc-update add "${x%%|*}" "${x##*|}"
	done
	fi

	if [ -n "${clst_rcdel}" ]
	then
	for x in ${clst_rcdel}
	do
		rc-update del "${x%%|*}" "${x##*|}"
	done
	for x in $(ls /etc/runlevels)
	do
		CONTENTS=$(find /etc/runlevels/${x} -type f)
		if [ -z "${CONTENTS}" ]
		then
			echo "${x}: Empty runlevel found.... deleting"
		rmdir "/etc/runlevels/${x}"
		fi
	done
			
	fi
fi

