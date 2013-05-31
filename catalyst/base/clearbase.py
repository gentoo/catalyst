
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



	def clear_autoresume(self):
		""" Clean resume points since they are no longer needed """
		if "autoresume" in self.settings["options"]:
			print "Removing AutoResume Points: ..."
		myemp=self.settings["autoresume_path"]
		if os.path.isdir(myemp):
				if "autoresume" in self.settings["options"]:
					print "Emptying directory",myemp
				"""
				stat the dir, delete the dir, recreate the dir and set
				the proper perms and ownership
				"""
				mystat=os.stat(myemp)
				if os.uname()[0] == "FreeBSD":
					cmd("chflags -R noschg "+myemp,\
						"Could not remove immutable flag for file "\
						+myemp)
				#cmd("rm -rf "+myemp, "Could not remove existing file: "+myemp,env-self.env)
				shutil.rmtree(myemp)
				ensure_dirs(myemp, 0755)
				os.chown(myemp,mystat[ST_UID],mystat[ST_GID])
				os.chmod(myemp,mystat[ST_MODE])


	def clear_chroot(self):
		myemp=self.settings["chroot_path"]
		if os.path.isdir(myemp):
			print "Emptying directory",myemp
			"""
			stat the dir, delete the dir, recreate the dir and set
			the proper perms and ownership
			"""
			mystat=os.stat(myemp)
			#cmd("rm -rf "+myemp, "Could not remove existing file: "+myemp,env=self.env)
			""" There's no easy way to change flags recursively in python """
			if os.uname()[0] == "FreeBSD":
				os.system("chflags -R noschg "+myemp)
			shutil.rmtree(myemp)
			ensure_dirs(myemp, mode=0755)
			os.chown(myemp,mystat[ST_UID],mystat[ST_GID])
			os.chmod(myemp,mystat[ST_MODE])


	def clear_packages(self):
		if "pkgcache" in self.settings["options"]:
			print "purging the pkgcache ..."

			myemp=self.settings["pkgcache_path"]
			if os.path.isdir(myemp):
				print "Emptying directory",myemp
				"""
				stat the dir, delete the dir, recreate the dir and set
				the proper perms and ownership
				"""
				mystat=os.stat(myemp)
				#cmd("rm -rf "+myemp, "Could not remove existing file: "+myemp,env=self.env)
				shutil.rmtree(myemp)
				ensure_dirs(myemp, mode=0755)
				os.chown(myemp,mystat[ST_UID],mystat[ST_GID])
				os.chmod(myemp,mystat[ST_MODE])


	def clear_kerncache(self):
		if "kerncache" in self.settings["options"]:
			print "purging the kerncache ..."

			myemp=self.settings["kerncache_path"]
			if os.path.isdir(myemp):
				print "Emptying directory",myemp
				"""
				stat the dir, delete the dir, recreate the dir and set
				the proper perms and ownership
				"""
				mystat=os.stat(myemp)
				#cmd("rm -rf "+myemp, "Could not remove existing file: "+myemp,env=self.env)
				shutil.rmtree(myemp)
				ensure_dirs(myemp, mode=0755)
				os.chown(myemp,mystat[ST_UID],mystat[ST_GID])
				os.chmod(myemp,mystat[ST_MODE])


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

