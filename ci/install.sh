#!/bin/sh

set -ex

main() {
    curl https://sh.rustup.rs -sSf > rustup-init.sh
    sh rustup-init.sh --default-toolchain nightly -y
    # pip install -r requirements.txt
    pip install .
    pip freeze
}

main
