include("${CMAKE_SOURCE_DIR}/cmake/string_to_list.cmake")
include("${CMAKE_SOURCE_DIR}/cmake/find_llvm.cmake")

# TODO: Remove the line below in the release version!
set(SVF_DIR "/opt/svf-2.2")
include("${CMAKE_SOURCE_DIR}/cmake/find_svf.cmake")

add_library(afl_config INTERFACE)

if (CMAKE_BUILD_TYPE STREQUAL "Debug")
    target_compile_options(
        afl_config
        INTERFACE -g
                  -O0
                  -Wall
                  -Wno-pointer-sign
    )
else ()
    target_compile_options(
        afl_config
        INTERFACE -funroll-loops
                  -O3
                  -Wall
                  -Wno-pointer-sign
    )
endif ()

target_compile_definitions(
    afl_config
    INTERFACE _FORTIFY_SOURCE=2
              AFL_PATH=\"${CMAKE_INSTALL_PREFIX}/lib/afl\"
              BIN_PATH=\"${CMAKE_INSTALL_PREFIX}/bin\"
              DOC_PATH=\"${CMAKE_INSTALL_PREFIX}/share/doc/afl\"
)
target_link_libraries(afl_config INTERFACE ${CMAKE_DL_LIBS} m)

set(afl_targets
    afl-analyze
    afl-fuzz
    afl-gotcpu
    afl-showmap
    afl-tmin
)

foreach (target ${afl_targets})
    add_executable(${target} ${target}.c)
    target_link_libraries(${target} PRIVATE afl_config)
endforeach ()

add_subdirectory(static_analysis)
add_subdirectory(instrumentation)
add_subdirectory(libs)
