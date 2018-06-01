#!/bin/sh

set -ex

main() {
    # pip install -r requirements.txt
    pip install .
    pip freeze
}

main
