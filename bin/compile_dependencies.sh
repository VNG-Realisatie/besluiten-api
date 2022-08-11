#!/bin/bash

set -ex

toplevel=$(git rev-parse --show-toplevel)

cd $toplevel

export CUSTOM_COMPILE_COMMAND="./bin/compile_dependencies.sh"

# Base deps
pip-compile \
    --no-emit-index-url \
    --allow-unsafe \
    "$@" \
    requirements/base.in

# Jenkins/tests deps
pip-compile \
    --no-emit-index-url \
    --allow-unsafe \
    --output-file requirements/jenkins.txt \
    "$@" \
    requirements/base.txt \
    requirements/testing.in \
    requirements/jenkins.in
