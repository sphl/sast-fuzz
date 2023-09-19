add_library(libsfz STATIC container/distance_matrix.c container/target_bb.c cycle_length.c)

target_include_directories(libsfz PUBLIC ${SFZ_INCLUDE_DIR})
target_link_libraries(libsfz PUBLIC afl_config)
set_target_properties(libsfz PROPERTIES PREFIX "")

# target_compile_definitions(libsfz PUBLIC SFZ_OUTPUT_STATS)

if (CMAKE_BUILD_TYPE STREQUAL "Debug")
    target_compile_definitions(libsfz PUBLIC SFZ_DEBUG)
else ()
    # Disable asserts
    target_compile_definitions(libsfz PUBLIC NDEBUG)
endif ()

add_executable(sast-fuzz main.c)
target_link_libraries(sast-fuzz libsfz)
add_dependencies(sast-fuzz libsfz)
