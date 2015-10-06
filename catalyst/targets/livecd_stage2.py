"""
LiveCD stage2 target, builds upon previous LiveCD stage1 tarball
"""
# NOTE: That^^ docstring has influence catalyst-spec(5) man page generation.

import os

from catalyst.support import (normpath, file_locate, CatalystError, cmd)
from catalyst.fileops import ensure_dirs
from catalyst.base.stagebase import StageBase


class livecd_stage2(StageBase):
	"""
	Builder class for a LiveCD stage2 build.
	"""
	def __init__(self,spec,addlargs):
		self.required_values=["boot/kernel"]

		self.valid_values=[]

		self.valid_values.extend(self.required_values)
		self.valid_values.extend(["livecd/cdtar","livecd/empty","livecd/rm",\
			"livecd/unmerge","livecd/iso","livecd/gk_mainargs","livecd/type",\
			"livecd/readme","livecd/motd","livecd/overlay",\
			"livecd/modblacklist","livecd/splash_theme","livecd/rcadd",\
			"livecd/rcdel","livecd/fsscript","livecd/xinitrc",\
			"livecd/root_overlay","livecd/users","portage_overlay",\
			"livecd/fstype","livecd/fsops","livecd/linuxrc","livecd/bootargs",\
			"gamecd/conf","livecd/xdm","livecd/xsession","livecd/volid","livecd/verify"])

		StageBase.__init__(self,spec,addlargs)
		if "livecd/type" not in self.settings:
			self.settings["livecd/type"] = "generic-livecd"

		file_locate(self.settings, ["cdtar","controller_file"])

	def set_source_path(self):
		self.settings["source_path"]=normpath(self.settings["storedir"]+"/builds/"+self.settings["source_subpath"])
		if os.path.isfile(self.settings["source_path"]):
			self.settings["source_path_hash"] = \
				self.settings["hash_map"].generate_hash(
					self.settings["source_path"])
		else:
			self.settings["source_path"]=normpath(self.settings["storedir"]+"/tmp/"+self.settings["source_subpath"])
		if not os.path.exists(self.settings["source_path"]):
			raise CatalystError("Source Path: " +
				self.settings["source_path"] + " does not exist.",
					print_traceback=True)

	def set_spec_prefix(self):
		self.settings["spec_prefix"]="livecd"

	def set_target_path(self):
		self.settings["target_path"]=normpath(self.settings["storedir"]+"/builds/"+self.settings["target_subpath"])
		if "autoresume" in self.settings["options"] \
			and self.resume.is_enabled("setup_target_path"):
				print "Resume point detected, skipping target path setup operation..."
		else:
			# first clean up any existing target stuff
			if os.path.isdir(self.settings["target_path"]):
				cmd("rm -rf "+self.settings["target_path"],
				"Could not remove existing directory: "+self.settings["target_path"],env=self.env)
				self.resume.enable("setup_target_path")
			ensure_dirs(self.settings["target_path"])

	def run_local(self):
		# what modules do we want to blacklist?
		if "livecd/modblacklist" in self.settings:
			try:
				myf=open(self.settings["chroot_path"]+"/etc/modprobe.d/blacklist.conf","a")
			except:
				self.unbind()
				raise CatalystError("Couldn't open " +
					self.settings["chroot_path"] +
					"/etc/modprobe.d/blacklist.conf.",
					print_traceback=True)

			myf.write("\n#Added by Catalyst:")
			# workaround until config.py is using configparser
			if isinstance(self.settings["livecd/modblacklist"], str):
				self.settings["livecd/modblacklist"] = self.settings["livecd/modblacklist"].split()
			for x in self.settings["livecd/modblacklist"]:
				myf.write("\nblacklist "+x)
			myf.close()

	def set_action_sequence(self):
		self.settings["action_sequence"]=["unpack","unpack_snapshot",\
				"config_profile_link","setup_confdir","portage_overlay",\
				"bind","chroot_setup","setup_environment","run_local",\
				"build_kernel"]
		if "fetch" not in self.settings["options"]:
			self.settings["action_sequence"] += ["bootloader","preclean",\
				"livecd_update","root_overlay","fsscript","rcupdate","unmerge",\
				"unbind","remove","empty","target_setup",\
				"setup_overlay","create_iso"]
		self.settings["action_sequence"].append("clear_autoresume")
