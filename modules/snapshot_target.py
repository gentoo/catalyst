# Distributed under the GNU General Public License version 2
# Copyright 2003-2004 Gentoo Technologies, Inc.
# $Header: /var/cvsroot/gentoo/src/catalyst/modules/snapshot_target.py,v 1.4 2004/08/13 16:00:48 zhen Exp $

"""
Builder class for snapshots.
"""

import os
from catalyst_support import *
from generic_stage_target import *

class snapshot_target(generic_target):
	def __init__(self,myspec,addlargs):
		self.required_values=["version_stamp","target"]
		self.valid_values=["version_stamp","target","portdir_overlay"]
		
		generic_target.__init__(self,myspec,addlargs)
		self.settings=myspec
		self.settings["target_subpath"]="portage"
		st=self.settings["storedir"]
		self.settings["snapshot_path"]=st+"/snapshots/portage-"+self.settings["version_stamp"]\
			+".tar.bz2"
		self.settings["tmp_path"]=st+"/tmp/"+self.settings["target_subpath"]

	def setup(self):
		x=self.settings["storedir"]+"/snapshots"
		if not os.path.exists(x):
			os.makedirs(x)

	def run(self):
		self.setup()
		print "Creating Portage tree snapshot "+self.settings["version_stamp"]+\
			" from "+self.settings["portdir"]+"..."
		
		mytmp=self.settings["tmp_path"]
		if not os.path.exists(mytmp):
			os.makedirs(mytmp)
		
		cmd("rsync -a --delete --exclude /packages/ --exclude /distfiles/ --exclude CVS/ "+\
			self.settings["portdir"]+"/ "+mytmp+"/portage/","Snapshot failure")
		
		if self.settings.has_key("portdir_overlay"):
			print "Adding Portage overlay to the snapshot..."
			cmd("rsync -a --exclude /packages/ --exclude /distfiles/ --exclude CVS/ "+\
				self.settings["portdir_overlay"]+"/ "+mytmp+"/portage/","Snapshot/ overlay addition failure")
			
		print "Compressing Portage snapshot tarball..."
		cmd("tar cjf "+self.settings["snapshot_path"]+" -C "+mytmp+" portage",\
			"Snapshot creation failure")
		self.cleanup()
		print "snapshot: complete!"

	def cleanup(self):
		print "Cleaning up..."
			
def register(foo):
	foo.update({"snapshot":snapshot_target})
	return foo
