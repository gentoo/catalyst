"""
Snapshot target
"""

import subprocess
import sys

import fasteners

from pathlib import Path

from catalyst import log
from catalyst.base.targetbase import TargetBase
from catalyst.support import CatalystError, command

class snapshot(TargetBase):
    """
    Builder class for snapshots.
    """
    required_values = frozenset([
        'target',
    ])
    valid_values = required_values | frozenset([
        'snapshot_treeish',
    ])

    def __init__(self, myspec, addlargs):
        TargetBase.__init__(self, myspec, addlargs)

        self.git = command('git')
        self.ebuild_repo = Path(self.settings['repos_storedir'],
                                self.settings['repo_name']).with_suffix('.git')
        self.gitdir = str(self.ebuild_repo)

    def update_ebuild_repo(self) -> str:
        repouri = 'https://anongit.gentoo.org/git/repo/sync/gentoo.git'

        if self.ebuild_repo.is_dir():
            git_cmds = [
                [self.git, '-C', self.gitdir, 'fetch', '--quiet', '--depth=1'],
                [self.git, '-C', self.gitdir, 'update-ref', 'HEAD', 'FETCH_HEAD'],
                [self.git, '-C', self.gitdir, 'gc', '--quiet'],
            ]
        else:
            git_cmds = [
                [self.git, 'clone', '--quiet', '--depth=1', '--bare',
                 # Set some config options to enable git gc to clean everything
                 # except what we just fetched. See git-gc(1).
                 '-c', 'gc.reflogExpire=0',
                 '-c', 'gc.reflogExpireUnreachable=0',
                 '-c', 'gc.rerereresolved=0',
                 '-c', 'gc.rerereunresolved=0',
                 '-c', 'gc.pruneExpire=now',
                 '--branch=stable',
                 repouri, self.gitdir],
            ]


        env = os.environ.copy()
        pgp_keyring = self.settings["repo_openpgp_key_path"]
        if pgp_keyring:
            try:
                import gemato.openpgp
            except ImportError as e:
                 raise CatalystError(
                     f"gemato could not be imported but repo_openpgp_key_path was non-empty."
                 )

            pgp_path = Path(pgp_keyring)
            if not pgp_path.exists() or not pgp_path.is_file():
                raise CatalystError(
                    f"OpenPGP keyring at repo_openpgp_key_path={pgp_path} does not exist. Is sec-keys/openpgp-keys-gentoo-release installed?"
                )

            git_cmds.append(self.git, '-C', self.gitdir, 'verify-commit', 'HEAD')

            openpgp_env = gemato.openpgp.OpenPGPEnvironment
            try:
                with open(pgp_path, "rb") as f:
                    openpgp_env.import_key(f)
                    openpgp_env.refresh_keys()
            except (GematoException, asyncio.TimeoutError) as e:
                raise CatalystError(
                    f"OpenPGP verification via gemato failed: {e}"
                )
                openpgp_env.close()

            env["GNUPGHOME"] = openpgp_env.home

        try:
            for cmd in git_cmds:
                log.notice('>>> ' + ' '.join(cmd))
                subprocess.run(cmd,
                               capture_output=True,
                               check=True,
                               env=env,
                               encoding='utf-8',
                               close_fds=False)

            sp = subprocess.run([self.git, '-C', self.gitdir, 'rev-parse', 'stable'],
                                capture_output=True,
                                check=True,
                                encoding='utf-8',
                                close_fds=False)
            return sp.stdout.rstrip()

        except subprocess.CalledProcessError as e:
            raise CatalystError(f'{e.cmd} failed with return code'
                                f'{e.returncode}\n'
                                f'{e.output}\n') from e
        finally:
            if pgp_keyring:
                openpgp_env.close()

    def run(self):
        if self.settings['snapshot_treeish'] == 'stable':
            treeish = self.update_ebuild_repo()
        else:
            treeish = self.settings['snapshot_treeish']

        self.set_snapshot(treeish)

        git_cmd = [self.git, '-C', self.gitdir, 'archive', '--format=tar',
                   treeish]
        tar2sqfs_cmd = [command('tar2sqfs'), str(self.snapshot), '-q', '-f',
                        '-j1', '-c', 'gzip']

        log.notice('Creating %s tree snapshot %s from %s',
                   self.settings['repo_name'], treeish, self.gitdir)
        log.notice('>>> ' + ' '.join([*git_cmd, '|']))
        log.notice('    ' + ' '.join(tar2sqfs_cmd))

        with fasteners.InterProcessLock(self.snapshot.with_suffix('.lock')):
            git = subprocess.Popen(git_cmd,
                                   stdout=subprocess.PIPE,
                                   stderr=sys.stderr,
                                   close_fds=False)
            tar2sqfs = subprocess.Popen(tar2sqfs_cmd,
                                        stdin=git.stdout,
                                        stdout=sys.stdout,
                                        stderr=sys.stderr,
                                        close_fds=False)
            git.stdout.close()
            git.wait()
            tar2sqfs.wait()

        if tar2sqfs.returncode == 0:
            log.notice('Wrote snapshot to %s', self.snapshot)
        else:
            log.error('Failed to create snapshot')
        return tar2sqfs.returncode == 0
