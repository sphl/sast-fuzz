# SPDX-FileCopyrightText: 2023 Stephan Lipp, Technical University of Munich (TUM), et al.
# SPDX-License-Identifier: Apache-2.0
klee_get_llvm_libs(
    LLVM_LIBS
    bitwriter
    core
    ipo
    irreader
    instcombine
    instrumentation
    target
    linker
    analysis
    scalaropts
    support
)

add_library(
    libsfi STATIC
    container/bb_info.cpp
    container/func_info.cpp
    logic/inspector.cpp
    utils/io.cpp
    utils/llvm_utils.cpp
    utils/pretty_printer.cpp
)

target_include_directories(libsfi PUBLIC ${SVF_INCLUDE_DIR} ${SFI_INCLUDE_DIR})
target_link_libraries(libsfi PRIVATE ${LLVM_LIBS} ${SVF_LIB})
set_target_properties(libsfi PROPERTIES PREFIX "")

add_executable(sfi main.cpp)

target_compile_options(sfi PRIVATE -O3 -fno-rtti -fPIC)
# Note that creating static libraries does not involve a linking steps, so we need to link "sfi" against SVF and cannot
# simply use it through "libsfi".
target_link_libraries(sfi PRIVATE libsfi ${SVF_LIB})
