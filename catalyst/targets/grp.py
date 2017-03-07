"""
Gentoo Reference Platform (GRP) target
"""
# NOTE: That^^ docstring has influence catalyst-spec(5) man page generation.

import os
import glob

from catalyst import log
from catalyst.support import (CatalystError, normpath, cmd)
from catalyst.base.stagebase import StageBase


class grp(StageBase):
	"""
	The builder class for GRP (Gentoo Reference Platform) builds.
	"""
	def __init__(self,spec,addlargs):
		self.required_values=["version_stamp","target","subarch",\
			"rel_type","profile","snapshot","source_subpath"]

		self.valid_values=self.required_values[:]
		self.valid_values.extend(["grp/use"])
		if "grp" not in addlargs:
			raise CatalystError("Required value \"grp\" not specified in spec.")

		self.required_values.extend(["grp"])
		if isinstance(addlargs['grp'], str):
			addlargs["grp"]=[addlargs["grp"]]

		if "grp/use" in addlargs:
			if isinstance(addlargs['grp/use'], str):
				addlargs["grp/use"]=[addlargs["grp/use"]]

		for x in addlargs["grp"]:
			self.required_values.append("grp/"+x+"/packages")
			self.required_values.append("grp/"+x+"/type")

		StageBase.__init__(self,spec,addlargs)

	def run_local(self):
		for pkgset in self.settings["grp"]:
			# example call: "grp.sh run pkgset cd1 xmms vim sys-apps/gleep"
			try:
				cmd([self.settings['controller_file'], 'run',
					self.settings['grp/' + pkgset + '/type'],
					pkgset] + self.settings['grp/' + pkgset + '/packages'],
					env=self.env)

			except CatalystError:
				self.unbind()
				raise CatalystError("GRP build aborting due to error.",
					print_traceback=True)

	def set_mounts(self):
		self.mounts.append("/tmp/grp")
		self.mountmap["/tmp/grp"]=self.settings["target_path"]

	def generate_digests(self):
		for pkgset in self.settings["grp"]:
			if self.settings["grp/"+pkgset+"/type"] == "pkgset":
				destdir=normpath(self.settings["target_path"]+"/"+pkgset+"/All")
				log.notice('Digesting files in the pkgset...')
				digests=glob.glob(destdir+'/*.DIGESTS')
				for i in digests:
					if os.path.exists(i):
						os.remove(i)

				files=os.listdir(destdir)
				#ignore files starting with '.' using list comprehension
				files=[filename for filename in files if filename[0] != '.']
				for i in files:
					if os.path.isfile(normpath(destdir+"/"+i)):
						self.gen_contents_file(normpath(destdir+"/"+i))
						self.gen_digest_file(normpath(destdir+"/"+i))
			else:
				destdir=normpath(self.settings["target_path"]+"/"+pkgset)
				log.notice('Digesting files in the srcset...')

				digests=glob.glob(destdir+'/*.DIGESTS')
				for i in digests:
					if os.path.exists(i):
						os.remove(i)

				files=os.listdir(destdir)
				#ignore files starting with '.' using list comprehension
				files=[filename for filename in files if filename[0] != '.']
				for i in files:
					if os.path.isfile(normpath(destdir+"/"+i)):
						#self.gen_contents_file(normpath(destdir+"/"+i))
						self.gen_digest_file(normpath(destdir+"/"+i))

	def set_action_sequence(self):
		self.settings["action_sequence"]=["unpack","unpack_snapshot",\
					"config_profile_link","setup_confdir","portage_overlay","bind","chroot_setup",\
					"setup_environment","run_local","unbind",\
					"generate_digests","clear_autoresume"]
