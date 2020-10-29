"""
LiveCD stage2 target, builds upon previous LiveCD stage1 tarball
"""
# NOTE: That^^ docstring has influence catalyst-spec(5) man page generation.

from catalyst.support import (normpath, file_locate, CatalystError)
from catalyst.fileops import clear_dir
from catalyst.base.stagebase import StageBase


class livecd_stage2(StageBase):
    """
    Builder class for a LiveCD stage2 build.
    """
    required_values = frozenset([
        "boot/kernel",
    ])
    valid_values = required_values | frozenset([
        "livecd/bootargs",
        "livecd/cdtar",
        "livecd/depclean",
        "livecd/empty",
        "livecd/fsops",
        "livecd/fsscript",
        "livecd/fstype",
        "livecd/gk_mainargs",
        "livecd/iso",
        "livecd/linuxrc",
        "livecd/modblacklist",
        "livecd/motd",
        "livecd/overlay",
        "livecd/rcadd",
        "livecd/rcdel",
        "livecd/readme",
        "livecd/rm",
        "livecd/root_overlay",
        "livecd/type",
        "livecd/unmerge",
        "livecd/users",
        "livecd/verify",
        "livecd/volid",
        "livecd/xdm",
        "livecd/xinitrc",
        "livecd/xsession",
        "portage_overlay",
    ])

    def __init__(self, spec, addlargs):
        StageBase.__init__(self, spec, addlargs)
        if "livecd/type" not in self.settings:
            self.settings["livecd/type"] = "generic-livecd"

        file_locate(self.settings, ["cdtar", "controller_file"])

    def set_spec_prefix(self):
        self.settings["spec_prefix"] = "livecd"

    def set_target_path(self):
        '''Set the target path for the finished stage.

        This method runs the StageBase.set_target_path mehtod,
        and additionally creates a staging directory for assembling
        the final components needed to produce the iso image.
        '''
        super(livecd_stage2, self).set_target_path()
        clear_dir(self.settings['target_path'])

    def run_local(self):
        # what modules do we want to blacklist?
        if "livecd/modblacklist" in self.settings:
            path = normpath(self.settings["chroot_path"] +
                            "/etc/modprobe.d/blacklist.conf")
            try:
                with open(path, "a") as myf:
                    myf.write("\n#Added by Catalyst:")
                    # workaround until config.py is using configparser
                    if isinstance(self.settings["livecd/modblacklist"], str):
                        self.settings["livecd/modblacklist"] = self.settings[
                            "livecd/modblacklist"].split()
                    for x in self.settings["livecd/modblacklist"]:
                        myf.write("\nblacklist "+x)
            except:
                self.unbind()
                raise CatalystError("Couldn't open " +
                                    self.settings["chroot_path"] +
                                    "/etc/modprobe.d/blacklist.conf.",
                                    print_traceback=True)

    def set_action_sequence(self):
        self.prepare_sequence.extend([
            "unpack",
            "config_profile_link",
            "setup_confdir",
            "portage_overlay",
        ])
        self.build_sequence.extend([
            "bind",
            "chroot_setup",
            "setup_environment",
            "run_local",
            "build_kernel"
        ])
        if "fetch" not in self.settings["options"]:
            self.build_sequence.extend([
                "bootloader",
                "preclean",
                "livecd_update",
                "root_overlay",
                "fsscript",
                "rcupdate",
                "unmerge",
                "unbind",
            ])
            self.finish_sequence.extend([
                "remove",
                "empty",
                "clean",
                "target_setup",
                "setup_overlay",
                "create_iso",
            ])
        self.finish_sequence.append("clear_autoresume")
