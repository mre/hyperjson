#!/bin/sh

# This script takes care of testing your crate

set -ex

# This is the "test phase", tweak it as you see fit
main() {
    if [ ! -z $DISABLE_TESTS ]; then
        return
    fi

    pip3 show setuptools-rust 2>&1 1>/dev/null || \
        pip3 install setuptools-rust
    pip3 install -r requirements-test.txt
    python3 setup.py test
}

main
