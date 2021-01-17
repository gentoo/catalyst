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
        "embedded/root_overlay",
        "embedded/runscript",
        "embedded/unmerge",
        "embedded/use",
    ])

    def __init__(self, spec, addlargs):
        StageBase.__init__(self, spec, addlargs)

    def set_action_sequence(self):
        self.prepare_sequence.extend([
            self.unpack,
            self.config_profile_link,
            self.setup_confdir,
            self.portage_overlay,
        ])
        self.build_sequence.extend([
            self.bind,
            self.chroot_setup,
            self.setup_environment,
            self.build_kernel,
            self.build_packages,
            self.root_overlay,
            self.fsscript,
            self.unmerge,
        ])
        self.finish_sequence.extend([
            self.remove,
            self.empty,
            self.clean,
            self.capture,
            self.clear_autoresume,
        ])

    def set_root_path(self):
        self.settings["root_path"] = normpath("/tmp/mergeroot")
        log.info('embedded root path is %s', self.settings['root_path'])
