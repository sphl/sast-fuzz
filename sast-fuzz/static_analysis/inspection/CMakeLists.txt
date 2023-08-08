# Add CXX coverage compiler flags
if (CODE_COVERAGE AND UNIX)
    include("${CMAKE_SOURCE_DIR}/cmake/code_coverage.cmake")
    append_coverage_compiler_flags()
endif (CODE_COVERAGE AND UNIX)

set(SFI_INCLUDE_DIR "${CMAKE_CURRENT_SOURCE_DIR}/include")

add_subdirectory(src)

enable_testing()
add_subdirectory(tests)
