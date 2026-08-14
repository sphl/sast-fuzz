add_library(libsfz STATIC
    container/distance_matrix.c
    container/target_bb.c
    cycle_length.c
)

target_include_directories(libsfz PUBLIC ${SFZ_INCLUDE_DIR})
target_link_libraries(libsfz PUBLIC afl_config)
set_target_properties(libsfz PROPERTIES PREFIX "")

target_compile_definitions(libsfz PUBLIC
    SFZ_OUTPUT_STATS
    $<$<CONFIG:Debug>:SFZ_DEBUG>
    $<$<NOT:$<CONFIG:Debug>>:NDEBUG>
)

add_executable(sast-fuzz main.c)
target_link_libraries(sast-fuzz PRIVATE libsfz)
