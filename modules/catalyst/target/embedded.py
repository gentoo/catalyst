
"""
This class works like a 'stage3'.  A stage2 tarball is unpacked, but instead
of building a stage3, it emerges a 'system' into another directory
inside the 'stage2' system.  This way we do not have to emerge gcc/portage
into the staged system.

It sounds real complicated but basically it runs
ROOT=/tmp/submerge emerge --blahblah foo bar
"""

from generic_stage import *
import catalyst.util

class embedded_target(generic_stage_target):

	def __init__(self,spec,addlargs):
		self.required_values=[]
		self.valid_values=[]
		self.valid_values.extend(["embedded/empty","embedded/rm","embedded/unmerge","embedded/fs-prepare","embedded/fs-finish","embedded/mergeroot","embedded/packages","embedded/fs-type","embedded/runscript","boot/kernel","embedded/linuxrc"])
		self.valid_values.extend(["embedded/use"])
		if "embedded/fs-type" in addlargs:
			self.valid_values.append("embedded/fs-ops")

		generic_stage_target.__init__(self,spec,addlargs)
		self.set_build_kernel_vars()

	def set_action_sequence(self):
		self.settings["action_sequence"]=["dir_setup","unpack","unpack_snapshot",\
					"config_profile_link","setup_confdir",\
					"portage_overlay","bind","chroot_setup",\
					"setup_environment","build_kernel","build_packages",\
					"bootloader","root_overlay","fsscript","unmerge",\
					"unbind","remove","empty","clean","capture","clear_autoresume"]

	def set_stage_path(self):
		self.settings["stage_path"]=catalyst.util.normpath(self.settings["chroot_path"]+"/tmp/mergeroot")
		print "embedded stage path is "+self.settings["stage_path"]

	def set_root_path(self):
		self.settings["root_path"]=catalyst.util.normpath("/tmp/mergeroot")
		print "embedded root path is "+self.settings["root_path"]

__target_map = {"embedded":embedded_target}
