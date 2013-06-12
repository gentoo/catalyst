
# Maintained in full by:
# Catalyst Team <catalyst@gentoo.org>
# Release Engineering Team <releng@gentoo.org>

'''fileops.py

Performs file operations such as pack/unpack,
ensuring directories exist,... imports snakeoils osutils
functions for use throughout catalyst.
'''

from snakeoil.osutils import (ensure_dirs as snakeoil_ensure_dirs, normpath,
	pjoin, listdir_files)
from catalyst.support import CatalystError


def ensure_dirs(path, gid=-1, uid=-1, mode=0777, minimal=True,
		failback=None, fatal=False):
	'''Wrapper to snakeoil.osutil's ensure_dirs()
	This additionally allows for failures to run
	cleanup or other code and/or raise fatal errors.

	:param path: directory to ensure exists on disk
	:param gid: a valid GID to set any created directories to
	:param uid: a valid UID to set any created directories to
	:param mode: permissions to set any created directories to
	:param minimal: boolean controlling whether or not the specified mode
		must be enforced, or is the minimal permissions necessary.  For example,
		if mode=0755, minimal=True, and a directory exists with mode 0707,
		this will restore the missing group perms resulting in 757.
	:param failback: function to run in the event of a failed attemp
		to create the directory.
	:return: True if the directory could be created/ensured to have those
		permissions, False if not.
	'''
	succeeded = snakeoil_ensure_dirs(path, gid=-1, uid=-1, mode=0777, minimal=True)
	if not succeeded:
		if failback:
			failback()
		if fatal:
			raise CatalystError(
				"Failed to create directory: %s" % path, print_traceback=True)
	return succeeded
