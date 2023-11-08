klee_get_llvm_libs(
    LLVM_LIBS
    analysis
    bitwriter
    instrumentation
    irreader
)

if (CMAKE_BUILD_TYPE STREQUAL "Debug")
    set(CBI_COMPILE_OPTIONS -g -O0)
else ()
    set(CBI_COMPILE_OPTIONS -O3)
endif ()

add_library(libcbi STATIC container/target.cpp)

if (CMAKE_BUILD_TYPE STREQUAL "Debug")
    target_compile_definitions(libcbi PUBLIC CBI_DEBUG)
else ()
    # Disable asserts
    # target_compile_definitions(libcbi PUBLIC NDEBUG)
endif ()

target_include_directories(libcbi PUBLIC ${CBI_INCLUDE_DIR})
target_compile_options(libcbi PUBLIC ${CBI_COMPILE_OPTIONS})
set_target_properties(libcbi PROPERTIES PREFIX "")

add_executable(cbi container/target.cpp main.cpp)

target_include_directories(cbi PRIVATE "${SVF_INCLUDE_DIR}")
target_include_directories(cbi PUBLIC ${LLVM_INCLUDE_DIRS})
target_compile_options(cbi PRIVATE -fno-rtti -fPIC ${CBI_COMPILE_OPTIONS})
target_link_libraries(
    cbi
    PRIVATE libcbi
            ${SVF_LIB}
            ${SVF_CUDD_LIB}
            ${LLVM_LIBS}
)
add_dependencies(cbi libcbi)
