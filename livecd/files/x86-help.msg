Gentoo Linux LiveCD boot options - [F1 to display available kernels]

Please hit F1 to see the available kernels on this livecd.  Please note that
the -nofb counterparts to each kernel disable the framebuffer
and splash images. Additionally, the memtest86 boot option is available
to test local RAM for errors. To use memtest86, just type 'memtest86'.

Options available to pass to your kernel of choice.
- agpgart       loads agpgart (use if you have graphic problems,lockups)
- acpi=on       loads support for ACPI firmware
- ide=nodma     force disabling of DMA for malfunctioning IDE devices
- doscsi        scan for scsi devices (breaks some ethernet cards)
- dopcmcia      starts pcmcia service for PCMCIA cdroms
- nofirewire    disables firewire modules in initrd (for firewire cdroms,etc)
- nokeymap      disables keymap selection for non-us keyboard layouts
- docache       cache the entire runtime portion of cd in RAM, allows you
		to umount /mnt/cdrom to mount another cdrom.
- nodetect      causes hwsetup/kudzu and hotplug not to run
- nousb         disables usb module load from initrd, disables hotplug
- nodhcp        dhcp does not automatically start if nic detected
- nohotplug     disables loading hotplug service
- noapic        disable apic (try if having hardware problems nics,scsi,etc)
- hdx=stroke	allows you to partition the whole harddrive even when your BIOS
		can't handle large harddrives
