"""
stage4 target, builds upon previous stage3/stage4 tarball
"""
# NOTE: That^^ docstring has influence catalyst-spec(5) man page generation.

from catalyst.base.stagebase import StageBase


class stage4(StageBase):
    """
    Builder class for stage4.
    """
    required_values = frozenset([
        "stage4/packages",
    ])
    valid_values = required_values | frozenset([
        "boot/kernel",
        "portage_overlay",
        "splash_theme",
        "stage4/empty",
        "stage4/fsscript",
        "stage4/gk_mainargs",
        "stage4/linuxrc",
        "stage4/rcadd",
        "stage4/rcdel",
        "stage4/rm",
        "stage4/root_overlay",
        "stage4/unmerge",
        "stage4/use",
    ])

    def __init__(self, spec, addlargs):
        StageBase.__init__(self, spec, addlargs)

    def set_cleanables(self):
        self.settings["cleanables"] = ["/var/tmp/*", "/tmp/*"]

    def set_action_sequence(self):
        self.settings['action_sequence'] = [
            "unpack",
            "config_profile_link",
            "setup_confdir",
            "portage_overlay",
            "bind",
            "chroot_setup",
            "setup_environment",
            "build_packages",
            "build_kernel",
            "bootloader",
            "root_overlay",
            "fsscript",
            "preclean",
            "rcupdate",
            "unmerge",
            "unbind",
            "remove",
            "empty",
            "clean",
        ]
        self.set_completion_action_sequences()
