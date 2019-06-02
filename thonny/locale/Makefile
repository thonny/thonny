DESTDIR =

SOURCES = $(shell find .. -name '*.py')
POFILES = $(shell find . -name "*.po")
MOFILES = $(patsubst %.po, %.mo, $(POFILES))
LANG = $(patsubst %.po, %, $(POFILES))

LOCALEDIR = .

all: $(MOFILES)

%.mo: %.po
	pybabel compile -d . -D thonny

$(POFILES): thonny.pot
	pybabel update -D thonny -i ./thonny.pot -d .

thonny.pot: $(SOURCES)
	pybabel extract .. --output-file thonny.pot

clean:
	rm -f *.mo *~

install: all
	for l in $(LANG); do \
	  install -d $(LOCALEDIR)/$$l/LC_MESSAGES; \
	  install -m 644 $$l.mo $(LOCALEDIR)/$$l/LC_MESSAGES/thonny.mo; \
	done

.PHONY: all clean install
