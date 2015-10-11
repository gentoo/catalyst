
import os

from snakeoil import fileutils
from snakeoil import osutils
from catalyst.fileops import ensure_dirs


LockInUse = osutils.LockException


class LockDir(object):
	"""An object that creates locks inside dirs"""

	def __init__(self, lockdir):
		self.gid = 250
		self.lockfile = os.path.join(lockdir, '.catalyst_lock')
		ensure_dirs(lockdir)
		fileutils.touch(self.lockfile, mode=0o664)
		os.chown(self.lockfile, -1, self.gid)
		self.lock = osutils.FsLock(self.lockfile)

	def read_lock(self):
		self.lock.acquire_read_lock()

	def write_lock(self):
		self.lock.acquire_write_lock()

	def unlock(self):
		# Releasing a write lock is the same as a read lock.
		self.lock.release_write_lock()
