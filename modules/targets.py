
"""
local variables from spec:

version_stamp			20031016					user (from spec)
target				stage3						user (from spec)
subarch				pentium4					user (from spec)
rel_type			default						user (from spec) (was BUILDTYPE)
rel_version			1.4						user (from spec) (was MAINVERSION)
snapshot			20031016					user (from spec)
source_subpath			default-x86-1.4/stage2-pentium4-20031016	user (from spec)
"""

class generic_target:
	def __init__(self,myspec):
		self.settings=myspec
		pass
	def run_prep(self):
		"""copy scripts into location, generate files containing build
		commands (for GRP), etc."""
	def list_mounts(self):
		"""specify needed mounts and their locations."""
	def run_script(self):
		"""specify script to run."""
	def spec_require(self):
		"""return list of definitions required from spec"""

class generic_stage_target(generic_target):
	def __init__(self,myspec):
		generic_target.__init__(self,myspec)
		#we'd want to make sure we have all the settings we need here
		self.settings["target_subpath"]=self.settings["rel_type"]+"-"+self.settings["mainarch"]+"-"+self.settings["rel_version"]
		self.settings["target_subpath"]+="/"+self.settings["target"]+"-"+self.settings["subarch"]+"-"+self.settings["version_stamp"]
		st=self.settings["storedir"]
		self.settings["snapshot_path"]=st+"/snapshots/portage-"+self.settings["snapshot"]+".tar.bz2"
		self.settings["target_path"]=st+"/builds/"+self.settings["target_subpath"]+".tar.bz2"
		self.settings["source_path"]=st+"/builds/"+self.settings["source_subpath"]+".tar.bz2"
		self.settings["chroot_path"]=st+"/tmp/"+self.settings["target_subpath"]
		self.settings["pkgcache_path"]=st+"/packages/"+self.settings["target_subpath"]

class snapshot_target(generic_target):
	def __init__(self):
		pass
	def spec_require(self):
		return ["snapshot"]

class stage1_target(generic_stage_target):
	def __init__(self,spec):
		generic_stage_target.__init__(self,spec)
		pass

class stage2_target(generic_stage_target):
	def __init__(self,spec):
		generic_stage_target.__init__(self,spec)
		pass

class stage3_target(generic_stage_target):
	def __init__(self,spec):
		generic_stage_target.__init__(self,spec)
		pass

class grp_target(generic_stage_target):
	def __init__(self,spec):
		generic_target.__init__(self,spec)
		pass

class livecd_target(generic_stage_target):
	def __init__(self):
		generic_target.__init__(self)
		pass

def register(foo):
	foo.update({"stage1":stage1_target,"stage2":stage2_target,"stage3":stage3_target,
	"grp":grp_target,"livecd":livecd_target,"snapshot":snapshot_target})
	return foo
	
