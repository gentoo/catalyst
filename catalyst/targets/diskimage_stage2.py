"""
Disk image stage2 target, builds upon previous disk image stage1 tarball
"""
# NOTE: That^^ docstring has influence catalyst-spec(5) man page generation.

from catalyst.support import (normpath, file_locate, CatalystError)
from catalyst.fileops import clear_dir
from catalyst.base.stagebase import StageBase


class diskimage_stage2(StageBase):
    """
    Builder class for a disk image stage2 build.
    """
    required_values = frozenset([
        "boot/kernel",
    ])
    valid_values = required_values | frozenset([
        "diskimage/bootargs",
        "diskimage/fstar",
        "diskimage/depclean",
        "diskimage/empty",
        "diskimage/fsops",
        "diskimage/fsscript",
        "diskimage/fstype",
        "diskimage/gk_mainargs",
        "diskimage/image",
        "diskimage/imageformat",
        "diskimage/modblacklist",
        "diskimage/motd",
        "diskimage/rcadd",
        "diskimage/rcdel",
        "diskimage/readme",
        "diskimage/rm",
        "diskimage/type",
        "diskimage/unmerge",
        "diskimage/users",
        "diskimage/verify",
        "diskimage/volid",
        "repos",
    ])

    def __init__(self, spec, addlargs):
        StageBase.__init__(self, spec, addlargs)
        if "diskimage/type" not in self.settings:
            self.settings["diskimage/type"] = "generic-diskimage"

        file_locate(self.settings, ["fstar", "controller_file"])

    def set_spec_prefix(self):
        self.settings["spec_prefix"] = "diskimage"

    def set_target_path(self):
        '''Set the target path for the finished stage.

        This method runs the StageBase.set_target_path mehtod,
        and additionally creates a staging directory for assembling
        the final components needed to produce the iso image.
        '''
        super(diskimage_stage2, self).set_target_path()
        clear_dir(self.settings['target_path'])

    def run_local(self):
        # what modules do we want to blacklist?
        if "diskimage/modblacklist" in self.settings:
            path = normpath(self.settings["chroot_path"] +
                            "/etc/modprobe.d/blacklist.conf")
            try:
                with open(path, "a") as myf:
                    myf.write("\n#Added by Catalyst:")
                    # workaround until config.py is using configparser
                    if isinstance(self.settings["diskimage/modblacklist"], str):
                        self.settings["diskimage/modblacklist"] = self.settings[
                            "diskimage/modblacklist"].split()
                    for x in self.settings["diskimage/modblacklist"]:
                        myf.write("\nblacklist "+x)
            except Exception as e:
                raise CatalystError("Couldn't open " +
                                    self.settings["chroot_path"] +
                                    "/etc/modprobe.d/blacklist.conf.",
                                    print_traceback=True) from e

    def set_action_sequence(self):
        self.build_sequence.extend([
            self.run_local,
            self.build_kernel
        ])
        if "fetch" not in self.settings["options"]:
            self.build_sequence.extend([
                self.create_diskimage,           # create image file
                self.open_diskimage,
                self.make_filesystems,           # partition, make filesystems
                self.move_into_image,
                self.bootloader,
                self.preclean,
                self.fsscript,
                self.rcupdate,
                self.unmerge,
            ])
            self.finish_sequence.extend([
                self.remove,
                self.empty,
                self.clean,
                self.target_setup,
                self.close_diskimage,           # unmount, unmap
            ])
        self.set_completion_action_sequences()
