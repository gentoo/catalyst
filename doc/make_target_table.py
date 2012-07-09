#!/usr/bin/env python
# Copyright (C) 2012 W. Trevor King <wking@drexel.edu>
# Copyright (C) 2012 Sebastian Pipping <sebastian@pippin.org>
# Licensed under GPL v2 or later

# This script should be run from the root of the catalyst source.

from __future__ import print_function

import sys as _sys

_sys.path.insert(0, 'modules')  # so we can find the `catalyst` module

import glob
import re


if __name__ == '__main__':
	extractor = re.compile('^modules/(([^ ]+)_target).py$')
	for filename in sorted(glob.glob('modules/*_target.py')):
		if 'generic' in filename:
			continue

		match = extractor.match(filename)
		target_name = match.group(2).replace('_', '-')
		module_name = match.group(1)

		__import__(module_name)
		module = _sys.modules[module_name]

		print('`%s`;;' % target_name)
		# Replace blank lines with `+` (asciidoc list item continuation)
		print(module.__doc__.strip().replace('\n\n', '\n+\n'))
		print('')
