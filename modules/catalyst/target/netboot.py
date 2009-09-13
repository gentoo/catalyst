
"""
Builder class for a netboot build, version 2
"""

import os, string
from generic_stage import *
import catalyst.util
from catalyst.error import *
from catalyst.spawn import cmd
from catalyst.output import *

class netboot_target(generic_stage_target):
	def __init__(self):
		generic_stage_target.__init__(self)

		self.required_values=[
			"boot/kernel"
		]
		self.valid_values=self.required_values[:]
		self.valid_values.extend([
			"netboot/packages",
			"netboot/use",
			"netboot/extra_files",
			"netboot/overlay",
			"netboot/busybox_config",
			"netboot/root_overlay",
			"netboot/linuxrc"
		])

		try:
			if "netboot/packages" in self.settings:
				if isinstance(self.settings["netboot/packages"], str):
					loopy=[self.settings["netboot/packages"]]
				else:
					loopy=self.settings["netboot/packages"]

				for x in loopy:
					self.valid_values.append("netboot/packages/"+x+"/files")
		except:
			raise CatalystError,"configuration error in netboot/packages."

		self.settings["merge_path"]=catalyst.util.normpath("/tmp/image/")

	def set_target_path(self):
		self.settings["target_path"]=catalyst.util.normpath(self.settings["storedir"]+"/builds/"+\
			self.settings["target_subpath"]+"/")
		if self.check_autoresume("setup_target_path"):
				msg("Resume point detected, skipping target path setup operation...")
		else:
			# first clean up any existing target stuff
			if os.path.isfile(self.settings["target_path"]):
				catalyst.util.remove_path(self.settings["target_path"])

			if not os.path.exists(self.settings["storedir"]+"/builds/"):
				os.makedirs(self.settings["storedir"]+"/builds/")

			self.set_autoresume("setup_target_path")

	def copy_files_to_image(self):
		# copies specific files from the buildroot to merge_path
		myfiles=[]

		# check for autoresume point
		if self.check_autoresume("copy_files_to_image"):
				msg("Resume point detected, skipping target path setup operation...")
		else:
			if "netboot/packages" in self.settings:
				if isinstance(self.settings["netboot/packages"], str):
					loopy=[self.settings["netboot/packages"]]
				else:
					loopy=self.settings["netboot/packages"]

			for x in loopy:
				if "netboot/packages/"+x+"/files" in self.settings:
					if isinstance(self.settings["netboot/packages/"+x+"/files"], list):
						myfiles.extend(self.settings["netboot/packages/"+x+"/files"])
					else:
						myfiles.append(self.settings["netboot/packages/"+x+"/files"])

			if "netboot/extra_files" in self.settings:
				if isinstance(self.settings["netboot/extra_files"], list):
					myfiles.extend(self.settings["netboot/extra_files"])
				else:
					myfiles.append(self.settings["netboot/extra_files"])

			try:
				self.run_controller_action("image", catalyst.util.list_bashify(myfiles))
			except CatalystError:
				self.unbind()
				raise CatalystError,"Failed to copy files to image!"

			self.set_autoresume("copy_files_to_image")

	def setup_overlay(self):
		if self.check_autoresume("setup_overlay"):
			msg("Resume point detected, skipping setup_overlay operation...")
		else:
			if "netboot/overlay" in self.settings:
				for x in self.settings["netboot/overlay"]:
					if os.path.exists(x):
						cmd("rsync -a "+x+"/ "+\
							self.settings["chroot_path"] + self.settings["merge_path"], "netboot/overlay: "+x+" copy failed.",env=self.env)
				self.set_autoresume("setup_overlay")

	def move_kernels(self):
		# we're done, move the kernels to builds/*
		# no auto resume here as we always want the
		# freshest images moved
		try:
			self.run_controller_action("final")
			msg(">>> Netboot Build Finished!")
		except CatalystError:
			self.unbind()
			raise CatalystError,"Failed to move kernel images!"

	def remove(self):
		if self.check_autoresume("remove"):
			msg("Resume point detected, skipping remove operation...")
		else:
			if "rm" in self.settings:
				for x in self.settings["rm"]:
					msg("netboot: removing " + x)
					catalyst.util.remove_path(self.settings["chroot_path"] + self.settings["merge_path"] + x)

	def empty(self):
		if self.check_autoresume("empty"):
			msg("Resume point detected, skipping empty operation...")
		else:
			if "netboot/empty" in self.settings:
				if isinstance(self.settings["netboot/empty"], str):
					self.settings["netboot/empty"]=self.settings["netboot/empty"].split()
				for x in self.settings["netboot/empty"]:
					myemp=self.settings["chroot_path"] + self.settings["merge_path"] + x
					if not os.path.isdir(myemp):
						msg(x + " not a directory or does not exist, skipping 'empty' operation.")
						continue
					msg("Emptying directory " + x)
					catalyst.util.empty_dir(x)
		self.set_autoresume("empty")

	def set_action_sequence(self):
		self.settings["action_sequence"]=["unpack","unpack_snapshot","config_profile_link",
				"setup_confdir","portage_overlay","bind","chroot_setup",\
				"setup_environment","build_packages","root_overlay",\
				"copy_files_to_image","setup_overlay","build_kernel","move_kernels",\
				"remove","empty","unbind","clean","clear_autoresume"]

__target_map = {"netboot":netboot_target}

# vim: ts=4 sw=4 sta noet sts=4 ai
