"""
stage3 target, builds upon previous stage2/stage3 tarball
"""
# NOTE: That^^ docstring has influence catalyst-spec(5) man page generation.


from catalyst.base.stagebase import StageBase


class stage3(StageBase):
	"""
	Builder class for a stage3 installation tarball build.
	"""
	def __init__(self,spec,addlargs):
		self.required_values=[]
		self.valid_values=[]
		StageBase.__init__(self,spec,addlargs)

	def set_portage_overlay(self):
		StageBase.set_portage_overlay(self)
		if "portage_overlay" in self.settings:
			print "\nWARNING !!!!!"
			print "\tUsing an overlay for earlier stages could cause build issues."
			print "\tIf you break it, you buy it. Don't complain to us about it."
			print "\tDont say we did not warn you\n"

	def set_cleanables(self):
		StageBase.set_cleanables(self)
