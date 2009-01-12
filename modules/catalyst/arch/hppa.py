
import catalyst.arch
from catalyst.support import *

class generic_hppa(catalyst.arch.generic_arch):
	"Abstract base class for all hppa builders"
	def __init__(self,myspec):
		catalyst.arch.generic_arch.__init__(self,myspec)
		self.settings["CHROOT"]="chroot"
		self.settings["CFLAGS"]="-O2 -pipe"
		self.settings["CXXFLAGS"]="-O2 -pipe"

class arch_hppa(generic_hppa):
	"Builder class for hppa systems"
	def __init__(self,myspec):
		generic_hppa.__init__(self,myspec)
		self.settings["CFLAGS"]+=" -march=1.0"
		self.settings["CHOST"]="hppa-unknown-linux-gnu"

class arch_hppa1_1(generic_hppa):
	"Builder class for hppa 1.1 systems"
	def __init__(self,myspec):
		generic_hppa.__init__(self,myspec)
		self.settings["CFLAGS"]+=" -march=1.1"
		self.settings["CHOST"]="hppa1.1-unknown-linux-gnu"

class arch_hppa2_0(generic_hppa):
	"Builder class for hppa 2.0 systems"
	def __init__(self,myspec):
		generic_hppa.__init__(self,myspec)
		self.settings["CFLAGS"]+=" -march=2.0"
		self.settings["CHOST"]="hppa2.0-unknown-linux-gnu"

__subarch_map = {
	"hppa":		arch_hppa,
	"hppa1.1":	arch_hppa1_1,
	"hppa2.0":	arch_hppa2_0
}

__machine_map = ("parisc","parisc64","hppa","hppa64")

