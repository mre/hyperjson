.PHONY: build
build: nightly
	cargo build

.PHONY: nightly
nightly:
	rustup override set nightly

.PHONY: install
install: nightly
	pyo3-pack build

.PHONY: clean
clean:
	pipenv --rm || true
	cargo clean

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

.PHONY: profile-mac
profile-mac: nightly
	cargo build --bin hyperjson-bench
	pipenv shell && sudo macos-profiler time-spent --command ./target/debug/hyperjson-bench	&& exit

