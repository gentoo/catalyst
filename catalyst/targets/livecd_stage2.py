"""
LiveCD stage2 target, builds upon previous LiveCD stage1 tarball
"""
# NOTE: That^^ docstring has influence catalyst-spec(5) man page generation.

import os


from catalyst.support import (normpath, file_locate, CatalystError, cmd,
	read_from_clst, touch)
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
			"gamecd/conf","livecd/xdm","livecd/xsession","livecd/volid"])

		StageBase.__init__(self,spec,addlargs)
		if "livecd/type" not in self.settings:
			self.settings["livecd/type"] = "generic-livecd"

		file_locate(self.settings, ["cdtar","controller_file"])

	def set_source_path(self):
		self.settings["source_path"]=normpath(self.settings["storedir"]+"/builds/"+self.settings["source_subpath"].rstrip('/')+".tar.bz2")
		if os.path.isfile(self.settings["source_path"]):
			self.settings["source_path_hash"] = \
				self.settings["hash_map"].generate_hash(
					self.settings["source_path"])
		else:
			self.settings["source_path"]=normpath(self.settings["storedir"]+"/tmp/"+self.settings["source_subpath"]+'/')
		if not os.path.exists(self.settings["source_path"]):
			raise CatalystError("Source Path: " +
				self.settings["source_path"] + " does not exist.",
					print_traceback=True)

	def set_spec_prefix(self):
		self.settings["spec_prefix"]="livecd"

	def set_target_path(self):
		self.settings["target_path"]=normpath(self.settings["storedir"]+"/builds/"+self.settings["target_subpath"]+"/")
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

	def unpack(self):
		_unpack=True
		display_msg=None

		clst_unpack_hash = self.resume.get("unpack")

		if os.path.isdir(self.settings["source_path"]):
			unpack_cmd="rsync -a --delete "+self.settings["source_path"]+" "+self.settings["chroot_path"]
			display_msg="\nStarting rsync from "+self.settings["source_path"]+"\nto "+\
				self.settings["chroot_path"]+" (This may take some time) ...\n"
			error_msg="Rsync of "+self.settings["source_path"]+" to "+self.settings["chroot_path"]+" failed."
			invalid_snapshot=False

		if "autoresume" in self.settings["options"]:
			if os.path.isdir(self.settings["source_path"]) and \
				self.resume.is_enabled("unpack"):
				print "Resume point detected, skipping unpack operation..."
				_unpack=False
			elif "source_path_hash" in self.settings:
				if self.settings["source_path_hash"] != clst_unpack_hash:
					invalid_snapshot=True

		if _unpack:
			self.mount_safety_check()
			if invalid_snapshot:
				print "No Valid Resume point detected, cleaning up  ..."
				self.clear_autoresume()
				self.clear_chroot()

			ensure_dirs(self.settings["chroot_path"]+"/tmp", mode=1777)

			if "pkgcache" in self.settings["options"]:
				ensure_dirs(self.settings["pkgcache_path"], mode=0755)

			if not display_msg:
				raise CatalystError("Could not find appropriate source.\n"
					"Please check the 'source_subpath' "
					"setting in the spec file.",
					print_traceback=True)

			print display_msg
			cmd(unpack_cmd,error_msg,env=self.env)

			if "source_path_hash" in self.settings:
				self.resume.enable("unpack", data=self.settings["source_path_hash"])
			else:
				self.resume.enable("unpack")

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
