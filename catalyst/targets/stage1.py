"""
stage1 target
"""
# NOTE: That^^ docstring has influence catalyst-spec(5) man page generation.

from catalyst import log
from catalyst.support import normpath
from catalyst.fileops import ensure_dirs, move_path
from catalyst.base.stagebase import StageBase


class stage1(StageBase):
	"""
	Builder class for a stage1 installation tarball build.
	"""
	def __init__(self,spec,addlargs):
		self.required_values=[]
		self.valid_values=["chost"]
		self.valid_values.extend(["update_seed","update_seed_command"])
		StageBase.__init__(self,spec,addlargs)

	def set_stage_path(self):
		self.settings["stage_path"]=normpath(self.settings["chroot_path"]+self.settings["root_path"])
		log.notice('stage1 stage path is %s', self.settings['stage_path'])

	def set_root_path(self):
		# sets the root path, relative to 'chroot_path', of the stage1 root
		self.settings["root_path"]=normpath("/tmp/stage1root")
		log.info('stage1 root path is %s', self.settings['root_path'])

	def set_cleanables(self):
		StageBase.set_cleanables(self)
		self.settings["cleanables"].extend([\
		"/usr/share/zoneinfo", self.settings["port_conf"] + "/package*"])

	# XXX: How do these override_foo() functions differ from the ones in StageBase and why aren't they in stage3_target?
	# XXY: It appears the difference is that these functions are actually doing something and the ones in stagebase don't :-(
	# XXZ: I have a wierd suspicion that it's the difference in capitolization

	def override_chost(self):
		if "chost" in self.settings:
			self.settings["CHOST"] = self.settings["chost"]

	def override_common_flags(self):
		if "common_flags" in self.settings:
			self.settings["COMMON_FLAGS"] = self.settings["common_flags"]

	def override_cflags(self):
		if "cflags" in self.settings:
			self.settings["CFLAGS"] = self.settings["cflags"]

	def override_cxxflags(self):
		if "cxxflags" in self.settings:
			self.settings["CXXFLAGS"] = self.settings["cxxflags"]

	def override_fcflags(self):
		if "fcflags" in self.settings:
			self.settings["FCFLAGS"] = self.settings["fcflags"]

	def override_fflags(self):
		if "fflags" in self.settings:
			self.settings["FFLAGS"] = self.settings["fflags"]

	def override_ldflags(self):
		if "ldflags" in self.settings:
			self.settings["LDFLAGS"] = self.settings["ldflags"]

	def set_portage_overlay(self):
		StageBase.set_portage_overlay(self)
		if "portage_overlay" in self.settings:
			log.warning(
				'Using an overlay for earlier stages could cause build issues.\n'
				"If you break it, you buy it.  Don't complain to us about it.\n"
				"Don't say we did not warn you.")

	def base_dirs(self):
		pass

	def set_mounts(self):
		# stage_path/proc probably doesn't exist yet, so create it
		ensure_dirs(self.settings["stage_path"]+"/proc")

		# alter the mount mappings to bind mount proc onto it
		self.mounts.append("stage1root/proc")
		self.target_mounts["stage1root/proc"] = "/tmp/stage1root/proc"
		self.mountmap["stage1root/proc"] = "/proc"

	def set_completion_action_sequences(self):
		'''Override function for stage1

		Its purpose is to move the new stage1root out of the seed stage
		and rename it to the stage1 chroot_path after cleaning the seed stage
		chroot for re-use in stage2 without the need to unpack it.
		'''
		if "fetch" not in self.settings["options"]:
			self.settings["action_sequence"].append("capture")
		if "keepwork" in self.settings["options"]:
			self.settings["action_sequence"].append("clear_autoresume")
		elif "seedcache" in self.settings["options"]:
			self.settings["action_sequence"].append("remove_autoresume")
			self.settings["action_sequence"].append("clean_stage1")
		else:
			self.settings["action_sequence"].append("remove_autoresume")
			self.settings["action_sequence"].append("remove_chroot")


	def clean_stage1(self):
		'''seedcache is enabled, so salvage the /tmp/stage1root,
		remove the seed chroot'''
		log.notice('Salvaging the stage1root from the chroot path ...')
		# move the self.settings["stage_path"] outside of the self.settings["chroot_path"]
		tmp_path = normpath(self.settings["storedir"] + "/tmp/" + "stage1root")
		if move_path(self.settings["stage_path"], tmp_path):
			self.remove_chroot()
			# move it to self.settings["chroot_path"]
			if not move_path(tmp_path, self.settings["chroot_path"]):
				log.error('clean_stage1 failed, see previous log messages for details')
				return False
			log.notice('Successfully moved and cleaned the stage1root for the seedcache')
			return True
		log.error('clean_stage1 failed to move the stage1root to a temporary loation')
		return False
