DIR := $(shell basename $(CURDIR))

.PHONY: build
build: nightly
	cargo build

.PHONY: nightly
nightly:
	rustup override set nightly

.PHONY: install2
install2: nightly
	pipenv install --dev
	python2 setup.py install

.PHONY: install
install: nightly
	pipenv install --dev
	python3 setup.py install

.PHONY: test
test:
	pytest tests

.PHONY: bench
bench:
	pytest benchmarks

.PHONY: bench-all
bench-all:
	pytest benchmarks --compare --benchmark-json=benchmark
	@echo "Rendering plots from benchmarks"
	python benchmarks/histogram.py