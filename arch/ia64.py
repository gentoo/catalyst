# Copyright 1999-2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/arch/ia64.py,v 1.3 2004/10/15 02:36:00 zhen Exp $

import builder,os
from catalyst_support import *

class arch_ia64(builder.generic):
	"builder class for ia64"
	def __init__(self,myspec):
		builder.generic.__init__(self,myspec)
		self.settings["mainarch"]="ia64"
		self.settings["CHROOT"]="chroot"
		self.settings["CFLAGS"]="-O2"
		self.settings["CHOST"]="ia64-unknown-linux-gnu"

def register(foo):
	"Inform main catalyst program of the contents of this plugin."
	foo.update({ "ia64":arch_ia64 })
