"""
stage3 target, builds upon previous stage2/stage3 tarball
"""
# NOTE: That^^ docstring has influence catalyst-spec(5) man page generation.

from catalyst import log
from catalyst.base.stagebase import StageBase


class stage3(StageBase):
	"""
	Builder class for a stage3 installation tarball build.
	"""
	required_values = frozenset()
	valid_values = frozenset()

	def __init__(self,spec,addlargs):
		StageBase.__init__(self,spec,addlargs)

	def set_portage_overlay(self):
		StageBase.set_portage_overlay(self)
		if "portage_overlay" in self.settings:
			log.warning(
				'Using an overlay for earlier stages could cause build issues.\n'
				"If you break it, you buy it.  Don't complain to us about it.\n"
				"Don't say we did not warn you.")

	def set_cleanables(self):
		StageBase.set_cleanables(self)
