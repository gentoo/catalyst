

from catalyst import log
from catalyst.support import countdown
from catalyst.fileops import clear_dir

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
			log.notice('Removing AutoResume Points ...')
			self.resume.clear_all()


	def remove_autoresume(self):
		""" Rmove all resume points since they are no longer needed """
		if "autoresume" in self.settings["options"]:
			log.notice('Removing AutoResume ...')
			self.resume.clear_all(remove=True)


	def clear_chroot(self):
		self.chroot_lock.unlock()
		log.notice('Clearing the chroot path ...')
		clear_dir(self.settings["chroot_path"], 0o755, True)


	def remove_chroot(self):
		self.chroot_lock.unlock()
		log.notice('Removing the chroot path ...')
		clear_dir(self.settings["chroot_path"], 0o755, True, remove=True)


	def clear_packages(self, remove=False):
		if "pkgcache" in self.settings["options"]:
			log.notice('purging the pkgcache ...')
			clear_dir(self.settings["pkgcache_path"], remove=remove)


	def clear_kerncache(self, remove=False):
		if "kerncache" in self.settings["options"]:
			log.notice('purging the kerncache ...')
			clear_dir(self.settings["kerncache_path"], remove=remove)


	def purge(self, remove=False):
		countdown(10,"Purging Caches ...")
		if any(k in self.settings["options"] for k in ("purge",
				"purgeonly", "purgetmponly")):
			log.notice('purge(); clearing autoresume ...')
			self.clear_autoresume()

			log.notice('purge(); clearing chroot ...')
			self.clear_chroot()

			if "purgetmponly" not in self.settings["options"]:
				log.notice('purge(); clearing package cache ...')
				self.clear_packages(remove)

			log.notice('purge(); clearing kerncache ...')
			self.clear_kerncache(remove)
