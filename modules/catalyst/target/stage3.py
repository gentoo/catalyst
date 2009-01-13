
"""
Builder class for a stage3 installation tarball build.
"""

from generic_stage import *

class stage3_target(generic_stage_target):

	def __init__(self):
		generic_stage_target.__init__(self)

		self.required_values=[]
		self.valid_values=[]

	def set_portage_overlay(self):
		generic_stage_target.set_portage_overlay(self)
		if "portage_overlay" in self.settings:
			msg()
			msg("WARNING !!!!!")
			msg("\tUsing an overlay for earlier stages could cause build issues.")
			msg("\tIf you break it, you buy it. Don't complain to us about it.")
			msg("\tDont say we did not warn you")
			msg()

	def set_cleanables(self):
		generic_stage_target.set_cleanables(self)
		self.settings["cleanables"].extend(["/etc/portage"])

__target_map = {"stage3":stage3_target}
