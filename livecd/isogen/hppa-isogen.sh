#!/bin/bash
ISO=${ISO:-../gentoo.iso}
mkisofs -J -R -r -l -o ${ISO} .
#palo -f boot/palo.conf -C ${ISO}
palo -k vmlinux -b boot/iplboot -r initrd -c "0/vmlinux initrd=initrd TERM=linux root=/dev/ram0 init=/linuxrc cdroot looptype=normal loop=/livecd.loop" -C ${ISO} -f foo


