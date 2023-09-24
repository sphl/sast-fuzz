#!/bin/bash

build_type=${1:-Release}
svf_dir="/opt/svf-2.2"

[ -d build ] && rm -rf build

mkdir build

pushd build
cmake -DCMAKE_BUILD_TYPE=$build_type -DSVF_DIR=$svf_dir .. && make -j
popd

echo "INFO: ${build_type}-build finished!"
