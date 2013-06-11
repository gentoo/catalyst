# Maintained in full by:
# Catalyst Team <catalyst@gentoo.org>
# Release Engineering Team <releng@gentoo.org>
# Copyright: 2011 Brian Harring <ferringb@gmail.com>
# License: BSD/GPL2
# Copied & edited by: Brian Dolbec <dolsen@gentoo.org>

'''Version information and/or git version information
'''

from snakeoil.version import format_version

__version__="rewrite-git"
_ver = None

def get_version():
	"""Return: a string describing our version."""
	global _ver
	if _ver is None:
		_ver = format_version('catalyst',__file__, __version__)
	return _ver
