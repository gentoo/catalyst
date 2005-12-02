# Copyright 1999-2005 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/modules/stage2_target.py,v 1.6 2005/12/02 17:05:56 wolf31o2 Exp $

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

def register(foo):
	foo.update({"stage2":stage2_target})
	return foo
