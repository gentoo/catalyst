#!/bin/bash
mkisofs -J -R -l -z -o ../gentoo.iso .
isomarkboot ../gentoo.iso /boot/bootlx
