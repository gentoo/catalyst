# Copyright 1999-2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/arch/ppc.py,v 1.11 2004/10/15 02:36:00 zhen Exp $

import os,builder
from catalyst_support import *

# gcc-3.3.3 required to do G5 optimizations
# install a 32bit kernel personality changer (that works) before building on a ppc64 host
# new gcc optimization feature requires -fno-strict-aliasing needed, otherwise code complains 
# use the experimental thing for nptl builds

class generic_ppc(builder.generic):
	"abstract base class for all ppc builders"
	def __init__(self,myspec):
		builder.generic.__init__(self,myspec)
		self.settings["mainarch"]="ppc"
		self.settings["CHOST"]="powerpc-unknown-linux-gnu"
		if self.settings["hostarch"]=="ppc64":
			if not os.path.exists("/usr/bin/powerpc32"):
				raise CatalystError,"required /usr/bin/setarch executable not found."
			self.settings["CHROOT"]="/usr/bin/powerpc32 chroot"
		else:   
			self.settings["CHROOT"]="chroot"

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
		self.settings["CFLAGS"]="-O3 -mcpu=G3 -fno-strict-aliasing -pipe"

class arch_g4(generic_ppc):
	def __init__(self,myspec):
		generic_ppc.__init__(self,myspec)
		self.settings["CFLAGS"]="-O3 -mcpu=G4 -maltivec -mabi=altivec -fno-strict-aliasing -pipe"
		self.settings["HOSTUSE"]=["altivec"]

class arch_g5(generic_ppc):
	def __init__(self,myspec):
		generic_ppc.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -mcpu=G5 -maltivec -mabi=altivec -fno-strict-aliasing -pipe"
		self.settings["HOSTUSE"]=["altivec"]

class arch_experimental(generic_ppc):
	def __init__(self,myspec):
		generic_ppc.__init__(self,myspec)
		self.settings["CFLAGS"]="-O3 -mcpu=7450 -maltivec -mabi=altivec -fno-strict-aliasing"
		self.settings["HOSTUSE"]=["altivec"]
	
def register(foo):
	"Inform main catalyst program of the contents of this plugin."
	foo.update({"experimental":arch_experimental,"ppc":arch_ppc,"power":arch_power,"power-ppc":arch_power_ppc,"g3":arch_g3,"g4":arch_g4,"g5":arch_g5})

