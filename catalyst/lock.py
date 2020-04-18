
import os

from contextlib import contextmanager

from snakeoil import fileutils
from snakeoil import osutils
from catalyst.fileops import ensure_dirs


LockInUse = osutils.LockException

class Lock:
    """
    A fnctl-based filesystem lock
    """
    def __init__(self, lockfile):
        fileutils.touch(lockfile, mode=0o664)
        os.chown(lockfile, uid=-1, gid=250)
        self.lock = osutils.FsLock(lockfile)

    def read_lock(self):
        self.lock.acquire_read_lock()

    def write_lock(self):
        self.lock.acquire_write_lock()

    def unlock(self):
        # Releasing a write lock is the same as a read lock.
        self.lock.release_write_lock()

class LockDir(Lock):
    """
    A fnctl-based filesystem lock in a directory
    """
    def __init__(self, lockdir):
        ensure_dirs(lockdir)
        lockfile = os.path.join(lockdir, '.catalyst_lock')

        Lock.__init__(self, lockfile)

@contextmanager
def read_lock(filename):
    lock = Lock(filename)
    lock.read_lock()
    try:
        yield
    finally:
        lock.unlock()

@contextmanager
def write_lock(filename):
    lock = Lock(filename)
    lock.write_lock()
    try:
        yield
    finally:
        lock.unlock()
