.PHONY: build
build: nightly
	cargo build

.PHONY: nightly
nightly:
	rustup override set nightly


.PHONY: install
install: nightly
	python3 setup.py install

.PHONY: test
test:
	pytest --verbose --capture=no