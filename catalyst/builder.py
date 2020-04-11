class generic():
	def __init__(self,myspec):
		self.settings=myspec
		self.settings.setdefault('CHROOT', 'chroot')

	def setarch(self, arch):
		"""Set the chroot wrapper to run through `setarch |arch|`

		Useful for building x86-on-amd64 and such.
		"""
		self.settings['CHROOT'] = 'setarch %s %s' % (arch, self.settings['CHROOT'])
