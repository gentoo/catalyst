Gentoo Linux LiveCD boot options - [F1 to display available kernels]

Please hit F1 to see the available kernels on this livecd.  Please note that
the -nofb counterparts to each kernel disable the framebuffer
and splash images. Additionally, the memtest86 boot option is available
to test local RAM for errors. To use memtest86, just type 'memtest86'.

Options available to pass to your kernel of choice.
- acpi=on       loads support for ACPI firmware
- ide=nodma     force disabling of DMA for malfunctioning IDE devices
- doscsi        scan for SCSI devices (breaks some ethernet cards)
- dopcmcia      starts card services for PCMCIA CDROMs
- nofirewire    disables firewire modules in initrd (for firewire CDROMs,etc)
- nokeymap      disables keymap selection for non-US keyboard layouts
- docache       cache the entire runtime portion of CD in RAM, allows you
                to umount /mnt/cdrom to mount another CDROM.
- nodetect      causes hwsetup/kudzu and hotplug/coldplug not to run
- nousb         disables USB modules load from initrd
- nodhcp        DHCP does not automatically start if NIC detected
- nohotplug     disables loading hotplug/coldplug services
- noapic        disable APIC (try if having hardware problems NICs,SCSI,etc)
- hdx=stroke    allows you to partition the whole hard disk even when your BIOS
                can't handle large hard disks
- noload=       disables loading a specific module(s), good for debugging
