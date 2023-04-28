include("${CMAKE_SOURCE_DIR}/cmake/google_test.cmake")

# create binary for test execution
add_executable(pi_tests main.cpp test_io.cpp)

# link gtest as static library
target_link_libraries(
        pi_tests
        gtest_main
        gmock_main
        libpi
)

# automatic discovery of unit tests
include(GoogleTest)
gtest_discover_tests(
        pi_tests
        PROPERTIES LABELS
        "unit"
        DISCOVERY_TIMEOUT # how long to wait (in seconds) before crashing
        240
)
