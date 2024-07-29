"""
stage1 target
"""
# NOTE: That^^ docstring has influence catalyst-spec(5) man page generation.

from catalyst import log
from catalyst.support import (normpath, get_repo_name)
from catalyst.fileops import move_path
from catalyst.base.stagebase import StageBase

from pathlib import Path

class stage1(StageBase):
    """
    Builder class for a stage1 installation tarball build.
    """
    required_values = frozenset()
    valid_values = required_values | frozenset([
        "chost",
        "update_seed",
        "update_seed_command",
    ])

    def __init__(self, spec, addlargs):
        StageBase.__init__(self, spec, addlargs)
        # In the stage1 build we need to make sure that the ebuild repositories are
        # accessible within $ROOT too... otherwise relative symlinks may point nowhere
        # and, e.g., portageq may malfunction due to missing profile.
        # Create a second bind mount entry for each repository
        for path, name, _ in self.repos:
            name = get_repo_name(path)
            mount_id = f'root_repo_{name}'
            self.mount[mount_id] = {
                'enable': True,
                'source': path,
                'target': Path(normpath("/tmp/stage1root") + "/" + str(self.get_repo_location(name)))
            }

    def set_root_path(self):
        # sets the root path, relative to 'chroot_path', of the stage1 root
        self.settings["root_path"] = normpath("/tmp/stage1root")
        log.info('stage1 root path is %s', self.settings['root_path'])

    def set_cleanables(self):
        StageBase.set_cleanables(self)
        self.settings["cleanables"].extend([
            self.settings["port_conf"] + "/package*",
        ])

    # XXX: How do these override_foo() functions differ from the ones in StageBase and why aren't they in stage3_target?
    # XXY: It appears the difference is that these functions are actually doing something and the ones in stagebase don't :-(
    # XXZ: I have a wierd suspicion that it's the difference in capitolization

    def override_chost(self):
        if "chost" in self.settings:
            self.settings["CHOST"] = self.settings["chost"]

    def override_common_flags(self):
        if "common_flags" in self.settings:
            self.settings["COMMON_FLAGS"] = self.settings["common_flags"]

    def override_cflags(self):
        if "cflags" in self.settings:
            self.settings["CFLAGS"] = self.settings["cflags"]

    def override_cxxflags(self):
        if "cxxflags" in self.settings:
            self.settings["CXXFLAGS"] = self.settings["cxxflags"]

    def override_fcflags(self):
        if "fcflags" in self.settings:
            self.settings["FCFLAGS"] = self.settings["fcflags"]

    def override_fflags(self):
        if "fflags" in self.settings:
            self.settings["FFLAGS"] = self.settings["fflags"]

    def override_ldflags(self):
        if "ldflags" in self.settings:
            self.settings["LDFLAGS"] = self.settings["ldflags"]

    def set_repos(self):
        StageBase.set_repos(self)
        if "repos" in self.settings:
            log.warning(
                'Using an overlay for earlier stages could cause build issues.\n'
                "If you break it, you buy it.  Don't complain to us about it.\n"
                "Don't say we did not warn you.")

    def set_completion_action_sequences(self):
        '''Override function for stage1

        Its purpose is to move the new stage1root out of the seed stage
        and rename it to the stage1 chroot_path after cleaning the seed stage
        chroot for re-use in stage2 without the need to unpack it.
        '''
        if "fetch" not in self.settings["options"]:
            self.finish_sequence.append(self.capture)
        if "keepwork" in self.settings["options"]:
            self.finish_sequence.append(self.clear_autoresume)
        elif "seedcache" in self.settings["options"]:
            self.finish_sequence.append(self.remove_autoresume)
            self.finish_sequence.append(self.clean_stage1)
        else:
            self.finish_sequence.append(self.remove_autoresume)
            self.finish_sequence.append(self.remove_chroot)

    def clean_stage1(self):
        '''seedcache is enabled, so salvage the /tmp/stage1root,
        remove the seed chroot'''
        log.notice('Salvaging the stage1root from the chroot path ...')
        # move the self.settings["stage_path"] outside of the self.settings["chroot_path"]
        tmp_path = normpath(self.settings["storedir"] + "/tmp/" + "stage1root")
        if move_path(self.settings["stage_path"], tmp_path):
            self.remove_chroot()
            # move it to self.settings["chroot_path"]
            if not move_path(tmp_path, self.settings["chroot_path"]):
                log.error(
                    'clean_stage1 failed, see previous log messages for details')
                return False
            log.notice(
                'Successfully moved and cleaned the stage1root for the seedcache')
            return True
        log.error(
            'clean_stage1 failed to move the stage1root to a temporary loation')
        return False
