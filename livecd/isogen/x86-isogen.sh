#!/bin/bash
mkisofs -J -R -l -o ../gentoo.iso -b isolinux/isolinux.bin -c isolinux/boot.cat -boot-load-size 4 -boot-info-table -z .
