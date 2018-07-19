.PHONY: build
build: nightly
	cargo build

.PHONY: nightly
nightly:
	rustup override set nightly

.PHONY: install
install: nightly
	pipenv install --dev
	pipenv run python setup.py install

.PHONY: test
test:
	pipenv run pytest tests

.PHONY: bench
bench:
	pipenv run pytest benchmarks

.PHONY: bench-all
bench-all:
	pipenv run pytest benchmarks --compare
	
.PHONY: plot
plot:
	pipenv run pytest benchmarks --compare --benchmark-json=benchmark.json
	@echo "Rendering plots from benchmarks"
	pipenv run python benchmarks/histogram.py