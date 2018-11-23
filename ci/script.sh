#!/bin/sh

# This script takes care of testing your crate

set -ex

# This is the "test phase", tweak it as you see fit
main() {
    if [ ! -z $DISABLE_TESTS ]; then
        return
    fi

    export PATH="$HOME/.cargo/bin:$PATH"

    make test
    make bench-all
}

main
