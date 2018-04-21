.PHONY: build
build:
	cargo build

.PHONY: install
install:
	python setup.py install
	python3 setup.py install

.PHONY: test
test:
	pytest -v