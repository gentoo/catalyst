# Copyright david@futuretel.com
# puts a the embedded image into a cramfs

root_fs_path="${clst_chroot_path}/tmp/mergeroot"

die() {
	echo "$1"
	exit 1
}

case $1 in

run)
	# move this to preclean stage
	# it's a hack because dhcpcd is lame
	install -d $root_fs_path/var/lib/dhcpc
	
	install -d $clst_image_path
	mkcramfs $root_fs_path $clst_image_path/root.img
	imagesize=`du -sk $clst_image_path/root.img | cut -f1`
	echo "Created cramfs image at ${clst_image_path}/root.img"
	echo "Image size: ${imagesize}k"
	;;

preclean)
	;;

esac
exit 0
