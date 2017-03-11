#!/usr/bin/python
# Copyright (C) 2011 Sebastian Pipping <sebastian@pipping.org>
# Copyright (C) 2013 Brian dolbec <dolsen@gentoo.org>
# Licensed under GPL v2 or later


import os
import re
import sys
import textwrap


_pattern_arch_generic = re.compile('^class arch_([a-z0-9_.-]+)\\(generic_([a-z0-9_.-]+)\\):')
_pattern_arch_arch = re.compile('^class arch_([a-z0-9_.-]+)\\(arch_([a-z0-9_.-]+)\\):')
_pattern_title = re.compile('"([a-z0-9_.-]+)"[ \\t]*:[ \\t]*arch_([a-z0-9_.-]+),?')

_pattern_arch_genericliases = {
	'armeb':'arm',
	'sheb':'sh',
	'mipsel':'mips',
	'mips64el':'mips64',
}


def handle_line(line, subarch_title_to_subarch_id, subarch_id_to_pattern_arch_genericrch_id):
	x = _pattern_arch_generic.search(line)
	if x is not None:
		subarch = x.group(1)
		arch = x.group(2)

		# Apply alias grouping
		arch = _pattern_arch_genericliases.get(arch, arch)

		assert subarch not in subarch_id_to_pattern_arch_genericrch_id
		subarch_id_to_pattern_arch_genericrch_id[subarch] = arch

		return

	x = _pattern_arch_arch.search(line)
	if x is not None:
		child_subarch = x.group(1)
		parent_subarch = x.group(2)

		assert child_subarch not in subarch_id_to_pattern_arch_genericrch_id
		subarch_id_to_pattern_arch_genericrch_id[child_subarch] = subarch_id_to_pattern_arch_genericrch_id[parent_subarch]

		return

	for x in re.finditer(_pattern_title, line):
		subarch_title = x.group(1)
		subarch_id = x.group(2)

		assert subarch_title not in subarch_title_to_subarch_id
		subarch_title_to_subarch_id[subarch_title] = subarch_id


def handle_file(fn, subarch_title_to_subarch_id, subarch_id_to_pattern_arch_genericrch_id):
	f = open(fn, 'r')
	for l in f:
		line = l.rstrip()
		handle_line(line, subarch_title_to_subarch_id, subarch_id_to_pattern_arch_genericrch_id)
	f.close()


def dump(subarch_title_to_subarch_id, subarch_id_to_pattern_arch_genericrch_id):
	arch_id_to_subarch_titles = dict()
	for subarch_title, subarch_id in subarch_title_to_subarch_id.items():
		arch_id = subarch_id_to_pattern_arch_genericrch_id.get(subarch_id, subarch_id)

		if arch_id not in arch_id_to_subarch_titles:
			arch_id_to_subarch_titles[arch_id] = set()
		arch_id_to_subarch_titles[arch_id].add(subarch_title)

	# GuideXML version
	f = open('doc/subarches.generated.xml', 'w')
	f.write("""
<table>
<tr>
<th>Architecture</th>
<th>Sub-architectures</th>
</tr>
""")
	for arch_id, subarch_titles in sorted(arch_id_to_subarch_titles.items()):
		f.write("""<tr>
<ti><c>%s</c></ti>
<ti><c>%s</c></ti>
</tr>
""" % (arch_id, '\n'.join(textwrap.wrap(' '.join(sorted(subarch_titles)), 60))))

	f.write("""</table>
""")
	f.close()

	# Asciidoc
	f = open('doc/subarches.generated.txt', 'w')
	for arch_id, subarch_titles in sorted(arch_id_to_subarch_titles.items()):
		f.write('*%s*::\n' % arch_id)
		f.write('    %s\n' % ', '.join(sorted(subarch_titles)))
		f.write('\n')
	f.close()


def main(_argv):
	subarch_title_to_subarch_id = dict()
	subarch_id_to_pattern_arch_genericrch_id = dict()

	for dirpath, _dirnames, filenames in os.walk('catalyst/arch'):
		for _fn in filenames:
			if not _fn.endswith('.py'):
				continue
			if _fn == '__init__.py':
				continue

			fn = os.path.join(dirpath, _fn)
			handle_file(fn, subarch_title_to_subarch_id, subarch_id_to_pattern_arch_genericrch_id)

	dump(subarch_title_to_subarch_id, subarch_id_to_pattern_arch_genericrch_id)


if __name__ == '__main__':
	main(sys.argv[1:])
