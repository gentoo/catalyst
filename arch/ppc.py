# Distributed under the GNU General Public License version 2
# Copyright 2003-2004 Gentoo Technologies, Inc.

import builder

class generic_ppc(builder.generic):
	"abstract base class for all ppc builders"
	def __init__(self,myspec):
		builder.generic.__init__(self,myspec)
		self.settings["mainarch"]="ppc"
		self.settings["CHROOT"]="chroot"
		self.settings["CHOST"]="powerpc-unknown-linux-gnu"


class arch_power_ppc(generic_ppc):
	"builder class for generic powerpc/power"
	def __init__(self,myspec):
		generic_ppc.__init__(self,myspec)
		self.settings["CFLAGS"]="-O3 -mcpu=common"

class arch_ppc(generic_ppc):
	"builder class for generic powerpc"
	def __init__(self,myspec):
		generic_ppc.__init__(self,myspec)
		self.settings["CFLAGS"]="-O3 -mcpu=powerpc"

class arch_power(generic_ppc):
	"builder class for generic power"
	def __init__(self,myspec):
		generic_ppc.__init__(self,myspec)
		self.settings["CFLAGS"]="-O3 -mcpu=power"

class arch_g3(generic_ppc):
	def __init__(self,myspec):
		generic_ppc.__init__(self,myspec)
		self.settings["CFLAGS"]="-O3 -mcpu=G3"

class arch_g4(generic_ppc):
	def __init__(self,myspec):
		generic_ppc.__init__(self,myspec)
		self.settings["CFLAGS"]="-O3 -mcpu=G4 -maltivec -mabi=altivec"
		self.settings["HOSTUSE"]=["altivec"]

class arch_g5(generic_ppc):
	def __init__(self,myspec):
		generic_ppc.__init__(self,myspec)
		self.settings["CFLAGS"]="-O3 -mcpu=G5 -maltivec -mabi=altivec"
		self.settings["HOSTUSE"]=["altivec"]
		
def register(foo):
	"Inform main catalyst program of the contents of this plugin."
	#power/ppc can't be used as a subarch name as it has a "/" in it and is used in filenames
	foo.update({"ppc":arch_ppc,"power":arch_power,"power-ppc":arch_power_ppc,"g3":arch_g3,"g4":arch_g4,"g5":arch_g5})

