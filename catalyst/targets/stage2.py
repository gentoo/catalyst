"""
stage2 target, builds upon previous stage1 tarball
"""
# NOTE: That^^ docstring has influence catalyst-spec(5) man page generation.


from catalyst import log
from catalyst.base.stagebase import StageBase


class stage2(StageBase):
	"""
	Builder class for a stage2 installation tarball build.
	"""
	def __init__(self,spec,addlargs):
		self.required_values=[]
		self.valid_values=["chost"]
		StageBase.__init__(self,spec,addlargs)

	# XXX: How do these override_foo() functions differ from the ones in
	# StageBase and why aren't they in stage3_target?

	def override_chost(self):
		if "chost" in self.settings:
			self.settings["CHOST"] = self.settings["chost"]

	def override_cflags(self):
		if "cflags" in self.settings:
			self.settings["CFLAGS"] = self.settings["cflags"]

	def override_cxxflags(self):
		if "cxxflags" in self.settings:
			self.settings["CXXFLAGS"] = self.settings["cxxflags"]

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
