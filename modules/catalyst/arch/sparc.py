
import catalyst.arch,os
from catalyst.support import *
from catalyst.error import *

class generic_sparc(catalyst.arch.generic_arch):
	"abstract base class for all sparc builders"
	def __init__(self,myspec):
		catalyst.arch.generic_arch.__init__(self,myspec)
		if self.settings["buildarch"]=="sparc64":
			if not os.path.exists("/bin/linux32") and not os.path.exists("/usr/bin/linux32"):
				raise CatalystError,"required executable linux32 not found (\"emerge setarch\" to fix.)"
			self.settings["CHROOT"]="linux32 chroot"
			self.settings["crosscompile"] = False;
		else:
			self.settings["CHROOT"]="chroot"

class generic_sparc64(catalyst.arch.generic_arch):
	"abstract base class for all sparc64 builders"
	def __init__(self,myspec):
		catalyst.arch.generic_arch.__init__(self,myspec)
		self.settings["CHROOT"]="chroot"

class arch_sparc(generic_sparc):
	"builder class for generic sparc (sun4cdm)"
	def __init__(self,myspec):
		generic_sparc.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -pipe"
		self.settings["CHOST"]="sparc-unknown-linux-gnu"

class arch_sparc64(generic_sparc64):
	"builder class for generic sparc64 (sun4u)"
	def __init__(self,myspec):
		generic_sparc64.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -mcpu=ultrasparc -pipe"
		self.settings["CHOST"]="sparc-unknown-linux-gnu"

__subarch_map = {
	"sparc"		: arch_sparc,
	"sparc64"	: arch_sparc64
}

__machine_map = ("sparc","sparc64")

