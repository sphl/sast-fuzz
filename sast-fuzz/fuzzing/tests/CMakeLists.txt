include("${CMAKE_SOURCE_DIR}/cmake/google_test.cmake")

# create binary for test execution
add_executable(sfz_tests main.cpp test_distance_matrix.cpp)

# link gtest as static library
target_link_libraries(
    sfz_tests
    gtest_main
    gmock_main
    libsfz
)

# automatic discovery of unit tests
include(GoogleTest)
gtest_discover_tests(
    sfz_tests
    PROPERTIES LABELS
               "unit"
               DISCOVERY_TIMEOUT # how long to wait (in seconds) before crashing
               240
)
