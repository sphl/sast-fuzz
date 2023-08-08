set(afl_targets
    afl-analyze
    afl-gotcpu
    afl-showmap
    afl-tmin
)

foreach (target ${afl_targets})
    add_executable(${target} ${target}.c)
    target_link_libraries(${target} PRIVATE afl_config)
endforeach ()

add_subdirectory(libs)
