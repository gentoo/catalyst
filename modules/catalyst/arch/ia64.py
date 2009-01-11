
import catalyst.arch,os
from catalyst.support import *

class arch_ia64(catalyst.arch.generic_arch):
	"builder class for ia64"
	def __init__(self,myspec):
		catalyst.arch.generic_arch.__init__(self,myspec)
		self.settings["CHROOT"]="chroot"
		self.settings["CFLAGS"]="-O2 -pipe"
		self.settings["CFLAGS"]="-O2 -pipe"
		self.settings["CHOST"]="ia64-unknown-linux-gnu"

__subarch_map = {
	"ia64": arch_ia64
}

__machine_map = ("ia64", )

