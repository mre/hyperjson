#!/bin/sh

# This script takes care of building your crate and packaging it for release

set -ex

main() {
    python3 setup.py sdist
    python3 setup.py bdist_wheel
    python3 setup.py bdist_rpm
    # python3 setup.py bdist_wininst
}

main
