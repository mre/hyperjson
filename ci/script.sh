#!/bin/sh

# This script takes care of testing your crate

set -ex

# This is the "test phase", tweak it as you see fit
main() {
    if [ ! -z $DISABLE_TESTS ]; then
        return
    fi

    export PATH="$HOME/.cargo/bin:$PATH"

    pip show setuptools-rust 2>&1 1>/dev/null || \
        pip install setuptools-rust
    pip install -r requirements-test.txt
    pip freeze
    which rustc
    rustc --version
    python setup.py test
}

main
