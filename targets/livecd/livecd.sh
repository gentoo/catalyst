#!/bin/bash  
# Copyright 1999-2003 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/livecd/Attic/livecd.sh,v 1.4 2003/11/11 15:01:12 zhen Exp $

# Original work done by livewire@gentoo.org and drobbins@gentoo.org
# Adapted to a catalyst plugin by zhen@gentoo.org

# we need a specfile setup for this!!! there are a ton of options that need set.

#############################################################################################
# Variables needed for livecd creation - make sure these get defined in the spec file		#
# Var					Use										Catalyst Define					#
#############################################################################################
# LIVECD_ROOT			build directory root					clst_livecd_root
# CD_PROFILE			build profile (portage profile)			clst_cd_profile (rel_type?)
# CD_STAGEFILE			stage3 used for building				-
# LOOP_ROOT				loop location (doesn't cloop do this?)	-
# ISO_ROOT				iso (build?) location					-
# LOOP_FILE				?										-
# CLOOP_FILE			cloop defs?								-
# STOREDIR				temp dir for building					clst_storedir	

# ok, now for mounting - all of this should be handled by catalyst itself.
# catalyst_util.py should handle all of the code - rel_type just needs to be set to livecd.

#####################################################################################
umount_all() {
	local x
	for x in /usr/portage /proc /home/distfiles /dev /tmp/livecd -initrd 
	do
	umount ${CHROOT_PATH}${x} 2>/dev/null || true
	done
	umount ${LOOP_ROOT} 2>/dev/null || true
	echo "Bind mounts should all be unmounted now."
}

mount_all() {
	mount -o bind /dev $CHROOT_PATH/dev || chroot_die
	mount -o bind /proc $CHROOT_PATH/proc || chroot_die
	mkdir -p $CHROOT_PATH/usr/portage
	mount -o bind $CD_PORTDIR $CHROOT_PATH/usr/portage || chroot_die
	[ ! -e $CHROOT_PATH/tmp/livecd ] && install -d $CD_BUILDCHROOT/tmp/livecd
	mount -o bind $STOREDIR $CHROOT_PATH/tmp/livecd || chroot_die
	mount -o bind $CD_DISTDIR $CHROOT_PATH/home/distfiles || chroot_die
}
#####################################################################################

build_setup() {
	cat > $STOREDIR/build-setup << EOF
#env-update is important for gcc-3.2.1-r6 and higher.
env-update
source /etc/profile
export DISTDIR=/home/distfiles
export CONFIG_PROTECT='-*'
#lilo appears to need to write to /etc do do awking
export FEATURES="-sandbox ccache distcc"
export PATH="/usr/bin/ccache:/usr/lib/distcc/bin:\${PATH}"
export CFLAGS="$CD_CFLAGS"
export CXXFLAGS="$CD_CFLAGS"
export USE="$CD_USE"
export PKGDIR=/tmp/livecd/packages
export CLEAN_DELAY=0
[ ! -e /tmp/log ] && install -d /tmp/log

ewrapper() {
	local opts
	local pkgs
	for x in \$*
	do
		if [ "\${x:0:1}" = "-" ]
		then
			opts="\$opts \$x"
		else
			pkgs="\$pkgs \$x"
		fi
	done
	for x in \$pkgs
	do
		echo ">>> Emerging \${x}..."
#once the --buildpkg bug is fixed, we may have to --buildpkg --usepkg
		emerge --buildpkg \$opts \$x 2>&1 | cat >> /tmp/log/emerge.log 
		if [ \$? -ne 0 ]
		then
			echo ">>> Error emerging \${x}."
			exit 1
		fi
	done
}

cwrapper() {
	echo ">>> Executing \${*}..."
	\${*} 2>&1 | cat >> /tmp/log/build.log
	if [ \$? -ne 0 ]
	then
		echo ">>> Error executing \${*}."
		exit 1
	fi
}
EOF
	}


#####################################################################################
#####################################################################################
# END COMMENTS

#"zapmost" is used to remove an entire directory tree, *except* for certain
#specified files. Arg 1 is the tree, args 2+ are the items to keep, which can
#be files or directories at the root or deeper levels.

#example calls:
#zapmost /usr/share/locales en_us
#zapmost /usr/share/terminfo l/linux

zapmost() {
	local rootdir
	rootdir="${CHROOT_PATH}${1}/"
	[ ! -e  "$rootdir" ] && echo "zapmost: $rootdir not found; skipping..." && return 1
	install -d ${STOREDIR}/zap
	local dirs
	shift
	local x
	for x in ${*}
	do
		if [ "${x##*/}" = "${x}" ]
		then
			#one deep
			mv ${rootdir}${x} ${STOREDIR}/zap
		else
			#more than one deep; create intermediate directories
			dirs=${x%/*}
			install -d ${STOREDIR}/zap/${dirs}
			mv ${rootdir}${x} ${STOREDIR}/zap/${x}
		fi
	done
	rm -rf ${rootdir}*
	mv ${STOREDIR}/zap/* ${rootdir}
}

#clean up if we are interrupted:
trap "chroot_die" SIGINT SIGQUIT

base_build() {
	cp "${LIVECD_ROOT}/profiles/${CD_PROFILE}/aux-files/freeramdisk.c" $STOREDIR || chroot_die
	cp ${LIVECD_ROOT}/profiles/${CD_PROFILE}/base-packages $STOREDIR || chroot_die
	if [ -d ${LIVECD_ROOT}/profiles/${CD_PROFILE}/launcher ]
	then
		cp -a ${LIVECD_ROOT}/profiles/${CD_PROFILE}/launcher $STOREDIR || chroot_die
	fi
	cat > $STOREDIR/base-build << EOF
cd /tmp/livecd
source /tmp/livecd/build-setup || exit 1
mv /etc/fstab /etc/fstab.bak
#update portage, then get ccache up and running.
#on separate line to allow for a portage db upgrade
emerge --noreplace portage 
ewrapper --noreplace ccache
emerge --noreplace distcc
distcc-config --set-hosts "${DISTCC_HOSTS}"
distccd &
echo 'MAKEOPTS="${MAKEOPTS}"' >>/etc/make.conf
#build our packages...
for x in \`cat /tmp/livecd/base-packages | grep -v ^#\`
 do
        if [ "\${x:0:1}" = "^" ]
             then
             ACCEPT_KEYWORDS="~${MAINARCH}" emerge -pv --noreplace --buildpkg --usepkg \${x:1} || exit 1
             ACCEPT_KEYWORDS="~${MAINARCH}" emerge --noreplace --buildpkg --usepkg \${x:1} || exit 1
        else
             emerge -pv --noreplace --buildpkg --usepkg \$x || exit 1
             emerge --noreplace --buildpkg --usepkg \$x || exit 1
                        fi
                done
gcc ${CFLAGS} freeramdisk.c -o /sbin/freeramdisk || exit 1
strip /sbin/freeramdisk
if [ -d /tmp/livecd/launcher ]
then
	cd /tmp/livecd/launcher
	#get the qt stuff in our path
	env-update
	source /etc/profile
	qmake || exit 1
	make || exit 1
	cp gamelaunch /usr/sbin/ || exit 1
fi
EOF
	chmod +x $STOREDIR/base-build
	chroot $CHROOT_PATH /tmp/livecd/base-build
	[ $? -ne 0 ] && chroot_die "base build failure"
}

kern_build() {
	cp ${LIVECD_ROOT}/profiles/${CD_PROFILE}/kern-packages $STOREDIR || chroot_die
	cat > $STOREDIR/kern-build << EOF
cd /tmp/livecd
source /tmp/livecd/build-setup || exit 1
#build our packages...
for x in \`cat /tmp/livecd/kern-packages | grep -v ^#\`
do
                        if [ "\${x:0:1}" = "^" ]
                        then
                                ACCEPT_KEYWORDS="~${MAINARCH}" emerge -pv --noreplace --buildpkg --usepkg \${x:1} || exit 1
                                ACCEPT_KEYWORDS="~${MAINARCH}" emerge --noreplace --buildpkg --usepkg \${x:1} || exit 1
                        else
                                emerge -pv --noreplace --buildpkg --usepkg \$x || exit 1
                                emerge --noreplace --buildpkg --usepkg \$x || exit 1
                        fi
                done

EOF
	chmod +x $STOREDIR/kern-build
	chroot $CHROOT_PATH /tmp/livecd/kern-build
	[ $? -ne 0 ] && chroot_die "kernel packages build failure"
}

kernel_build() {
	# safely call genkernel here, and then move the resulting kernel to the correct location.
}

cloop_create() {
	umount_all
    rm -f ${CD_BUILDROOT}/livecd.*
    rm -rf ${CD_BUILDROOT}/isoroot
    mkzftree -z 9 --verbose -V 4 -p 2 ${CD_BUILDROOT}/cdroot ${CD_BUILDROOT}/isoroot ||die
}

iso_create() {
	install -d ${ISO_ROOT}/isolinux
	cp ${LIVECD_ROOT}/archives/isolinux.bin ${ISO_ROOT}/isolinux || die
	cp ${LIVECD_ROOT}/profiles/${CD_PROFILE}/isolinux.cfg ${ISO_ROOT}/isolinux || die
	cp ${LIVECD_ROOT}/profiles/${CD_PROFILE}/{*.lss,*.msg} ${ISO_ROOT}/isolinux || die
	cp ${STOREDIR}/kernel/bzImage ${ISO_ROOT}/isolinux/gentoo || die
	cp ${STOREDIR}/kernel/initrd ${ISO_ROOT}/isolinux/initrd || die

	if [ "${BOOTSPLASH}" = "yes" ]
       	then
        	cat ${LIVECD_ROOT}/profiles/${CD_PROFILE}/aux-files/1024.initrd >> ${ISO_ROOT}/isolinux/initrd || die
        fi
	
	if [ -f ${LIVECD_ROOT}/profiles/${CD_PROFILE}/aux-files/memtest ]
		then
		cp ${LIVECD_ROOT}/profiles/${CD_PROFILE}/aux-files/memtest ${ISO_ROOT}/isolinux || die
	fi
	
	#First, clean up any old loops so we don't get extras on the Cd
    rm -f ${ISO_ROOT}/${CLOOP_FILE} ${ISO_ROOT}/${LOOP_FILE}

	#now, copy the one we want into place
	mkisofs -J -R -l -o ${CD_BUILDROOT}/${CD_ISONAME} -b isolinux/isolinux.bin -c isolinux/boot.cat \
	-no-emul-boot -boot-load-size 4 -boot-info-table -z ${ISO_ROOT}
}

chroot_generate() {
	umount_all
	[ ! -e "$CD_STAGEFILE" ] && chroot_die "$CD_STAGEFILE not found; please run \"fetch\" first."
	[ -e "$CHROOT_PATH" ] && chroot_die "$CD_BUILDCHROOT already exists; please run $0 $CD_PROFILE delete before running $0 $CD_PROFILE build"
	#create build chroot directory and extract stage tarball
	install -d "$CHROOT_PATH"
	echo ">>> Extracting stage tarball..."
	tar xjpf $CD_STAGEFILE -C $CHROOT_PATH || die "stage tarball extraction error"
	
	#set up our private temp directory and the mount-point inside the chroot.
	install -d "$STOREDIR" "${CHROOT_PATH}/tmp/livecd" || die "couldn't create chroot temp. directories"
	
	#set up distfile mount-point...
	install -d "${CHROOT_PATH}/home/distfiles" || die "couldn't create /home/distfiles mountpoint"

	#set up the profile symlink so that it points to the profile we want
	rm -f "${CHROOT_PATH}/etc/make.profile"
	ln -s ../usr/portage/profiles/${CD_PORTAGE_PROFILE} ${CHROOT_PATH}/etc/make.profile

	#copy our local resolv.conf and hosts over for now; this allows downloading to work.  
	cp /etc/resolv.conf /etc/hosts ${CHROOT_PATH}/etc

	#let's do this....
	mount_all
	build_setup
	base_build
	kernel_build
	kern_build
	umount_all
}

chroot_clean() {
	umount_all
    #first do local modifications script
    if [ -e "${LIVECD_ROOT}/profiles/${CD_PROFILE}/mods" ]
    then
    	source ${LIVECD_ROOT}/profiles/${CD_PROFILE}/mods
    else
        echo "No ${CD_PROFILE} mods script found; skipping."
    fi
    #next do global clean script
    if [ -e "${LIVECD_ROOT}/profiles/${CD_PROFILE}/clean" ]
    then
        source ${LIVECD_ROOT}/profiles/${CD_PROFILE}/clean
    else
        echo "No global clean script found; skipping."
    fi
    #now do the local post-clean
    if [ -e "${LIVECD_ROOT}/profiles/${CD_PROFILE}/post-clean" ]
    then
        source ${LIVECD_ROOT}/profiles/${CD_PROFILE}/post-clean
    else
        echo "No ${CD_PROFILE} post-clean script found; skipping."
    fi
    umount_all

}

case $1 in

	enter)
		clst_CHROOT clst_chroot_path
	;;

