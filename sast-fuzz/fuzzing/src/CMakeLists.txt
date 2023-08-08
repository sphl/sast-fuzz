add_executable(sast-fuzz cycle_length.c main.c target_bb.c)

target_include_directories(sast-fuzz PRIVATE ${SFZ_INCLUDE_DIR})
target_link_libraries(sast-fuzz PRIVATE afl_config)
