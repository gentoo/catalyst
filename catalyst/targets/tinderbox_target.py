"""
Tinderbox target
"""
# NOTE: That^^ docstring has influence catalyst-spec(5) man page generation.

import os

from catalyst.support import cmd, list_bashify, CatalystError
from catalyst.base.stagebase import StageBase


class tinderbox_target(StageBase):
	"""
	Builder class for the tinderbox target
	"""
	def __init__(self,spec,addlargs):
		self.required_values=["tinderbox/packages"]
		self.valid_values=self.required_values[:]
		self.valid_values.extend(["tinderbox/use"])
		StageBase.__init__(self,spec,addlargs)

	def run_local(self):
		# tinderbox
		# example call: "grp.sh run xmms vim sys-apps/gleep"
		try:
			if os.path.exists(self.settings["controller_file"]):
			    cmd(self.settings["controller_file"]+" run "+\
				list_bashify(self.settings["tinderbox/packages"]),"run script failed.",env=self.env)

		except CatalystError:
			self.unbind()
			raise CatalystError,"Tinderbox aborting due to error."

	def set_cleanables(self):
		self.settings['cleanables'] = [
			'/etc/resolv.conf',
			'/var/tmp/*',
			'/root/*',
			self.settings['portdir'],
			]

	def set_action_sequence(self):
		#Default action sequence for run method
		self.settings["action_sequence"]=["unpack","unpack_snapshot",\
		              "config_profile_link","setup_confdir","bind","chroot_setup",\
		              "setup_environment","run_local","preclean","unbind","clean",\
		              "clear_autoresume"]
