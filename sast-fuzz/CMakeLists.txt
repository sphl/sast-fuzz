option(CODE_COVERAGE "Enable code coverage instrumentation" OFF)

if (CODE_COVERAGE AND UNIX)
    add_compile_options(--coverage)
    add_link_options(--coverage)
    message(STATUS "Code coverage enabled")
endif ()

add_library(afl_config INTERFACE)

target_compile_options(afl_config INTERFACE
    $<$<CONFIG:Debug>:-g>
    $<$<CONFIG:Debug>:-O0>
    $<$<NOT:$<CONFIG:Debug>>:-funroll-loops>
    $<$<NOT:$<CONFIG:Debug>>:-O3>
    -Wall
    -Wno-pointer-sign
)

target_compile_definitions(afl_config INTERFACE
    _FORTIFY_SOURCE=2
    AFL_PATH=\"${CMAKE_INSTALL_PREFIX}/lib/afl\"
    BIN_PATH=\"${CMAKE_INSTALL_PREFIX}/bin\"
    DOC_PATH=\"${CMAKE_INSTALL_PREFIX}/share/doc/afl\"
)

target_link_libraries(afl_config INTERFACE ${CMAKE_DL_LIBS} m)

add_subdirectory(fuzzing)
add_subdirectory(instrumentation)
add_subdirectory(utils)
