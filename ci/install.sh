#!/bin/sh

set -ex

main() {
    curl https://sh.rustup.rs -sSf > rustup-init.sh
    sh rustup-init.sh --default-toolchain nightly -y -v
    export PATH="$HOME/.cargo/bin:$PATH"
    which rustc
    rustc --version
    curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python
    source ~/.poetry/env
    cargo install maturin
    make install
    poetry show --tree
}

main
