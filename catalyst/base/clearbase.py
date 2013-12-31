
import os
import shutil
from stat import ST_UID, ST_GID, ST_MODE


from catalyst.support import cmd, countdown
from catalyst.fileops import ensure_dirs, clear_dir

class ClearBase(object):
	"""
	This class does all of clearing after task completion
	"""
	def __init__(self, myspec):
		self.settings = myspec
		self.resume = None


	def clear_autoresume(self):
		""" Clean resume points since they are no longer needed """
		if "autoresume" in self.settings["options"]:
			print "Removing AutoResume Points: ..."
			self.resume.clear_all()


	def remove_autoresume(self):
		""" Rmove all resume points since they are no longer needed """
		if "autoresume" in self.settings["options"]:
			print "Removing AutoResume: ..."
			self.resume.clear_all(remove=True)


	def clear_chroot(self):
		print 'Clearing the chroot path ...'
		clear_dir(self.settings["chroot_path"], 0755, True)


	def remove_chroot(self):
		print 'Removing the chroot path ...'
		clear_dir(self.settings["chroot_path"], 0755, True, remove=True)


	def clear_packages(self, remove=False):
		if "pkgcache" in self.settings["options"]:
			print "purging the pkgcache ..."
			clear_dir(self.settings["pkgcache_path"], remove=remove)


	def clear_kerncache(self, remove=False):
		if "kerncache" in self.settings["options"]:
			print "purging the kerncache ..."
			clear_dir(self.settings["kerncache_path"], remove=remove)


	def purge(self, remove=False):
		countdown(10,"Purging Caches ...")
		if any(k in self.settings["options"] for k in ("purge",
				"purgeonly", "purgetmponly")):
			print "purge(); clearing autoresume ..."
			self.clear_autoresume(remove)

			print "purge(); clearing chroot ..."
			self.clear_chroot(remove)

			if "purgetmponly" not in self.settings["options"]:
				print "purge(); clearing package cache ..."
				self.clear_packages(remove)

			print "purge(); clearing kerncache ..."
			self.clear_kerncache(remove)
