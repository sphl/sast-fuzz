add_library(afl_config INTERFACE)
target_compile_options(
    afl_config
    INTERFACE -funroll-loops
              # -g
              -O3
              -Wall
              -Wno-pointer-sign
)
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

add_subdirectory(instrumentation)
add_subdirectory(libs)
