cmake_minimum_required(VERSION 3.16)

project(
    sast-fuzz
    VERSION 0.1
    DESCRIPTION "SAST-directed greybox fuzzing"
)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

include_directories(include)

add_subdirectory(src)
