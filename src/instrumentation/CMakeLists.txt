# SPDX-FileCopyrightText: 2023 Stephan Lipp, Technical University of Munich (TUM), et al.
# SPDX-License-Identifier: Apache-2.0
add_executable(afl-clang-fast afl-clang-fast.c)
target_link_libraries(afl-clang-fast PRIVATE afl_config)

add_custom_target(
    afl-clang-fast++ ALL
    COMMAND "${CMAKE_COMMAND}" -E create_symlink afl-clang-fast afl-clang-fast++
    WORKING_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}"
)

add_library(afl-llvm-pass MODULE afl-llvm-pass.so.cc)
target_compile_options(afl-llvm-pass PRIVATE -fno-rtti)
set_target_properties(afl-llvm-pass PROPERTIES PREFIX "")

add_library(afl-llvm-rt STATIC afl-llvm-rt.o.c)
target_link_libraries(afl-llvm-rt PRIVATE afl_config)
set_target_properties(afl-llvm-rt PROPERTIES PREFIX "")

add_subdirectory(beacon)
add_subdirectory(windranger)
