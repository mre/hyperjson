# Needed SHELL since I'm using zsh
SHELL := /bin/bash

ts := $(shell date -u +"%Y-%m-%dT%H:%M:%SZ")

.PHONY: help
help: ## This help message
	@echo -e "$$(grep -hE '^\S+:.*##' $(MAKEFILE_LIST) | sed -e 's/:.*##\s*/:/' -e 's/^\(.\+\):\(.*\)/\\x1b[36m\1\\x1b[m:\2/' | column -c2 -t -s :)"

.PHONY: build
build: nightly dev-packages ## Builds Rust code and hyperjson Python modules
	pipenv run maturin build

.PHONY: build-release
build-release: nightly dev-packages ## Build hyperjson module in release mode
	pipenv run maturin build --release

.PHONY: nightly
nightly: ## Set rust compiler to nightly version
	rustup override set nightly

.PHONY: install
install: nightly dev-packages ## Install hyperjson module into current virtualenv
	pipenv run maturin develop --release

.PHONY: publish
publish: ## Publish crate on Pypi
	pipenv run maturin publish

.PHONY: clean
clean: ## Clean up build artifacts
	pipenv --rm || true
	cargo clean

.PHONY: dev-packages
dev-packages: ## Install Python development packages for project
	pipenv install --dev

.PHONY: test
test: dev-packages install quicktest ## Intall hyperjson module and run tests

.PHONY: quicktest
quicktest: ## Run tests on already installed hyperjson module
	pipenv run pytest tests

.PHONY: bench
bench: ## Run benchmarks
	pipenv run pytest benchmarks

.PHONY: bench-compare
bench-compare: ## Run benchmarks and compare results with other JSON encoders
	pipenv run pytest benchmarks --compare

.PHONY: plot
plot: bench-compare ## Plot graph from benchmarks
	@echo "Rendering plots from benchmarks"
	pipenv run python benchmarks/histogram.py

.PHONY: build-profile
build-profile: ## Builds binary for profiling
	cd profiling && pipenv run cargo build --release

# Setup instructions here:
# https://gist.github.com/dlaehnemann/df31787c41bd50c0fe223df07cf6eb89
.PHONY: profile
profile: OUTPUT_PATH = measurements/flame-$(ts).svg
profile: FLAGS=booleans --iterations 10000
profile: nightly build-profile ## Run perf-based profiling (only works on Linux!)
	perf record --call-graph dwarf,16384 -e cpu-clock -F 997 target/release/profiling $(FLAGS)
	time perf script | stackcollapse-perf.pl | c++filt | flamegraph.pl > $(OUTPUT_PATH)
	@echo "$(OUTPUT_PATH)"

