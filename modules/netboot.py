# Distributed under the GNU General Public License version 2
# Copyright 2003-2004 Gentoo Technologies, Inc.
# $Header: /var/cvsroot/gentoo/src/catalyst/modules/Attic/netboot.py,v 1.1 2004/10/06 01:34:29 zhen Exp $

"""
Builder class for a netboot build.
"""

import os,string,types
from catalyst_support import *
from generic_stage_target import *

class netboot_target(generic_stage_target):
	def __init__(self,spec,addlargs):
		self.required_values=["netboot/kernel/sources",\
		"netboot/kernel/config","netboot/busybox_config"]

		self.valid_values=["netboot/extra_files"]
		if not addlargs.has_key("netboot/packages"):
			raise CatalystError, "Required value netboot/packages not specified."
			
		if type(addlargs["netboot/packages"]) == types.StringType:
			loopy=[addlargs["netboot/packages"]]
			
		else:
			loopy=addlargs["netboot/packages"]
			
		for x in loopy:
			self.required_values.append("netboot/packages/"+x+"/files")
		
		self.valid_values.extend(self.required_values)
		
		generic_stage_target.__init__(self,spec,addlargs)
		
		file_locate(self.settings, ["netboot/busybox_config"])
		file_locate(self.settings, ["netboot/kernel/config"])
		file_locate(self.settings, ["netboot/base_tarball"])
	
	def run_local(self):
		# Build packages
		mypack=list_bashify(self.settings["netboot/packages"])
		try:
			cmd("/bin/bash "+self.settings["sharedir"]+\
				"/targets/netboot/netboot.sh packages "+mypack)
		
		except CatalystError:
			self.unbind()
			raise CatalystError,"netboot build aborting due to error."

		# Build busybox
		try:
			cmd("/bin/bash "+self.settings["sharedir"]+\
				"/targets/netboot/netboot.sh busybox "+ self.settings["netboot/busybox_config"])
		
		except CatalystError:
			self.unbind()
			raise CatalystError,"netboot build aborting due to error."

		# Build kernel
		try:
			cmd("/bin/bash "+self.settings["sharedir"]+\
				"/targets/netboot/netboot.sh kernel "+ self.settings["netboot/kernel/sources"] + " " +\
				self.settings["netboot/kernel/config"])
		
		except CatalystError:
			self.unbind()
			raise CatalystError,"netboot build aborting due to error."

		# Create image
		myfiles=[]
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

		if type(self.settings["netboot/extra_files"]) == types.ListType:
			myfiles.extend(self.settings["netboot/extra_files"])
		else:
			myfiles.append(self.settings["netboot/extra_files"])

		try:
			cmd("/bin/bash "+self.settings["sharedir"]+\
				"/targets/netboot/netboot.sh image "+ self.settings["netboot/base_tarball"] + " " + list_bashify(myfiles))
		
		except CatalystError:
			self.unbind()
			raise CatalystError,"netboot build aborting due to error."

		# Copying images in the target_path
		try:
			cmd("/bin/bash "+self.settings["sharedir"]+\
				"/targets/netboot/netboot.sh finish")
		
		except CatalystError:
			self.unbind()
			raise CatalystError,"netboot build aborting due to error."

		# End
		print "netboot: build finished !"


def register(foo):
	foo.update({"netboot":netboot_target})
	return foo
