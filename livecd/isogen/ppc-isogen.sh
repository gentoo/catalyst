#!/bin/bash
mkisofs -J -r -netatalk -hfs -probe -map boot/map.hfs -part -no-desktop -hfs-volid GentooPPC_2004.0 -hfs-bless ./boot -o ../gentoo.iso .
