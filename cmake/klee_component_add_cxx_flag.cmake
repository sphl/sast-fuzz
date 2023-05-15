# SPDX-FileCopyrightText: 2023 Stephan Lipp, Technical University of Munich (TUM), et al.
# SPDX-License-Identifier: Apache-2.0
# ===----------------------------------------------------------------------------------------------------------------===
#
# The KLEE Symbolic Virtual Machine
#
# This file is distributed under the University of Illinois Open Source License. See LICENSE.TXT for details.
#
# ===----------------------------------------------------------------------------------------------------------------===
include(CheckCXXCompilerFlag)
include(CMakeParseArguments)

function (klee_component_add_cxx_flag flag)
    cmake_parse_arguments(
        klee_component_add_cxx_flag
        "REQUIRED"
        ""
        ""
        ${ARGN}
    )
    string(
        REPLACE "-"
                "_"
                SANITIZED_FLAG_NAME
                "${flag}"
    )
    string(
        REPLACE "/"
                "_"
                SANITIZED_FLAG_NAME
                "${SANITIZED_FLAG_NAME}"
    )
    string(
        REPLACE "="
                "_"
                SANITIZED_FLAG_NAME
                "${SANITIZED_FLAG_NAME}"
    )
    string(
        REPLACE " "
                "_"
                SANITIZED_FLAG_NAME
                "${SANITIZED_FLAG_NAME}"
    )
    string(
        REPLACE "+"
                "_"
                SANITIZED_FLAG_NAME
                "${SANITIZED_FLAG_NAME}"
    )
    unset(HAS_${SANITIZED_FLAG_NAME})
    check_cxx_compiler_flag("${flag}" HAS_${SANITIZED_FLAG_NAME})
    if (klee_component_add_cxx_flag_REQUIRED AND NOT HAS_${SANITIZED_FLAG_NAME})
        message(FATAL_ERROR "The flag \"${flag}\" is required but your C++ compiler doesn't support it")
    endif ()
    if (HAS_${SANITIZED_FLAG_NAME})
        message(STATUS "C++ compiler supports ${flag}")
        list(APPEND KLEE_COMPONENT_CXX_FLAGS "${flag}")
        set(KLEE_COMPONENT_CXX_FLAGS
            ${KLEE_COMPONENT_CXX_FLAGS}
            PARENT_SCOPE
        )
    else ()
        message(STATUS "C++ compiler does not support ${flag}")
    endif ()
endfunction ()
