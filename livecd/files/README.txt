
This lists the possible command line options that can be used to tweak the boot
process of this CD.  This lists the Gentoo-specific options, along with a few
options that are built-in to the kernel, but that have been proven very useful
to our users.  Also, all options that start with "do" have a "no" inverse, that
does the opposite.  For example, "doscsi" enables SCSI support in the initial
ramdisk boot, while "noscsi" disables it.


Hardware options:
acpi=on         This loads support for ACPI and also causes the acpid daemon to
                be started by the CD on boot.  This is only needed if your
                system requires ACPI to function properly.  This is not
                required for Hyperthreading support.
acpi=off        Completely disables ACPI.  This is useful on some older systems
                and is also a requirement for using APM.  This will disable any
                Hyperthreading support of your processor.
console=X       This sets up serial console access for the CD.  The first
                option is the device, usually ttyS0 on x86, followed by any
                connection options, which are comma separated.  The default
                options are 9600,8,n,1.
dmraid=X        This allows for passing options to the device-mapper RAID
                subsystem.  Options should be encapsulated in quotes.
doapm           This loads APM driver support.  This requires you to also use
                acpi=off.
dopcmcia        This loads support for PCMCIA and Cardbus hardware and also
                causes the pcmcia cardmgr to be started by the CD on boot.
                This is only required when booting from PCMCIA/Cardbus devices.
doscsi          This loads support for most SCSI controllers.  This is also a
                requirement for booting most USB devices, as they use the SCSI
                subsystem of the kernel.
hda=stroke      This allows you to partition the whole hard disk even when your
                BIOS is unable to handle large disks.  This option is only used
                on machines with an older BIOS.  Replace hda with the device
                that is requiring this option.
ide=nodma       This forces the disabling of DMA in the kernel and is required
                by some IDE chipsets and also by some CDROM drives.  If your
                system is having trouble reading from your IDE CDROM, try this
                option.  This also disables the default hdparm settings from
                being executed.
noapic          This disables the Advanced Programmable Interrupt Controller
                that is present on newer motherboards.  It has been known to
                cause some problems on older hardware.
nodetect        This disables all of the autodetection done by the CD,
                including device autodetection and DHCP probing.  This is
                useful for doing debugging of a failing CD or driver.
nodhcp          This disables DHCP probing on detected network cards.  This is
                useful on networks with only static addresses.
nodmraid        Disables support for device-mapper RAID, such as that used for
                on-board IDE/SATA RAID controllers.
nofirewire      This disables the loading of Firewire modules.  This should
                only be necessary if your Firewire hardware is causing
                a problem with booting the CD.
nogpm           This diables gpm console mouse support.
nohotplug       This disables the loading of the hotplug and coldplug init
                scripts at boot.  This is useful for doing debugging of a
                failing CD or driver.
nokeymap        This disables the keymap selection used to select non-US
                keyboard layouts.
nolapic         This disables the local APIC on Uniprocessor kernels.
nosata          This disables the loading of Serial ATA modules.  This is used
                if your system is having problems with the SATA subsystem.
nosmp           This disables SMP, or Symmetric Multiprocessing, on SMP-enabled
                kernels.  This is useful for debugging SMP-related issues with
                certain drivers and motherboards.
nosound         This disables sound support and volume setting.  This is useful
                for systems where sound support causes problems.
nousb           This disables the autoloading of USB modules.  This is useful
                for debugging USB issues.
slowusb         This adds some extra pauses into the boot process for slow
                USB CDROMs, like in the IBM BladeCenter.
Volume/Device Management:
doevms          This enables support for IBM's pluggable EVMS, or Enterprise
                Volume Management System.  This is not safe to use with lvm2.
dolvm           This enables support for Linux's Logical Volume Management.
                This is not safe to use with evms2.
Screen reader access:
speakup.synth=synth  starts speakup using a given synthesizer.
                     supported synths are acntpc, acntsa, apollo, audptr, bns,
                     decext, dectlk, dtlk, keypc, ltlk, spkout and txprt.
                     Also, soft is supported for software speech and dummy is
                     supported for testing.
speakup.quiet=1      sets the synthesizer not to speak until a key is pressed.
speakup_SYNTH.port=n sets the port for internal synthesizers.
speakup_SYNTH.ser=n  sets the serial port for external synthesizers.
Other options:
debug           Enables debugging code.  This might get messy, as it displays
                a lot of data to the screen.
docache         This caches the entire runtime portion of the CD into RAM,
                which allows you to umount /mnt/cdrom and mount another CDROM.
                This option requires that you have at least twice as much
                available RAM as the size of the CD.
doload=X        This causes the initial ramdisk to load any module listed, as
                well as dependencies.  Replace X with the module name.
                Multiple modules can be specified by a comma-separated list.
dosshd          Starts sshd on boot, which is useful for unattended installs.
passwd=foo      Sets whatever follows the equals as the root password, which
                is required for dosshd since we scramble the root password.
noload=X        This causes the initial ramdisk to skip the loading of a
                specific module that may be causing a problem.  Syntax matches
                that of doload.
nonfs           Disables the starting of portmap/nfsmount on boot.
nox             This causes an X-enabled LiveCD to not automatically start X,
                but rather, to drop to the command line instead.
scandelay       This causes the CD to pause for 10 seconds during certain
                portions the boot process to allow for devices that are slow to
                initialize to be ready for use.
scandelay=X     This allows you to specify a given delay, in seconds, to be
                added to certain portions of the boot process to allow for
                devices that are slow to initialize to be ready for use.
                Replace X with the number of seconds to pause.
