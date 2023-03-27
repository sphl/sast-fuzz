if (NOT DEFINED SVF_DIR)
    if (DEFINED ENV{SVF_DIR})
        set(SVF_DIR $ENV{SVF_DIR})
    else ()
        message(FATAL_ERROR "\"SVF_DIR\" is not specified!")
    endif ()
endif ()

if (CMAKE_BUILD_TYPE MATCHES "Debug")
    set(SVF_BUILD_DIR "${SVF_DIR}/Debug-build")
else ()
    set(SVF_BUILD_DIR "${SVF_DIR}/Release-build")
endif ()

set(SVF_INCLUDE_DIR "${SVF_DIR}/include")

set(SVF_LIB "${SVF_BUILD_DIR}/lib/libSvf.a")
set(SVF_CUDD_LIB "${SVF_BUILD_DIR}/lib/CUDD/libCudd.a")
