# Copyright 1999-2005 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/modules/stage1_target.py,v 1.11 2005/11/07 16:25:06 rocket Exp $

"""
Builder class for a stage1 installation tarball build.
"""

from catalyst_support import *
from generic_stage_target import *

class stage1_target(generic_stage_target):
	def __init__(self,spec,addlargs):
		self.required_values=[]
		self.valid_values=[]
		generic_stage_target.__init__(self,spec,addlargs)
	
	def set_stage_path(self):
		self.settings["stage_path"]=normpath(self.settings["chroot_path"]+self.settings["root_path"])
		print "stage1 stage path is "+self.settings["stage_path"]
	def set_root_path(self):
	       # ROOT= variable for emerges
		self.settings["root_path"]=normpath("/tmp/stage1root")
		print "stage1 root path is "+self.settings["root_path"]
	def set_dest_path(self):
                self.settings["destpath"]=normpath(self.settings["chroot_path"]+self.settings["root_path"])
	def set_cleanables(self):
		generic_stage_target.set_cleanables(self)
		self.settings["cleanables"].extend(["/usr/share/gettext","/usr/lib/python2.2/test", "/usr/lib/python2.2/encodings","/usr/lib/python2.2/email", "/usr/lib/python2.2/lib-tk","/usr/share/zoneinfo"])

	def override_chost(self):
	    if os.environ.has_key("CHOST"):
		self.settings["CHOST"] = os.environ["CHOST"]
	    if self.settings.has_key("chost"):
		self.settings["CHOST"]=list_to_string(self.settings["chost"])

	def override_cflags(self):
	    if os.environ.has_key("CFLAGS"):
		self.settings["CFLAGS"] = os.environ["CFLAGS"]
	    if self.settings.has_key("cflags"):
		self.settings["CFLAGS"]=list_to_string(self.settings["cflags"])

	def override_cxxflags(self):
	    if os.environ.has_key("CXXFLAGS"):
		self.settings["CXXFLAGS"] = os.environ["CXXFLAGS"]
	    if self.settings.has_key("cxxflags"):
		self.settings["CXXFLAGS"]=list_to_string(self.settings["cxxflags"])

        def override_ldflags(self):
                if os.environ.has_key("LDFLAGS"):
                    self.settings["LDFLAGS"] = os.environ["LDFLAGS"]
                if self.settings.has_key("ldflags"):
                    self.settings["LDFLAGS"]=list_to_string(self.settings["ldflags"])

def reg(foo):
	foo.update({"stage1":stage1_target})
	return foo
