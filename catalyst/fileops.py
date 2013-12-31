
# Maintained in full by:
# Catalyst Team <catalyst@gentoo.org>
# Release Engineering Team <releng@gentoo.org>

'''fileops.py

Performs file operations such as pack/unpack,
ensuring directories exist,... imports snakeoils osutils
functions for use throughout catalyst.
'''

import os
import shutil
from stat import ST_UID, ST_GID, ST_MODE

# NOTE: pjoin and listdir_files are imported here for export
# to other catalyst modules
from snakeoil.osutils import (ensure_dirs as snakeoil_ensure_dirs,
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


def clear_dir(target, mode=0755, chg_flags=False, remove=False):
	'''Universal directory clearing function

	@target: string, path to be cleared or removed
	@mode: integer, desired mode to set the directory to
	@chg_flags: boolean used for FreeBSD hoosts
	@remove: boolean, passed through to clear_dir()
	@return boolean
	'''
	#print "fileops.clear_dir()"
	if not target:
		#print "fileops.clear_dir(), no target... returning"
		return False
	if os.path.isdir(target):
		print "Emptying directory" , target
		"""
		stat the dir, delete the dir, recreate the dir and set
		the proper perms and ownership
		"""
		try:
			#print "fileops.clear_dir(), os.stat()"
			mystat=os.stat(target)
			""" There's no easy way to change flags recursively in python """
			if chg_flags and os.uname()[0] == "FreeBSD":
				os.system("chflags -R noschg " + target)
			#print "fileops.clear_dir(), shutil.rmtree()"
			shutil.rmtree(target)
			if not remove:
				#print "fileops.clear_dir(), ensure_dirs()"
				ensure_dirs(target, mode=mode)
				os.chown(target, mystat[ST_UID], mystat[ST_GID])
				os.chmod(target, mystat[ST_MODE])
		except Exception as e:
			print CatalystError("clear_dir(); Exeption: %s" % str(e))
			return False
	else:
		print "fileops.clear_dir(), %s is not a directory" % (target)
	#print "fileops.clear_dir(), DONE, returning True"
	return True
