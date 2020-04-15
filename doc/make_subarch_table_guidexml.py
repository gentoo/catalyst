#!/usr/bin/env python
# Licensed under GPL v2 or later


import pathlib
import sys
import textwrap
import toml


def write_guidexml(arch_to_subarch):
    with open('doc/subarches.generated.xml', 'w') as f:
        f.write(textwrap.dedent("""\
			<table>
			<tr>
			<th>Architecture</th>
			<th>Sub-architectures</th>
			</tr>
			"""))
        for arch, subarches in sorted(arch_to_subarch.items()):
            f.write(textwrap.dedent("""\
				<tr>
				<ti><c>%s</c></ti>
				<ti><c>%s</c></ti>
				</tr>
				""") % (arch, '\n'.join(textwrap.wrap(' '.join(sorted(subarches)), 60))))
        f.write("</table>\n")


def write_asciidoc(arch_to_subarch):
    with open('doc/subarches.generated.txt', 'w') as f:
        for arch, subarches in sorted(arch_to_subarch.items()):
            f.write('*%s*::\n' % arch)
            f.write('    %s\n' % ', '.join(sorted(subarches)))
            f.write('\n')


def main(_argv):
    arch_to_subarch = {}
    p = pathlib.Path('arch')

    for file in p.glob('*.toml'):
        data = toml.load(file)

        for arch in [x for x in data if x != 'setarch']:
            arch_to_subarch.update({arch: list(data[arch].keys())})

    write_guidexml(arch_to_subarch)
    write_asciidoc(arch_to_subarch)


if __name__ == '__main__':
    main(sys.argv[1:])
