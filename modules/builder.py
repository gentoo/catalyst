# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/modules/builder.py,v 1.6 2004/06/08 04:07:34 zhen Exp $

class generic:
	def __init__(self,myspec):
		self.settings=myspec
	def mount_safety_check(self):
		"""make sure that no bind mounts exist in chrootdir (to use before
		cleaning the directory, to make sure we don't wipe the contents of
		a bind mount"""
		pass
	def mount_all(self):
		"""do all bind mounts"""
		pass
	def umount_all(self):
		"""unmount all bind mounts"""
		pass
