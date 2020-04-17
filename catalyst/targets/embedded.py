"""
Enbedded target, similar to the stage2 target, builds upon a stage2 tarball.

A stage2 tarball is unpacked, but instead
of building a stage3, it emerges @system into another directory
inside the stage2 system.  This way, we do not have to emerge GCC/portage
into the staged system.
It may sound complicated but basically it runs
ROOT=/tmp/submerge emerge --something foo bar .
"""
# NOTE: That^^ docstring has influence catalyst-spec(5) man page generation.

from catalyst import log
from catalyst.support import normpath
from catalyst.base.stagebase import StageBase


class embedded(StageBase):
    """
    Builder class for embedded target
    """
    required_values = frozenset()
    valid_values = required_values | frozenset([
        "boot/kernel",
        "embedded/empty",
        "embedded/fs-finish",
        "embedded/fs-ops",
        "embedded/fs-prepare",
        "embedded/fs-type",
        "embedded/linuxrc",
        "embedded/mergeroot",
        "embedded/packages",
        "embedded/rm",
        "embedded/runscript",
        "embedded/unmerge",
        "embedded/use",
    ])

    def __init__(self, spec, addlargs):
        StageBase.__init__(self, spec, addlargs)

    def set_action_sequence(self):
        self.settings['action_sequence'] = [
            "dir_setup",
            "unpack",
            "config_profile_link",
            "setup_confdir",
            "portage_overlay",
            "bind",
            "chroot_setup",
            "setup_environment",
            "build_kernel",
            "build_packages",
            "bootloader",
            "root_overlay",
            "fsscript",
            "unmerge",
            "unbind",
            "remove",
            "empty",
            "clean",
            "capture",
            "clear_autoresume",
        ]

    def set_stage_path(self):
        self.settings["stage_path"] = normpath(
            self.settings["chroot_path"]+"/tmp/mergeroot")
        log.info('embedded stage path is %s', self.settings['stage_path'])

    def set_root_path(self):
        self.settings["root_path"] = normpath("/tmp/mergeroot")
        log.info('embedded root path is %s', self.settings['root_path'])
