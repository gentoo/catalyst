'''fileops.py

Performs file operations such as pack/unpack,
ensuring directories exist,... imports snakeoils osutils
functions for use throughout catalyst.
'''

import glob
import os
import shutil
from stat import ST_UID, ST_GID, ST_MODE

# NOTE: pjoin and listdir_files are imported here for export
# to other catalyst modules
# pylint: disable=unused-import
from snakeoil.osutils import (ensure_dirs as snakeoil_ensure_dirs,
	pjoin, listdir_files)
# pylint: enable=unused-import

from catalyst import log
from catalyst.support import (cmd, CatalystError)


def ensure_dirs(path, gid=-1, uid=-1, mode=0o755, minimal=True,
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
		if mode=0o755, minimal=True, and a directory exists with mode 0707,
		this will restore the missing group perms resulting in 757.
	:param failback: function to run in the event of a failed attemp
		to create the directory.
	:return: True if the directory could be created/ensured to have those
		permissions, False if not.
	'''
	succeeded = snakeoil_ensure_dirs(path, gid=gid, uid=uid, mode=mode, minimal=minimal)
	if not succeeded:
		if failback:
			failback()
		if fatal:
			raise CatalystError(
				"Failed to create directory: %s" % path, print_traceback=True)
	return succeeded


def clear_dir(target, mode=0o755, chg_flags=False, remove=False,
		clear_nondir=True):
	'''Universal directory clearing function

	@target: string, path to be cleared or removed
	@mode: integer, desired mode to set the directory to
	@chg_flags: boolean used for FreeBSD hosts
	@remove: boolean, passed through to clear_dir()
	@return boolean
	'''
	log.debug('start: %s', target)
	if not target:
		log.debug('no target... returning')
		return False

	mystat = None
	if os.path.isdir(target) and not os.path.islink(target):
		log.notice('Emptying directory: %s', target)
		# stat the dir, delete the dir, recreate the dir and set
		# the proper perms and ownership
		try:
			log.debug('os.stat()')
			mystat = os.stat(target)
			# There's no easy way to change flags recursively in python
			if chg_flags and os.uname()[0] == "FreeBSD":
				cmd(['chflags', '-R', 'noschg', target])
			log.debug('shutil.rmtree()')
			shutil.rmtree(target)
		except Exception:
			log.error('clear_dir failed', exc_info=True)
			return False
	elif os.path.exists(target):
		if clear_nondir:
			log.debug("Clearing (unlinking) non-directory: %s", target)
			os.unlink(target)
		else:
			log.info('clear_dir failed: %s: is not a directory', target)
			return False
	else:
		log.debug("Conditions not met to clear: %s", target)
		log.debug("                      isdir: %s", os.path.isdir(target))
		log.debug("                     islink: %s", os.path.islink(target))
		log.debug("                     exists: %s", os.path.exists(target))

	if not remove:
		log.debug('ensure_dirs()')
		ensure_dirs(target, mode=mode)
		if mystat:
			os.chown(target, mystat[ST_UID], mystat[ST_GID])
			os.chmod(target, mystat[ST_MODE])

	log.debug('DONE, returning True')
	return True


def clear_path(target_path):
	"""Nuke |target_path| regardless of it being a dir, file or glob."""
	targets = glob.glob(target_path)
	for path in targets:
		clear_dir(path, remove=True)


def move_path(src, dest):
	'''Move a source target to a new destination

	:param src: source path to move
	:param dest: destination path to move it to
	:returns: boolean
	'''
	log.debug('Start move_path(%s, %s)', src, dest)
	if os.path.isdir(src) and not os.path.islink(src):
		if os.path.exists(dest):
			log.warning('Removing existing target destination: %s', dest)
			if not clear_dir(dest, remove=True):
				return False
		log.debug('Moving source...')
		try:
			shutil.move(src, dest)
		except Exception:
			log.error('move_path failed', exc_info=True)
			return False
		return True
	return False
