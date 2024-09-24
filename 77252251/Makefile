SHELL := /bin/bash
PATH := /usr/bin:/usr/sbin:/usr/local/bin
SOURCES := $(wildcard *.py)
LINT := $(SOURCES:.py=.pylint)
TEST := $(SOURCES:.py=.doctest)
PYTHON := $(shell which python3 python false | head -n 1)
PYLINT := $(shell which pylint3 pylint true | head -n 1)
MITMDUMP := $(shell which mitmdump false | head -n 1)
DOCTEST := $(PYTHON) -m doctest
PROXY := localhost:8080
WGET := http_proxy=$(PROXY) wget -v -O-
FILTER ?= filter.py
TESTS = 2  # one for each strategy
ifneq ($(SHOWENV),)
 export
else
 export PATH
endif
%.pylint: %.py
	$(PYLINT) $<
%.doctest: %.py
	$(DOCTEST) $<
# run stop before as well as after, in case error caused `make` to fail
all: $(LINT) $(TEST) stop serve proxy wait test stop
fast: stop serve proxy test stop
serve: server.py
	$(PYTHON) $< 2>&1 | tee server.log &
wait:
	@echo giving server and/or mitmproxy a chance to start...
	@sleep 1
test:  # one fetch for each strategy we want to test
	-for test in $$(seq 1 $(TESTS)); do \
	 $(WGET) http://localhost:8000/; \
	done
stop: .FORCE
	# kill mitmdump if running
	if [ "$$(lsof -t -itcp:8080 -s tcp:listen)" ]; then \
	 kill $$(lsof -t -itcp:8080 -s tcp:listen); \
	else \
	 echo mitmdump was already not running >&2; \
	fi
	# kill webserver if running
	if [ "$$(lsof -t -itcp:8000 -s tcp:listen)" ]; then \
	 kill $$(lsof -t -itcp:8000 -s tcp:listen); \
	else \
	 echo webserver was already not running >&2; \
	fi
proxy:
	# mitmdump using default listen-port 8080
	$(MITMDUMP) --anticache \
	 --anticomp \
	 --listen-host localhost \
	 --scripts $(FILTER) \
	 --flow-detail 3 \
	 --save-stream-file mitmproxy.log &>mitmdump.log &
env:
ifeq ($(SHOWENV),)
	$(MAKE) SHOWENV=1 $@
else
	$@
endif
test_replay:
	$(MAKE) FILTER=replay.py TESTS=1 stop serve proxy wait test stop
.FORCE:
