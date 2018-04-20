.PHONY: build
build:
	cargo build

.PHONY: install
install:
	python setup.py install

.PHONY: test
test:
	pytest -v