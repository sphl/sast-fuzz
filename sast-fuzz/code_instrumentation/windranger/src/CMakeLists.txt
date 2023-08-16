klee_get_llvm_libs(
    LLVM_LIBS
    analysis
    bitwriter
    instrumentation
    irreader
)

add_library(libcbi STATIC container/target.cpp)
target_include_directories(libcbi PUBLIC ${CBI_INCLUDE_DIR})
set_target_properties(libcbi PROPERTIES PREFIX "")

add_executable(cbi container/target.cpp main.cpp)

if (CMAKE_BUILD_TYPE STREQUAL "Debug")
    target_compile_options(
        cbi
        PRIVATE -fno-rtti
                -fPIC
                -g
                -O0
    )
else ()
    target_compile_options(cbi PRIVATE -fno-rtti -fPIC -O3)
endif ()

target_include_directories(cbi PRIVATE "${SVF_INCLUDE_DIR}")
target_link_libraries(
    cbi
    PRIVATE libcbi
            ${SVF_LIB}
            ${SVF_CUDD_LIB}
            ${LLVM_LIBS}
)
add_dependencies(cbi libcbi)