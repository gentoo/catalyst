
"""
The builder class for GRP (Gentoo Reference Platform) builds.
"""

import os, glob
from generic_stage import *
import catalyst
from catalyst.error import *
from catalyst.spawn import cmd
from catalyst.output import *

class grp_target(generic_stage_target):

	depends = ('system', 'stage3')

	def __init__(self):
		generic_stage_target.__init__(self)

		self.required_values=["version_stamp","target","subarch",\
			"rel_type","profile","snapshot","source_subpath"]

		self.valid_values=self.required_values[:]
		self.valid_values.extend(["grp/use"])
		if not "grp" in self.settings:
			raise CatalystError,"Required value \"grp\" not specified in spec."

		self.required_values.extend(["grp"])
		if isinstance(self.settings["grp"], str):
			self.settings["grp"]=[self.settings["grp"]]

		if "grp/use" in self.settings:
		    if isinstance(self.settings["grp/use"], str):
			    self.settings["grp/use"]=[self.settings["grp/use"]]

		for x in self.settings["grp"]:
			self.required_values.append("grp/"+x+"/packages")
			self.required_values.append("grp/"+x+"/type")

	def set_target_path(self):
		self.settings["target_path"]=catalyst.util.normpath(self.settings["storedir"]+"/builds/"+self.settings["target_subpath"]+"/")
		if self.check_autoresume("setup_target_path"):
			msg("Resume point detected, skipping target path setup operation...")
		else:
			# first clean up any existing target stuff
			#if os.path.isdir(self.settings["target_path"]):
				#cmd("rm -rf "+self.settings["target_path"],
				#"Could not remove existing directory: "+self.settings["target_path"],env=self.env)
			if not os.path.exists(self.settings["target_path"]):
				os.makedirs(self.settings["target_path"])

			self.set_autoresume("setup_target_path")

	def run_local(self):
		for pkgset in self.settings["grp"]:
			# example call: "grp.sh run pkgset cd1 xmms vim sys-apps/gleep"
			mypackages = catalyst.util.list_bashify(self.settings[pkgset + "/packages"])
			try:
				self.run_controller_action("run", self.settings[pkgset + "/type"] + " " + pkgset)

			except CatalystError:
				self.unbind()
				raise CatalystError,"GRP build aborting due to error."

	def set_use(self):
		generic_stage_target.set_use(self)
		if "use" in self.settings:
			self.settings["use"].append("bindist")
		else:
			self.settings["use"]=["bindist"]

	def set_mounts(self):
		self.mounts.append("/tmp/grp")
		self.mountmap["/tmp/grp"]=self.settings["target_path"]

	def generate_digests(self):
		for pkgset in self.settings["grp"]:
			if self.settings["grp/"+pkgset+"/type"] == "pkgset":
				destdir=catalyst.util.normpath(self.settings["target_path"]+"/"+pkgset+"/All")
				msg("Digesting files in the pkgset.....")
				digests=glob.glob(destdir+'/*.DIGESTS')
				for i in digests:
					if os.path.exists(i):
						os.remove(i)

				files=os.listdir(destdir)
				#ignore files starting with '.' using list comprehension
				files=[filename for filename in files if filename[0] != '.']
				for i in files:
					if os.path.isfile(catalyst.util.normpath(destdir+"/"+i)):
						catalyst.hash.gen_contents_file(catalyst.util.normpath(destdir+"/"+i), self.settings)
						catalyst.hash.gen_digest_file(catalyst.util.normpath(destdir+"/"+i), self.settings)
			else:
				destdir=catalyst.util.normpath(self.settings["target_path"]+"/"+pkgset)
				msg("Digesting files in the srcset.....")

				digests=glob.glob(destdir+'/*.DIGESTS')
				for i in digests:
					if os.path.exists(i):
						os.remove(i)

				files=os.listdir(destdir)
				#ignore files starting with '.' using list comprehension
				files=[filename for filename in files if filename[0] != '.']
				for i in files:
					if os.path.isfile(catalyst.util.normpath(destdir+"/"+i)):
						#catalyst.hash.gen_contents_file(catalyst.util.normpath(destdir+"/"+i), self.settings)
						catalyst.hash.gen_digest_file(catalyst.util.normpath(destdir+"/"+i), self.settings)

	def set_action_sequence(self):
		self.settings["action_sequence"]=["unpack","unpack_snapshot",\
				"config_profile_link","setup_confdir","portage_overlay","bind","chroot_setup",\
				"setup_environment","run_local","unbind",\
				"generate_digests","clear_autoresume"]

__target_map = { "grp": grp_target }

# vim: ts=4 sw=4 sta noet sts=4 ai
