# Copyright 1999-2005 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/arch/sparc.py,v 1.7 2006/01/03 14:55:11 wolf31o2 Exp $

import builder,os
from catalyst_support import *

class generic_sparc(builder.generic):
	"abstract base class for all sparc builders"
	def __init__(self,myspec):
		builder.generic.__init__(self,myspec)
		self.settings["mainarch"]="sparc"
		if self.settings["hostarch"]=="sparc64":
			if not os.path.exists("/usr/bin/sparc32"):
				raise CatalystError,"required /usr/bin/sparc32 executable not found (\"emerge sparc-utils\" to fix.)"
			self.settings["CHROOT"]="/usr/bin/sparc32 chroot"
		else:
			self.settings["CHROOT"]="chroot"

class arch_sparc(generic_sparc):
	"builder class for generic sparc (sun4cdm)"
	def __init__(self,myspec):
		generic_sparc.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -pipe"
		self.settings["CXXFLAGS"]="-O2 -pipe"
		self.settings["CHOST"]="sparc-unknown-linux-gnu"

def register(foo):
	"Inform main catalyst program of the contents of this plugin."
	foo.update({"sparc":arch_sparc})
