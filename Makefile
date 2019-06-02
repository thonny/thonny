DESTDIR =
SUBDIRS = thonny/locale
all:
	for d in $(SUBDIRS); do make -C $$d $@ DESTDIR=$(DESTDIR); done

clean:
	find . -name __pycache__ -o name "*~" | xargs rm -rf
	for d in $(SUBDIRS); do make -C $$d $@ DESTDIR=$(DESTDIR); done

install: all
	for d in $(SUBDIRS); do make -C $$d $@ DESTDIR=$(DESTDIR); done

.PHONY: all clean install
