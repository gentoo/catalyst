Gentoo Linux Installation LiveCD boot options - [F1 to display available kernels]

Many kernel profiles exist on a livecd. Please hit F1
to see the available kernels on this livecd.  Please note that
the -nofb counterparts to each kernel disable the framebuffer
and bootsplash. Additionally, the memtest86 boot option is available
to test local RAM for errors. To use memtest86, just type 'memtest86'.

Options available to pass to your kernel of choice.
- agpgart       loads agpgart (use if you have graphic problems,lockups)
- acpi=on       loads support for ACPI firmware
- ide=nodma     Force disabling of dma for malfunctioning ide devices
                to umount /mnt/cdrom to mount another cdrom.
- doscsi        scan for scsi devices (breaks some ethernet cards)
- doataraid     loads ide raid modules from initrd
- dopcmcia      starts pcmcia service
- doapm         disables apm module load
- dofirewire    modprobes firewire modules in initrd (for firewire cdroms,etc)
- dokeymap      enable keymap selection for non-us keyboard layouts
- docache       Cache the entire runtime portion of cd in ram, allows you
- nodetect      causes hwsetup/kudzu and hotplug not to run
- nousb         disables usb module load from initrd, disables hotplug
- nodhcp        dhcp does not automatically start if nic detected
- noraid        disables loading of evms modules
- nohotplug     disables loading hotplug service
- noapic        disable apic (try if having hardware problems ,nics,scsi,etc)
