add_executable(sast-fuzz main.c)
target_link_libraries(sast-fuzz PRIVATE afl_config)
