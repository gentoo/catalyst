'''Version information and/or git version information
'''

import os

from snakeoil.version import get_git_version as get_ver

__version__ = "4.0.0"
_ver = None


def get_git_version(version=__version__):
    """Return: a string describing our version."""
    # pylint: disable=global-statement
    global _ver
    cwd = os.path.dirname(os.path.abspath(__file__))
    version_info = get_ver(cwd)

    if not version_info:
        s = "extended version info unavailable"
    elif version_info['tag'] == __version__:
        s = 'released %s' % (version_info['date'],)
    else:
        s = ('vcs version %s, date %s' %
             (version_info['rev'], version_info['date']))

    _ver = 'Catalyst %s\n%s' % (version, s)

    return _ver


def get_version(reset=False):
    '''Returns a saved release version string or the
    generated git release version.
    '''
    # pylint: disable=global-statement
    global __version__, _ver
    if _ver and not reset:
        return _ver
    try:  # getting the fixed version
        from .verinfo import version
        _ver = version
        __version__ = version.split('\n')[0].split()[1]
    except ImportError:  # get the live version
        version = get_git_version()
    return version


def set_release_version(version, root=None):
    '''Saves the release version along with the
    git log release information

    @param version: string
    @param root: string, optional alternate root path to save to
    '''
    #global __version__
    filename = "verinfo.py"
    if not root:
        path = os.path.join(os.path.dirname(__file__), filename)
    else:
        path = os.path.join(root, filename)
    #__version__ = version
    ver = get_git_version(version)
    with open(path, 'w') as f:
        f.write("version = {0!r}".format(ver))
