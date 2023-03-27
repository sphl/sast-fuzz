#!/bin/bash

config_file="./.cmake-format.yaml"

if [ ! -f "$config_file" ]; then
    echo "Config file ('.cmake-format.yaml') couldn't be found!"
    exit 1
fi

echo "cmake-format ..."

cmake-format --in-place $(find . -name "CMakeLists.txt" -o -name "*.cmake" -not -path "./build*" | xargs)

echo "done!"
exit 0