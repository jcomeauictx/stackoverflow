SHELL := /bin/bash
SOURCES := $(wildcard *.py)
LINT := $(SOURCES:.py=.pylint)
TEST := $(SOURCES:.py=.doctest)
PYTHON := $(shell which python3 python false | head -n 1)
PYLINT := $(shell which pylint3 pylint true | head -n 1)
DOCTEST := $(PYTHON) -m doctest
%.pylint: %.py
	$(PYLINT) $<
%.doctest: %.py
	$(DOCTEST) $<
all: $(LINT) $(TEST) serve wait test
fast: serve test
serve: server.py
	$(PYTHON) $< &
wait:
	@echo giving server a chance to start...
	@sleep 1
test:
	for try in $$(seq 0 6); do wget -q -O- http://localhost:8000/; done
