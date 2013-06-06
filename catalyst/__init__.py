"Catalyst is a release building tool used by Gentoo Linux"

try:
	from .verinfo import version as fullversion
	__version__ = fullversion.split('\n')[0].split()[1]
except ImportError:
	from .version import get_version, __version__
	fullversion = get_version(reset=True)
