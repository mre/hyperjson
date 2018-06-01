#!/bin/sh

# This script takes care of building your crate and packaging it for release

set -ex

main() {
    python setup.py sdist
    python setup.py bdist_wheel
    python setup.py bdist_rpm
    # python setup.py bdist_wininst
}

main
