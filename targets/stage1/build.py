#!/usr/bin/python3

import os
import sys
import portage
from portage.util import grabfile_package, stack_lists

# this loads files from the profiles ...
# wrap it here to take care of the different
# ways portage handles stacked profiles
# last case is for portage-2.1_pre*
def scan_profile(path):
	return stack_lists([grabfile_package(os.path.join(x, path)) for x in portage.settings.profiles], incremental=1)

# loaded the stacked packages / packages.build files
pkgs = scan_profile("packages")
buildpkgs = scan_profile("packages.build")

# go through the packages list and strip off all the
# crap to get just the <category>/<package> ... then
# search the buildpkg list for it ... if it's found,
# we replace the buildpkg item with the one in the
# system profile (it may have <,>,=,etc... operators
# and version numbers)
for idx in range(0, len(pkgs)):
	try:
		bidx = buildpkgs.index(portage.dep_getkey(pkgs[idx]))
		buildpkgs[bidx] = pkgs[idx]
		if buildpkgs[bidx][0:1] == "*":
			buildpkgs[bidx] = buildpkgs[bidx][1:]
	except Exception:
		pass

for b in buildpkgs:
	sys.stdout.write(b + " ")
