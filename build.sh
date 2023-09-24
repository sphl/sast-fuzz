#!/bin/bash

build_type=${1:-Release}

[ -d build ] && rm -rf build

mkdir build

pushd build
cmake -DCMAKE_BUILD_TYPE=$build_type .. && make -j
popd

echo "INFO: ${build_type}-build finished!"
