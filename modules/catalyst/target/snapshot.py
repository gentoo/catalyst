
"""
Builder class for snapshots.
"""

import os
from generic_stage import *
import catalyst
from catalyst.spawn import cmd
from catalyst.output import *

class snapshot_target(generic_target):
	def __init__(self,myspec,addlargs):
		self.required_values=["version_stamp","target"]
		self.valid_values=["version_stamp","target"]

		generic_target.__init__(self)
#		self.settings=myspec
		self.settings["target_subpath"]="portage"
		st=self.settings["storedir"]
		self.settings["snapshot_path"]=catalyst.util.normpath(st+"/snapshots/portage-"+self.settings["version_stamp"]\
			+".tar.bz2")
		self.settings["tmp_path"]=catalyst.util.normpath(st+"/tmp/"+self.settings["target_subpath"])

	def setup(self):
		x=catalyst.util.normpath(self.settings["storedir"]+"/snapshots")
		if not os.path.exists(x):
			os.makedirs(x)

	def mount_safety_check(self):
		pass

	def run(self):
		if "PURGEONLY" in self.settings:
			self.purge()
			return

		if "PURGE" in self.settings:
			self.purge()

		self.setup()
		msg("Creating Portage tree snapshot " + self.settings["version_stamp"] + \
			" from " + self.settings["portdir"] + "...")

		mytmp=self.settings["tmp_path"]
		if not os.path.exists(mytmp):
			os.makedirs(mytmp)

		cmd("rsync -a --delete --exclude /packages/ --exclude /distfiles/ --exclude /local/ --exclude CVS/ --exclude .svn --filter=H_**/files/digest-* "+\
			self.settings["portdir"]+"/ "+mytmp+"/portage/","Snapshot failure",env=self.env)

		msg("Compressing Portage snapshot tarball...")
		cmd("tar cjf "+self.settings["snapshot_path"]+" -C "+mytmp+" portage",\
			"Snapshot creation failure",env=self.env)

		catalyst.hash.gen_contents_file(self.settings["snapshot_path"], self.settings)
		catalyst.hash.gen_digest_file(self.settings["snapshot_path"], self.settings)

		self.cleanup()
		msg("snapshot: complete!")

	def kill_chroot_pids(self):
		pass

	def cleanup(self):
		msg("Cleaning up...")

	def purge(self):
		myemp=self.settings["tmp_path"]
		if os.path.isdir(myemp):
			msg("Emptying directory " + myemp)
			"""
			stat the dir, delete the dir, recreate the dir and set
			the proper perms and ownership
			"""
			mystat=os.stat(myemp)
			""" There's no easy way to change flags recursively in python """
			if os.uname()[0] == "FreeBSD":
				os.system("chflags -R noschg "+myemp)
			shutil.rmtree(myemp)
			os.makedirs(myemp,0755)
			os.chown(myemp,mystat[ST_UID],mystat[ST_GID])
			os.chmod(myemp,mystat[ST_MODE])

__target_map = {"snapshot":snapshot_target}
