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
        "repos",
        "stage4/empty",
        "stage4/fsscript",
        "stage4/gk_mainargs",
        "stage4/groups",
        "stage4/linuxrc",
        "stage4/rcadd",
        "stage4/rcdel",
        "stage4/rm",
        "stage4/root_overlay",
        "stage4/ssh_public_keys",
        "stage4/unmerge",
        "stage4/use",
        "stage4/users",
    ])

    def __init__(self, spec, addlargs):
        StageBase.__init__(self, spec, addlargs)

    def set_cleanables(self):
        StageBase.set_cleanables(self)

        # We want to allow stage4's fsscript to generate a default
        # /etc/resolv.conf
        self.settings["cleanables"].remove('/etc/resolv.conf')

    def set_action_sequence(self):
        self.build_sequence.extend([
            self.build_packages,
            self.build_kernel,
            self.bootloader,
            self.root_overlay,
            self.fsscript,
            self.preclean,
            self.rcupdate,
            self.unmerge,
        ])
        self.finish_sequence.extend([
            self.remove,
            self.groups,
            self.users,
            self.ssh_public_keys,
            self.empty,
            self.clean,
        ])
        self.set_completion_action_sequences()
