subarch: x86
version_stamp: 20031215
target: livecd-stage2
rel_type: default
rel_version: 1.4
snapshot: 20031215
source_subpath: default-x86-1.4/livecd-stage2-x86-20031215
boot/kernel: gentoo
livecd-stage3/cdtar: /path/to/cd.tar
livecd-stage3/runscript: /path/to/myrunscript.sh
livecd-stage3/clean:
	/usr/src/linux
	/usr/share/doc
	/usr/share/man
	/var/db/pkg
	/var/tmp
