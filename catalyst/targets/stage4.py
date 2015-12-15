"""
stage4 target, builds upon previous stage3/stage4 tarball
"""
# NOTE: That^^ docstring has influence catalyst-spec(5) man page generation.

from catalyst.base.stagebase import StageBase


class stage4(StageBase):
	"""
	Builder class for stage4.
	"""
	def __init__(self,spec,addlargs):
		self.required_values=["stage4/packages"]
		self.valid_values=self.required_values[:]
		self.valid_values.extend(["stage4/use", "boot/kernel",
			"stage4/root_overlay", "stage4/fsscript",
			"stage4/gk_mainargs", "splash_theme",
			"portage_overlay", "stage4/rcadd", "stage4/rcdel",
			"stage4/linuxrc", "stage4/unmerge", "stage4/rm", "stage4/empty"])
		StageBase.__init__(self,spec,addlargs)

	def set_cleanables(self):
		self.settings["cleanables"]=["/var/tmp/*","/tmp/*"]

	def set_action_sequence(self):
		self.settings["action_sequence"] = ["unpack", "unpack_snapshot",
			"config_profile_link", "setup_confdir", "portage_overlay",
			"bind", "chroot_setup", "setup_environment", "build_packages",
			"build_kernel", "bootloader", "root_overlay", "fsscript",
			"preclean", "rcupdate", "unmerge", "unbind", "remove", "empty",
			"clean"]
		self.set_completion_action_sequences()
