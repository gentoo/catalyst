"""
Snapshot target
"""

import os
import shutil
from stat import ST_UID, ST_GID, ST_MODE


from catalyst.support import normpath, cmd
from generic_stage_target import generic_stage_target

class snapshot_target(generic_stage_target):
	"""
	Builder class for snapshots.
	"""
	def __init__(self,myspec,addlargs):
		self.required_values=["version_stamp","target"]
		self.valid_values=["version_stamp","target"]

		generic_stage_target.__init__(self,myspec,addlargs)
		self.settings=myspec
		self.settings["target_subpath"]="portage"
		st=self.settings["storedir"]
		self.settings["snapshot_path"]=normpath(st + "/snapshots/"
			+ self.settings["snapshot_name"]
			+ self.settings["version_stamp"] + ".tar.bz2")
		self.settings["tmp_path"]=normpath(st+"/tmp/"+self.settings["target_subpath"])

	def setup(self):
		x=normpath(self.settings["storedir"]+"/snapshots")
		if not os.path.exists(x):
			os.makedirs(x)

	def mount_safety_check(self):
		pass

	def run(self):
		if "purgeonly" in self.settings["options"]:
			self.purge()
			return

		if "purge" in self.settings["options"]:
			self.purge()

		self.setup()
		print "Creating Portage tree snapshot "+self.settings["version_stamp"]+\
			" from "+self.settings["portdir"]+"..."

		mytmp=self.settings["tmp_path"]
		if not os.path.exists(mytmp):
			os.makedirs(mytmp)

		cmd("rsync -a --delete --exclude /packages/ --exclude /distfiles/ " +
			"--exclude /local/ --exclude CVS/ --exclude .svn --filter=H_**/files/digest-* " +
			self.settings["portdir"] + "/ " + mytmp + "/%s/" % self.settings["repo_name"],
			"Snapshot failure",env=self.env)

		print "Compressing Portage snapshot tarball..."
		cmd("tar -I lbzip2 -cf " + self.settings["snapshot_path"] + " -C " +
			mytmp + " %s" % self.settings["repo_name"],
			"Snapshot creation failure",env=self.env)

		self.gen_contents_file(self.settings["snapshot_path"])
		self.gen_digest_file(self.settings["snapshot_path"])

		self.cleanup()
		print "snapshot: complete!"

	def kill_chroot_pids(self):
		pass

	def cleanup(self):
		print "Cleaning up..."

	def purge(self):
		myemp=self.settings["tmp_path"]
		if os.path.isdir(myemp):
			print "Emptying directory",myemp
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

def register(foo):
	foo.update({"snapshot":snapshot_target})
	return foo
