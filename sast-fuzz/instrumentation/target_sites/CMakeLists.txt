if (NOT SVF_DIR)
    if (DEFINED ENV{SVF_DIR})
        set(SVF_DIR "$ENV{SVF_DIR}" CACHE PATH "Root directory of the SVF installation")
    else ()
        message(FATAL_ERROR
            "SVF_DIR is not set. Please pass -DSVF_DIR=<path> or set the SVF_DIR environment variable "
            "to the SVF root directory (e.g., /opt/svf-2.2).")
    endif ()
endif ()

if (CMAKE_BUILD_TYPE STREQUAL "Debug")
    set(_svf_build_dir "${SVF_DIR}/Debug-build")
else ()
    set(_svf_build_dir "${SVF_DIR}/Release-build")
endif ()

set(SVF_INCLUDE_DIRS
    "${SVF_DIR}/include"
    "${_svf_build_dir}/include"
)

find_library(SVF_LIB
    NAMES Svf
    PATHS "${_svf_build_dir}/lib"
    NO_DEFAULT_PATH
    DOC "SVF library (libSvf)"
)

find_library(SVF_CUDD_LIB
    NAMES Cudd
    PATHS "${_svf_build_dir}/lib/CUDD"
    NO_DEFAULT_PATH
    DOC "SVF CUDD library (libCudd)"
)

if (NOT SVF_LIB)
    message(FATAL_ERROR
        "Could not find libSvf under ${_svf_build_dir}/lib.\n"
        "Make sure SVF has been built (./build.sh) before configuring this project.")
endif ()

message(STATUS "Found SVF: ${SVF_LIB}")

set(CBI_INCLUDE_DIR "${CMAKE_CURRENT_SOURCE_DIR}/include")

add_subdirectory(src)
