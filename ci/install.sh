#!/bin/sh

set -ex

main() {
    curl https://sh.rustup.rs -sSf > rustup-init.sh
    sh rustup-init.sh --default-toolchain nightly -y -v
    export PATH="$HOME/.cargo/bin:$PATH"
    which rustc
    rustc --version
    pip install pipenv
    apt-get update && apt-get install libdbus-1-3
    cargo install pyo3-pack
    make install
    pipenv graph
}

main
