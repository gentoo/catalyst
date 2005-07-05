# Copyright 1999-2005 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/arch/ppc64.py,v 1.3 2005/07/05 21:53:41 wolf31o2 Exp $

import builder

class generic_ppc64(builder.generic):
	"abstract base class for all ppc64 builders"
	def __init__(self,myspec):
		builder.generic.__init__(self,myspec)
		self.settings["mainarch"]="ppc64"
		self.settings["CHROOT"]="chroot"

class arch_ppc64(generic_ppc64):
	"builder class for generic ppc64 (G5/Power4/Power4+)"
	def __init__(self,myspec):
		generic_ppc64.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2"
		self.settings["CHOST"]="powerpc64-unknown-linux-gnu"

def register(foo):
	"Inform main catalyst program of the contents of this plugin."
	foo.update({"ppc64":arch_ppc64})
		
