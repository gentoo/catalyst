
import os
import shutil
from stat import ST_UID, ST_GID, ST_MODE


from catalyst.support import cmd, countdown
from catalyst.fileops import ensure_dirs

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


	def clear_chroot(self):
		print 'Clearing the chroot path ...'
		self.clear_dir(self.settings["chroot_path"], 0755, True)


	def clear_packages(self):
		if "pkgcache" in self.settings["options"]:
			print "purging the pkgcache ..."
			self.clear_dir(self.settings["pkgcache_path"])


	def clear_kerncache(self):
		if "kerncache" in self.settings["options"]:
			print "purging the kerncache ..."
			self.clear_dir(self.settings["kerncache_path"])


	def purge(self):
		countdown(10,"Purging Caches ...")
		if any(k in self.settings["options"] for k in ("purge","purgeonly","purgetmponly")):
			print "purge(); clearing autoresume ..."
			self.clear_autoresume()

			print "purge(); clearing chroot ..."
			self.clear_chroot()

			if "purgetmponly" not in self.settings["options"]:
				print "purge(); clearing package cache ..."
				self.clear_packages()

			print "purge(); clearing kerncache ..."
			self.clear_kerncache()


	def clear_dir(self, myemp, mode=0755, chg_flags=False):
		'''Universal directory clearing function
		'''
		if not myemp:
			return False
		if os.path.isdir(myemp):
			print "Emptying directory" , myemp
			"""
			stat the dir, delete the dir, recreate the dir and set
			the proper perms and ownership
			"""
			try:
				mystat=os.stat(myemp)
				""" There's no easy way to change flags recursively in python """
				if chg_flags and os.uname()[0] == "FreeBSD":
					os.system("chflags -R noschg " + myemp)
				shutil.rmtree(myemp)
				ensure_dirs(myemp, mode=mode)
				os.chown(myemp,mystat[ST_UID],mystat[ST_GID])
				os.chmod(myemp,mystat[ST_MODE])
			except Exception as e:
				print CatalystError("clear_dir(); Exeption: %s" % str(e))
				return False
			return True
