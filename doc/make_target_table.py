#!/usr/bin/env python
# Copyright (C) 2012 W. Trevor King <wking@drexel.edu>
# Copyright (C) 2012 Sebastian Pipping <sebastian@pipping.org>
# Copyright (C) 2013 Brian dolbec <dolsen@gentoo.org>
# Licensed under GPL v2 or later

# This script should be run from the root of the catalyst source.
# source the testpath file then run "doc/make_target_table.py"


import glob
import locale
import os
import sys


def main(_argv):
    source_root = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

    # Force consistent sorting order.
    locale.setlocale(locale.LC_COLLATE, 'C')

    targets = list()
    for filename in glob.glob(os.path.join(source_root, 'catalyst/targets/*.py')):
        if '__init__' in filename:
            continue

        name = os.path.basename(filename)[0:-3]
        target_name = name.replace('_', '-')
        module_name = 'catalyst.targets.' + name

        __import__(module_name)
        module = sys.modules[module_name]

        targets.append((target_name, module))

    for target_name, module in sorted(targets, key=lambda x: x[0]):
        print('`%s`;;' % target_name)
        # Replace blank lines with `+` (asciidoc list item continuation)
        print(module.__doc__.strip().replace('\n\n', '\n+\n'))
        print('')


if __name__ == '__main__':
    main(sys.argv[1:])
