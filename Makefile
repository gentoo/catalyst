# Copyright (C) 2011 Sebastian Pipping <sebastian@pipping.org>
# Licensed under GPL v2 or later

PACKAGE_VERSION = `fgrep '__version__=' catalyst | sed 's|^__version__="\(.*\)"$$|\1|'`
MAN_PAGES = catalyst.1 catalyst-spec.5
MAN_PAGE_INCLUDES = doc/subarches.generated.txt doc/targets.generated.txt
EXTRA_DIST = $(MAN_PAGES:%=files/%)
CLEAN_FILES = $(EXTRA_DIST) $(MAN_PAGE_INCLUDES)

distdir = catalyst-$(PACKAGE_VERSION)


all: $(EXTRA_DIST)

$(MAN_PAGES:%=files/%): files/%: doc/%.txt $(MAN_PAGE_INCLUDES) doc/asciidoc.conf Makefile catalyst
	a2x --conf-file=doc/asciidoc.conf --attribute="catalystversion=$(PACKAGE_VERSION)" \
		 --format=manpage -D files "$<"

doc/subarches.generated.txt: $(wildcard arch/*.py) doc/make_subarch_table_guidexml.py
	./doc/make_subarch_table_guidexml.py

doc/targets.generated.txt: doc/make_target_table.py $(wildcard modules/catalyst/targets/*.py)
	"./$<" > "$@"

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
