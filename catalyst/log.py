# Copyright 2003-2015 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2

"""Logging related code

This largely exposes the same interface as the logging module except we add
another level "notice" between warning & info, and all output goes through
the "catalyst" logger.
"""

import logging
import logging.handlers
import os
import sys
import time


class CatalystLogger(logging.Logger):
    """Override the _log member to autosplit on new lines"""

    def _log(self, level, msg, args, **kwargs):
        """If given a multiline message, split it"""

        # Increment stacklevel to hide this function call
        stacklevel = kwargs.get("stacklevel", 1)
        kwargs["stacklevel"] = stacklevel + 1

        # We have to interpolate it first in case they spread things out
        # over multiple lines like: Bad Thing:\n%s\nGoodbye!
        msg %= args
        for line in msg.splitlines():
            super(CatalystLogger, self)._log(level, line, (), **kwargs)


# The logger that all output should go through.
# This is ugly because we want to not perturb the logging module state.
_klass = logging.getLoggerClass()
logging.setLoggerClass(CatalystLogger)
logger = logging.getLogger('catalyst')
logging.setLoggerClass(_klass)
del _klass


# Set the notice level between warning and info.
NOTICE = (logging.WARNING + logging.INFO) // 2
logging.addLevelName(NOTICE, 'NOTICE')


# The API we expose to consumers.
def notice(msg, *args, **kwargs):
    """Log a notice message"""

    # Increment stacklevel to hide this function call
    stacklevel = kwargs.get("stacklevel", 1)
    kwargs["stacklevel"] = stacklevel + 1

    logger.log(NOTICE, msg, *args, **kwargs)


def critical(msg, *args, **kwargs):
    """Log a critical message and then exit"""

    # Increment stacklevel to hide this function call
    stacklevel = kwargs.get("stacklevel", 1)
    kwargs["stacklevel"] = stacklevel + 1

    status = kwargs.pop('status', 1)
    logger.critical(msg, *args, **kwargs)
    sys.exit(status)


error = logger.error
warning = logger.warning
info = logger.info
debug = logger.debug


class CatalystFormatter(logging.Formatter):
    """Mark bad messages with colors automatically"""

    _COLORS = {
        'CRITICAL':	'\033[1;35m',
        'ERROR':	'\033[1;31m',
        'WARNING':	'\033[1;33m',
        'DEBUG':	'\033[1;34m',
    }
    _NORMAL = '\033[0m'

    @staticmethod
    def detect_color():
        """Figure out whether the runtime env wants color"""
        if 'NOCOLOR' in os.environ:
            return False
        return os.isatty(sys.stdout.fileno())

    def __init__(self, *args, **kwargs):
        """Initialize"""
        color = kwargs.pop('color', None)
        if color is None:
            color = self.detect_color()
        if not color:
            self._COLORS = {}

        super(CatalystFormatter, self).__init__(*args, **kwargs)

    def format(self, record, **kwargs):
        """Format the |record| with our color settings"""
        msg = super(CatalystFormatter, self).format(record, **kwargs)
        color = self._COLORS.get(record.levelname)
        if color:
            return color + msg + self._NORMAL
        return msg


# We define |debug| in global scope so people can call log.debug(), but it
# makes the linter complain when we have a |debug| keyword.  Since we don't
# use that func in here, it's not a problem, so silence the warning.
# pylint: disable=redefined-outer-name
def setup_logging(level, output=None, debug=False, color=None):
    """Initialize the logging module using the |level| level"""
    # The incoming level will be things like "info", but setLevel wants
    # the numeric constant.  Convert it here.
    level = logging.getLevelName(level.upper())

    # The good stuff.
    fmt = '%(asctime)s: %(levelname)-8s: '
    if debug:
        fmt += '%(filename)s:%(funcName)s:%(lineno)d: '
    fmt += '%(message)s'

    # Figure out where to send the log output.
    if output is None:
        handler = logging.StreamHandler(stream=sys.stdout)
    else:
        handler = logging.FileHandler(output)

    # Use a date format that is readable by humans & machines.
    # Think e-mail/RFC 2822: 05 Oct 2013 18:58:50 EST
    tzname = time.strftime('%Z', time.localtime())
    datefmt = '%d %b %Y %H:%M:%S ' + tzname
    formatter = CatalystFormatter(fmt, datefmt, color=color)
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    logger.setLevel(level)
