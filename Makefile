# Copyright (C) 2011 Sebastian Pipping <sebastian@pipping.org>
# Licensed under GPL v2 or later

PACKAGE_VERSION = `fgrep '__version__=' catalyst | sed 's|^__version__="\(.*\)"$$|\1|'`
CLEAN_FILES = files/catalyst.1 doc/subarches.generated.txt
EXTRA_DIST = files/catalyst.1

distdir = catalyst-$(PACKAGE_VERSION)


all: files/catalyst.1

files/catalyst.1: doc/catalyst.1.txt doc/subarches.generated.txt doc/asciidoc.conf Makefile catalyst
	a2x --conf-file=doc/asciidoc.conf --attribute="catalystversion=$(PACKAGE_VERSION)" \
		 --format=manpage -D files "$<"

doc/subarches.generated.txt:
	./doc/make_subarch_table_guidexml.py

clean:
	rm -f $(CLEAN_FILES)
	find -name '*.pyo' -delete

check-git-repository:
	git diff --quiet || { echo 'STOP, you have uncommitted changes in the working directory' ; false ; }
	git diff --cached --quiet || { echo 'STOP, you have uncommitted changes in the index' ; false ; }

dist: check-git-repository $(EXTRA_DIST)
	rm -Rf "$(distdir)" "$(distdir)".tar "$(distdir)".tar.bz2
	mkdir "$(distdir)"
	git ls-files -z | xargs -0 cp --no-dereference --parents --target-directory="$(distdir)" \
		$(EXTRA_DIST)
	tar cf "$(distdir)".tar "$(distdir)"
	bzip2 -9v "$(distdir)".tar
	rm -Rf "$(distdir)"
