"""
stage4 target, builds upon previous stage3/stage4 tarball
"""
# NOTE: That^^ docstring has influence catalyst-spec(5) man page generation.

from catalyst.base.stagebase import StageBase


class stage4_target(StageBase):
	"""
	Builder class for stage4.
	"""
	def __init__(self,spec,addlargs):
		self.required_values=["stage4/packages"]
		self.valid_values=self.required_values[:]
		self.valid_values.extend(["stage4/use","boot/kernel",\
				"stage4/root_overlay","stage4/fsscript",\
				"stage4/gk_mainargs","splash_theme",\
				"portage_overlay","stage4/rcadd","stage4/rcdel",\
				"stage4/linuxrc","stage4/unmerge","stage4/rm","stage4/empty"])
		StageBase.__init__(self,spec,addlargs)

	def set_cleanables(self):
		self.settings["cleanables"]=["/var/tmp/*","/tmp/*"]

	def set_action_sequence(self):
		self.settings["action_sequence"]=["unpack","unpack_snapshot",\
					"config_profile_link","setup_confdir","portage_overlay",\
					"bind","chroot_setup","setup_environment","build_packages",\
					"build_kernel","bootloader","root_overlay","fsscript",\
					"preclean","rcupdate","unmerge","unbind","remove","empty",\
					"clean"]

#		if "TARBALL" in self.settings or \
#			"fetch" not in self.settings['options']:
		if "fetch" not in self.settings['options']:
			self.settings["action_sequence"].append("capture")
		self.settings["action_sequence"].append("clear_autoresume")

def register(foo):
	foo.update({"stage4":stage4_target})
	return foo

