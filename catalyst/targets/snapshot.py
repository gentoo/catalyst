"""
Snapshot target
"""

import os
import shutil
from stat import ST_UID, ST_GID, ST_MODE

from DeComp.compress import CompressMap

from catalyst import log
from catalyst.support import normpath, cmd
from catalyst.base.targetbase import TargetBase
from catalyst.base.genbase import GenBase
from catalyst.fileops import ensure_dirs


class snapshot(TargetBase, GenBase):
	"""
	Builder class for snapshots.
	"""
	def __init__(self,myspec,addlargs):
		self.required_values=["version_stamp","target"]
		self.valid_values=["version_stamp","target", "compression_mode"]

		TargetBase.__init__(self, myspec, addlargs)
		GenBase.__init__(self,myspec)
		#self.settings=myspec
		self.settings["target_subpath"]="portage"
		st=self.settings["storedir"]
		self.settings["snapshot_path"] = normpath(st + "/snapshots/"
			+ self.settings["snapshot_name"]
			+ self.settings["version_stamp"])
		self.settings["tmp_path"]=normpath(st+"/tmp/"+self.settings["target_subpath"])

	def setup(self):
		x=normpath(self.settings["storedir"]+"/snapshots")
		ensure_dirs(x)

	def mount_safety_check(self):
		pass

	def run(self):
		if "purgeonly" in self.settings["options"]:
			self.purge()
			return True

		if "purge" in self.settings["options"]:
			self.purge()

		success = True
		self.setup()
		log.notice('Creating Portage tree snapshot %s from %s ...',
			self.settings['version_stamp'], self.settings['portdir'])

		mytmp=self.settings["tmp_path"]
		ensure_dirs(mytmp)

		target_snapshot = self.settings["portdir"] + "/ " + mytmp + "/%s/" % self.settings["repo_name"]
		cmd("rsync -a --no-o --no-g --delete --exclude /packages/ --exclude /distfiles/ " +
			"--exclude /local/ --exclude CVS/ --exclude .svn --filter=H_**/files/digest-* " +
			target_snapshot, env=self.env)

		log.notice('Compressing Portage snapshot tarball ...')
		compressor = CompressMap(self.settings["compress_definitions"],
			env=self.env, default_mode=self.settings['compression_mode'],
			comp_prog=self.settings["comp_prog"])
		infodict = compressor.create_infodict(
			source=self.settings["repo_name"],
			destination=self.settings["snapshot_path"],
			basedir=mytmp,
			filename=self.settings["snapshot_path"],
			mode=self.settings["compression_mode"],
			auto_extension=True
			)
		if not compressor.compress(infodict):
			success = False
			log.error('Snapshot compression failure')
		else:
			filename = '.'.join([self.settings["snapshot_path"],
				compressor.extension(self.settings["compression_mode"])])
			log.notice('Snapshot successfully written to %s', filename)
			self.gen_contents_file(filename)
			self.gen_digest_file(filename)

		self.cleanup()
		if success:
			log.info('snapshot: complete!')
		return success

	def kill_chroot_pids(self):
		pass

	@staticmethod
	def cleanup():
		log.info('Cleaning up ...')

	def purge(self):
		myemp=self.settings["tmp_path"]
		if os.path.isdir(myemp):
			log.notice('Emptying directory %s', myemp)
			# stat the dir, delete the dir, recreate the dir and set
			# the proper perms and ownership
			mystat=os.stat(myemp)
			# There's no easy way to change flags recursively in python
			if os.uname()[0] == "FreeBSD":
				os.system("chflags -R noschg "+myemp)
			shutil.rmtree(myemp)
			ensure_dirs(myemp, mode=0o755)
			os.chown(myemp,mystat[ST_UID],mystat[ST_GID])
			os.chmod(myemp,mystat[ST_MODE])
