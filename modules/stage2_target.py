# Copyright 1999-2005 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/modules/stage2_target.py,v 1.9 2005/12/13 20:32:43 rocket Exp $

"""
Builder class for a stage2 installation tarball build.
"""

from catalyst_support import *
from generic_stage_target import *

class stage2_target(generic_stage_target):
	def __init__(self,spec,addlargs):
		self.required_values=[]
		self.valid_values=[]
		generic_stage_target.__init__(self,spec,addlargs)
	def set_root_path(self):
               # ROOT= variable for emerges
                self.settings["root_path"]=normpath("/tmp/stage1root")

        def set_source_path(self):
            self.settings["source_path"]=normpath(self.settings["storedir"]+"/tmp/"+self.settings["source_subpath"]+"/"+self.settings["root_path"]+"/")

	    # reset the root path so the preclean doesnt fail
	    generic_stage_target.set_root_path(self)

	    if os.path.isdir(self.settings["source_path"]):
                print "\nUsing seed-stage from "+self.settings["source_path"]
                print "Delete this folder if you wish to use a seed stage tarball instead\n"
            else:
                self.settings["source_path"]=normpath(self.settings["storedir"]+"/builds/"+self.settings["source_subpath"]+".tar.bz2")
                if os.path.isfile(self.settings["source_path"]):
                        if os.path.exists(self.settings["source_path"]):
                                 self.settings["source_path_md5sum"]=calc_md5(self.settings["source_path"])
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

        def set_portage_overlay(self):
                generic_stage_target.set_portage_overlay(self)
                print "\nWARNING !!!!!"
                print "\tUsing an overlay for earlier stages could cause build issues."
                print "\tIf you break it, you buy it. Don't complain to us about it."
                print "\tDont say we did not warn you\n"


def register(foo):
	foo.update({"stage2":stage2_target})
	return foo
