#!/bin/bash

if portageq has_version / '>=sys-apps/baselayout-2'
then
	# We need to add a few here for baselayout-2
	[[ -e /etc/init.d/device-mapper ]] && rc-update add device-mapper boot
	[[ -e /etc/init.d/lvm ]] && rc-update add lvm boot
	[[ -e /etc/init.d/dmcrypt ]] && rc-update add dmcrypt boot
	[[ -e /etc/init.d/mdraid ]] && rc-update add mdraid boot
fi

if [ "${clst_spec_prefix}" == "livecd" ]
then
	# default programs that we always want to start
	rc-update del iptables
	rc-update del netmount
	rc-update del keymaps
	rc-update del serial
	rc-update del consolefont
	# We need to add this one, unconditionally
	rc-update add autoconfig default
	[[ -e /etc/init.d/splash ]] && rc-update add splash default
	[[ -e /etc/init.d/fbcondecor ]] && rc-update add fbcondecor default
	[[ -e /etc/init.d/sysklogd ]] && rc-update add sysklogd default
	[[ -e /etc/init.d/metalog ]] && rc-update add metalog default
	[[ -e /etc/init.d/syslog-ng ]] && rc-update add syslog-ng default

	# Do some livecd_type specific rc-update changes
	case ${clst_livecd_type} in
		gentoo-gamecd)
			rc-update add spind default
			;;
		gentoo-release-live*)
			rc-update add spind default
			rc-update add xdm default
			;;
		generic-livecd)
			rc-update add spind default
			;;
	esac
fi

# Perform any rcadd then any rcdel
if [ -n "${clst_rcadd}" ] || [ -n "${clst_rcdel}" ]
then
	if [ -n "${clst_rcadd}" ]
	then
		for x in ${clst_rcadd}
		do
			echo "Adding ${x%%|*} to ${x##*|}"
			if [ ! -d /etc/runlevels/${x##*|} ]
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
	fi
fi

