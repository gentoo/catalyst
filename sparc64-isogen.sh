#!/bin/bash
mkisofs -J -R -z -l -o ../gentoo.iso  -G /boot/isofs.b -B ... .
