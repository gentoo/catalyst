
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
	def __init__(self):
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
	def spec_require(self):
		return ["version_stamp","subarch","rel_type","rel_version","snapshot","source_subpath"]

class snapshot_target(generic_target):
	def __init__(self):
		pass
	def spec_require(self):
		return ["snapshot"]

class stage1_target(generic_stage_target):
	def __init__(self):
		generic_target.__init__(self)
		pass

class stage2_target(generic_stage_target):
	def __init__(self):
		generic_target.__init__(self)
		pass

class stage3_target(generic_stage_target):
	def __init__(self):
		generic_target.__init__(self)
		pass

class grp_target(generic_stage_target):
	def __init__(self):
		generic_target.__init__(self)
		pass

class livecd_target(generic_stage_target):
	def __init__(self):
		generic_target.__init__(self)
		pass

def register(foo):
	foo.update({"stage1":stage1_target,"stage2":stage2_target,"stage3":stage3_target,
	"grp":grp_target,"livecd":livecd_target,"snapshot":snapshot_target})
	return foo
	
