DESTDIR =

all:
	make -C locale all DESTDIR=$(DESTDIR)

clean:
	find . -name __pycache__ -o name "*~" | xargs rm -rf
	make -C locale clean DESTDIR=$(DESTDIR)

install: all
	make -C locale install DESTDIR=$(DESTDIR)

.PHONY: all clean install
