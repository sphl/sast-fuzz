#!/bin/bash

[ -d build ] && rm -rf build

mkdir build

pushd build
cmake -DCMAKE_BUILD_TYPE=${1:-Release} .. && make -j
popd
