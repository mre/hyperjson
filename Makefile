DIR := $(shell basename $(CURDIR))

.PHONY: build
build: nightly
	cargo build

.PHONY: nightly
nightly:
	rustup override set nightly

.PHONY: install2
install2: nightly
	python2 setup.py install

.PHONY: install
install: nightly
	python3 setup.py install

.PHONY: test
test:
	pytest tests

.PHONY: bench
bench:
	pytest benchmarks

.PHONY: bench-all
bench-all:
	pytest benchmarks --compare