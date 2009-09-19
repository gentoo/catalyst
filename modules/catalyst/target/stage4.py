
"""
Builder class for stage4.
"""

from generic_stage import *

class stage4_target(generic_stage_target):

	depends = ('system', 'stage3')

	def __init__(self):
		generic_stage_target.__init__(self)

		self.required_values=["stage4/packages"]
		self.valid_values=self.required_values[:]
		self.valid_values.extend(["stage4/use","boot/kernel",\
				"stage4/root_overlay","stage4/fsscript",\
				"stage4/gk_mainargs","splash_theme",\
				"portage_overlay","stage4/rcadd","stage4/rcdel",\
				"stage4/linuxrc","stage4/unmerge","stage4/rm","stage4/empty"])

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
#			not "FETCH" in self.settings:
		if not "FETCH" in self.settings:
			self.settings["action_sequence"].append("capture")
		self.settings["action_sequence"].append("clear_autoresume")

__target_map = { "stage4": stage4_target }

# vim: ts=4 sw=4 sta noet sts=4 ai
