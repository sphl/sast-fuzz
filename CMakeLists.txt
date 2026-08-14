cmake_minimum_required(VERSION 3.16)

project(
    sast-fuzz
    VERSION 0.1
    DESCRIPTION "A SAST-guided greybox fuzzer."
)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

set(CMAKE_RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin")

include_directories(include)

enable_testing()
add_subdirectory(sast-fuzz)
