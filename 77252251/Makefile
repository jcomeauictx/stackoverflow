SHELL := /bin/bash
SOURCES := $(wildcard *.py)
LINT := $(SOURCES:.py=.pylint)
TEST := $(SOURCES:.py=.doctest)
PYTHON := $(shell which python3 python false | head -n 1)
PYLINT := $(shell which pylint3 pylint true | head -n 1)
DOCTEST := $(PYTHON) -m doctest
PROXY := localhost:8080
WGET := http_proxy=$(PROXY) wget -q -O- 
%.pylint: %.py
	$(PYLINT) $<
%.doctest: %.py
	$(DOCTEST) $<
all: $(LINT) $(TEST) serve proxy wait test stop
fast: serve test
serve: server.py
	$(PYTHON) $< &
wait:
	@echo giving server and/or mitmproxy a chance to start...
	@sleep 1
test:
	-for try in $$(seq 0 5); do $(WGET) http://localhost:8000/; done
stop:
	-kill $$(lsof -t -itcp:8080 -s tcp:listen)  # kill mitmdump
	-kill $$(lsof -t -itcp:8000 -s tcp:listen)  # kill webserver
proxy:
	# mitmdump using default listen-port 8080
	mitmdump --anticache \
	 --anticomp \
	 --listen-host localhost \
	 --scripts filter.py \
	 --flow-detail 3 \
	 --save-stream-file mitmproxy.log &>mitmdump.log &
