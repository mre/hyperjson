#!/bin/sh

set -ex

main() {
    # pip3 install -r requirements.txt
    pip3 install .
    pip3 freeze
}

main
