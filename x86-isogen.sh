#!/bin/bash
mkisofs -J -R -l -o ../gentoo.iso -b isolinux/isolinux.bin -c isolinux/boot.cat -no-emul-boot -boot-load-size 4 -boot-info-table -z .


