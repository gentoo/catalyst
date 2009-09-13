
"""
Builder class for snapshots.
"""

import os
import catalyst
from catalyst.target.generic import generic_target
from catalyst.spawn import cmd
from catalyst.output import *

class snapshot_target(catalyst.target.generic.generic_target):

	def __init__(self):
		generic_target.__init__(self)

		self.required_values = ["version_stamp","target"]
		self.valid_values = ["version_stamp","target"]

	def setup(self):
		self.settings["target_subpath"]="portage"
		st=self.settings["storedir"]
		self.settings["snapshot_path"]=catalyst.util.normpath(st+"/snapshots/portage-"+self.settings["version_stamp"]\
			+".tar.bz2")
		self.settings["tmp_path"]=catalyst.util.normpath(st+"/tmp/"+self.settings["target_subpath"])

		x=catalyst.util.normpath(self.settings["storedir"]+"/snapshots")
		if not os.path.exists(x):
			os.makedirs(x)

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

		catalyst.util.rsync(self.settings["portdir"] + "/", mytmp + "/portage/", delete=True, \
			extra_opts="--exclude /distfiles/ --exclude /local/ --exclude CVS/ --exclude .svn --filter=H_**/files/digest-*")

		msg("Compressing Portage snapshot tarball...")
		cmd("tar cjf "+self.settings["snapshot_path"]+" -C "+mytmp+" portage",\
			"Snapshot creation failure",env=self.env)

		catalyst.hash.gen_contents_file(self.settings["snapshot_path"], self.settings)
		catalyst.hash.gen_digest_file(self.settings["snapshot_path"], self.settings)

		self.cleanup()
		msg("snapshot: complete!")

	def cleanup(self):
		# What is the point of this?
		msg("Cleaning up...")

	def purge(self):
		myemp=self.settings["tmp_path"]
		if os.path.isdir(myemp):
			msg("Emptying directory " + myemp)
			catalyst.util.empty_dir(myemp)

__target_map = {"snapshot":snapshot_target}

# vim: ts=4 sw=4 sta noet sts=4 ai
