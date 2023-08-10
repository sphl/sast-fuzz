# Copy test artifacts to build directory
file(COPY "${CMAKE_CURRENT_SOURCE_DIR}/data" DESTINATION "${CMAKE_CURRENT_BINARY_DIR}")

include("${CMAKE_SOURCE_DIR}/cmake/google_test.cmake")

# Create binary for test execution
add_executable(sfz_tests main.cpp test_cycle_length.cpp test_distance_matrix.cpp)

# Link gtest as static library
target_link_libraries(
    sfz_tests
    gtest_main
    gmock_main
    libsfz
)

# Automatic discovery of unit tests
include(GoogleTest)
gtest_discover_tests(
    sfz_tests
    PROPERTIES LABELS
               "unit"
               DISCOVERY_TIMEOUT # How long to wait (in seconds) before crashing
               240
)
