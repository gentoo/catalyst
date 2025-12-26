"""
Disk image stage1 target
"""
# NOTE: That^^ docstring has influence catalyst-spec(5) man page generation.

from catalyst.support import normpath
from catalyst import log

from catalyst.base.stagebase import StageBase


class diskimage_stage1(StageBase):
    """
    Builder class for disk image stage1.
    """
    required_values = frozenset([
        "diskimage/packages",
    ])
    valid_values = required_values | frozenset([
        "diskimage/use",
    ])

    def __init__(self, spec, addlargs):
        StageBase.__init__(self, spec, addlargs)

    def set_action_sequence(self):
        self.build_sequence.extend([
            self.build_packages,
        ])
        self.finish_sequence.extend([
            self.clean,
        ])
        self.set_completion_action_sequences()

    def set_spec_prefix(self):
        self.settings["spec_prefix"] = "diskimage"

    def set_catalyst_use(self):
        StageBase.set_catalyst_use(self)
        if "catalyst_use" in self.settings:
            self.settings["catalyst_use"].append("diskimage")
        else:
            self.settings["catalyst_use"] = ["diskiage"]

    def set_packages(self):
        StageBase.set_packages(self)
        if self.settings["spec_prefix"]+"/packages" in self.settings:
            if isinstance(self.settings[self.settings['spec_prefix']+'/packages'], str):
                self.settings[self.settings["spec_prefix"]+"/packages"] = \
                    self.settings[self.settings["spec_prefix"] +
                                  "/packages"].split()

    def set_pkgcache_path(self):
        if "pkgcache_path" in self.settings:
            if not isinstance(self.settings['pkgcache_path'], str):
                self.settings["pkgcache_path"] = normpath(
                    ' '.join(self.settings["pkgcache_path"]))
        else:
            StageBase.set_pkgcache_path(self)

    def write_make_conf(self, setup=True):
        StageBase.write_make_conf(self, setup)

        # Append to make.conf
        makepath = normpath(self.settings["chroot_path"] +
                            self.settings["make_conf"])
        with open(makepath, "a") as myf:
            log.notice("Appending diskimage specifics to stage make.conf %s" % makepath)
            myf.write(
                '\n'
                '# We really want to use binary packages here and use them properly.\n'
                'FEATURES="binpkg-request-signature"\n')
