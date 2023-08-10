add_library(libsfz STATIC cycle_length.c container/distance_matrix.c container/target_bb.c)

target_include_directories(libsfz PUBLIC ${SFZ_INCLUDE_DIR})
target_link_libraries(libsfz PUBLIC afl_config)
set_target_properties(libsfz PROPERTIES PREFIX "")

add_executable(sast-fuzz main.c)

target_link_libraries(sast-fuzz libsfz)
