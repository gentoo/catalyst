#!/bin/bash
		
env-update
source /etc/profile
if [ -n "${clst_ENVSCRIPT}" ]
then
	source /tmp/envscript
	rm -f /tmp/envscript
fi
case $1 in
	build)
		#emerge and enable ccache before we set ROOT
		if [ -n "${clst_CCACHE}" ]
		then
			export FEATURES="ccache"	
			emerge --oneshot --nodeps ccache || exit 1
		fi
		if [ -n "${clst_DISTCC}" ]
                then   
                        export FEATURES="distcc"
                        export DISTCC_HOSTS="${clst_distcc_hosts}"
                        emerge --oneshot --nodeps distcc || exit 1
			echo "distcc:x:240:2:distccd:/dev/null:/bin/false" >> /etc/passwd
                        /usr/bin/distcc-config --install 2>&1 > /dev/null
                        /usr/bin/distccd 2>&1 > /dev/null
                fi
		export ROOT=${2}
		install -d $ROOT
		if [ -n "${clst_PKGCACHE}" ]
		then
			export EMERGE_OPTS="--usepkg --buildpkg"
		fi
		for x in $(/tmp/build.sh)
		do
			echo $x >> /tmp/build.log
			USE="-* build" emerge ${EMERGE_OPTS} --noreplace $x || exit 1
		done
	;;

	preclean)
		#normal chroot is fine here since this is our second chroot (no $clst_CHROOT needed)
		chroot ${2} /bin/bash << EOF
		#now, some finishing touches to initialize gcc-config....
		unset ROOT
		if [ -e /usr/sbin/gcc-config ]
		then
			mythang=\$( cd /etc/env.d/gcc; ls ${clst_CHOST}-* )
			gcc-config \${mythang}; env-update; source /etc/profile
		fi
		#stage1 is not going to have anything in zoneinfo, so save our Factory timezone
		rm -f /etc/localtime
		cp /usr/share/zoneinfo/Factory /etc/localtime
EOF
	;;		
esac
	
