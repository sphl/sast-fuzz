cmake_minimum_required(VERSION 3.16)

project(
    sast-fuzz
    VERSION 0.1
    DESCRIPTION "SAST-directed greybox fuzzing"
)

include_directories(include)
add_subdirectory(src)
