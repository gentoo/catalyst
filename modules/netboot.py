# Distributed under the GNU General Public License version 2
# Copyright 2003-2004 Gentoo Technologies, Inc.
# $Header: /var/cvsroot/gentoo/src/catalyst/modules/Attic/netboot.py,v 1.4 2004/10/11 15:41:23 zhen Exp $

"""
Builder class for a netboot build.
"""

import os,string,types
from catalyst_support import *
from generic_stage_target import *

class netboot_target(generic_stage_target):
	def __init__(self,spec,addlargs):
		self.valid_values = [
			"netboot/kernel/sources",
			"netboot/kernel/config",
			"netboot/kernel/prebuilt",

			"netboot/busybox_config",

			"netboot/extra_files",
			"netboot/packages"
		]
		self.required_values=[]
			
		try:
			if addlargs.has_key("netboot/packages"):
				if type(addlargs["netboot/packages"]) == types.StringType:
					loopy=[addlargs["netboot/packages"]]
				else:
					loopy=addlargs["netboot/packages"]
			
			for x in loopy:
				self.required_values.append("netboot/packages/"+x+"/files")
		except:
			raise CatalystError,"configuration error in netboot/packages."
		
		generic_stage_target.__init__(self,spec,addlargs)
		
		if addlargs.has_key("netboot/busybox_config"):
			file_locate(self.settings, ["netboot/busybox_config"])

		if addlargs.has_key("netboot/kernel/sources"):
			file_locate(self.settings, ["netboot/kernel/config"])
		elif addlargs.has_key("netboot/kernel/prebuilt"):
			file_locate(self.settings, ["netboot/kernel/prebuilt"])
		else:
			raise CatalystError,"you must define netboot/kernel/config or netboot/kernel/prebuilt"

		# unless the user wants specific CFLAGS/CXXFLAGS, let's use -Os
		for envvar in "CFLAGS", "CXXFLAGS":
			if not os.environ.has_key(envvar) and not addlargs.has_key(envvar):
				self.settings[envvar] = "-Os -pipe"

	
	def run_local(self):
		# setup our chroot
		try:
			cmd("/bin/bash "+self.settings["sharedir"]+\
				"/targets/netboot/netboot.sh setup")
		except CatalystError:
			self.unbind()
			raise CatalystError,"couldn't setup netboot env."

		# build packages
		if self.settings.has_key("netboot/packages"):
			mypack=list_bashify(self.settings["netboot/packages"])
		try:
			cmd("/bin/bash "+self.settings["sharedir"]+\
				"/targets/netboot/netboot.sh packages "+mypack)
		except CatalystError:
			self.unbind()
			raise CatalystError,"netboot build aborting due to error."

		# build busybox
		if self.settings.has_key("netboot/busybox_config"):
			mycmd = self.settings["netboot/busybox_config"]
		else:
			mycmd = ""
		try:
			cmd("/bin/bash "+self.settings["sharedir"]+\
				"/targets/netboot/netboot.sh busybox "+ mycmd)
		except CatalystError:
			self.unbind()
			raise CatalystError,"netboot build aborting due to error."

		# build kernel
		if self.settings.has_key("netboot/kernel/prebuilt"):
			mycmd = "kernel-prebuilt " + \
			        self.settings["netboot/kernel/prebuilt"]
		else:
			mycmd = "kernel-sources " + \
			        self.settings["netboot/kernel/sources"] + " " + \
			        self.settings["netboot/kernel/config"]
		try:
			cmd("/bin/bash "+self.settings["sharedir"]+\
			    "/targets/netboot/netboot.sh kernel " + mycmd)
		except CatalystError:
			self.unbind()
			raise CatalystError,"netboot build aborting due to error."

		# create image
		myfiles=[]
		if self.settings.has_key("netboot/packages"):
			if type(self.settings["netboot/packages"]) == types.StringType:
				loopy=[self.settings["netboot/packages"]]
			else:
				loopy=self.settings["netboot/packages"]
		
		for x in loopy:
			print x, self.settings["netboot/packages/"+x+"/files"]
			if type(self.settings["netboot/packages/"+x+"/files"]) == types.ListType:
				myfiles.extend(self.settings["netboot/packages/"+x+"/files"])
			else:
				myfiles.append(self.settings["netboot/packages/"+x+"/files"])

		if self.settings.has_key("netboot/extra_files"):
			if type(self.settings["netboot/extra_files"]) == types.ListType:
				myfiles.extend(self.settings["netboot/extra_files"])
			else:
				myfiles.append(self.settings["netboot/extra_files"])

		try:
			cmd("/bin/bash "+self.settings["sharedir"]+\
				"/targets/netboot/netboot.sh image " + list_bashify(myfiles))
		except CatalystError:
			self.unbind()
			raise CatalystError,"netboot build aborting due to error."

		# finish it all up
		try:
			cmd("/bin/bash "+self.settings["sharedir"]+\
				"/targets/netboot/netboot.sh finish")
		except CatalystError:
			self.unbind()
			raise CatalystError,"netboot build aborting due to error."

		# end
		print "netboot: build finished !"


def register(foo):
	foo.update({"netboot":netboot_target})
	return foo
