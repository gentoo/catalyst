#!/usr/bin/env python
# Copyright (C) 2012 W. Trevor King <wking@drexel.edu>
# Licensed under GPL v2 or later

# This script should be run from the root of the catalyst source.

import sys as _sys

_sys.path.insert(0, 'modules')  # so we can find the `catalyst` module

import catalyst.target as _catalyst_target


if __name__ == '__main__':
    for module_name,module in sorted(_catalyst_target.get_targets().items()):
        if hasattr(module, '__target_map'):
            target_name = module.__target_map.keys()[0]
            print('`{}`;;'.format(target_name))
            # Replace blank lines with `+` (asciidoc list item continuation)
            print(module.__doc__.strip().replace('\n\n', '\n+\n'))
            print('')
