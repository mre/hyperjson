.PHONY: nightly
nightly:
	rustup override set nightly

.PHONY: build
build: nightly
	cargo build

.PHONY: install
install: nightly
	python setup.py install
	python3 setup.py install

.PHONY: test
test:
	pytest --verbose --capture=no