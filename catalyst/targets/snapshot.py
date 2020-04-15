"""
Snapshot target
"""

from DeComp.compress import CompressMap

from catalyst import log
from catalyst.support import normpath, cmd
from catalyst.base.targetbase import TargetBase
from catalyst.base.genbase import GenBase
from catalyst.fileops import (clear_dir, ensure_dirs)


class snapshot(TargetBase, GenBase):
    """
    Builder class for snapshots.
    """
    required_values = frozenset([
        "target",
        "version_stamp",
    ])
    valid_values = required_values | frozenset([
        "compression_mode",
    ])

    def __init__(self, myspec, addlargs):
        TargetBase.__init__(self, myspec, addlargs)
        GenBase.__init__(self, myspec)

        self.settings["target_subpath"] = "repos"
        st = self.settings["storedir"]
        self.settings["snapshot_path"] = normpath(st + "/snapshots/"
                                                  + self.settings["snapshot_name"]
                                                  + self.settings["version_stamp"])
        self.settings["tmp_path"] = normpath(
            st+"/tmp/"+self.settings["target_subpath"])

    def setup(self):
        x = normpath(self.settings["storedir"]+"/snapshots")
        ensure_dirs(x)

    def run(self):
        if "purgeonly" in self.settings["options"]:
            self.purge()
            return True

        if "purge" in self.settings["options"]:
            self.purge()

        success = True
        self.setup()
        log.notice('Creating %s tree snapshot %s from %s ...',
                   self.settings["repo_name"], self.settings['version_stamp'],
                   self.settings['portdir'])

        mytmp = self.settings["tmp_path"]
        ensure_dirs(mytmp)

        cmd(['rsync', '-a', '--no-o', '--no-g', '--delete',
             '--exclude=/packages/',
             '--exclude=/distfiles/',
             '--exclude=/local/',
             '--exclude=CVS/',
             '--exclude=.svn',
             '--exclude=.git/',
             '--filter=H_**/files/digest-*',
             self.settings['portdir'] + '/',
             mytmp + '/' + self.settings['repo_name'] + '/'],
            env=self.env)

        log.notice('Compressing %s snapshot tarball ...',
                   self.settings["repo_name"])
        compressor = CompressMap(self.settings["compress_definitions"],
                                 env=self.env, default_mode=self.settings['compression_mode'],
                                 comp_prog=self.settings["comp_prog"])
        infodict = compressor.create_infodict(
            source=self.settings["repo_name"],
            destination=self.settings["snapshot_path"],
            basedir=mytmp,
            filename=self.settings["snapshot_path"],
            mode=self.settings["compression_mode"],
            auto_extension=True
        )
        if not compressor.compress(infodict):
            success = False
            log.error('Snapshot compression failure')
        else:
            filename = '.'.join([self.settings["snapshot_path"],
                                 compressor.extension(self.settings["compression_mode"])])
            log.notice('Snapshot successfully written to %s', filename)
            self.gen_contents_file(filename)
            self.gen_digest_file(filename)
        if "keepwork" not in self.settings["options"]:
            self.cleanup()
        if success:
            log.info('snapshot: complete!')
        return success

    def kill_chroot_pids(self):
        pass

    def cleanup(self):
        log.info('Cleaning up ...')
        self.purge()

    def purge(self):
        clear_dir(self.settings['tmp_path'])
