# Copy test artifacts to build directory
file(COPY "${CMAKE_CURRENT_SOURCE_DIR}/data" DESTINATION "${CMAKE_CURRENT_BINARY_DIR}")

include("${CMAKE_SOURCE_DIR}/cmake/google_test.cmake")

# create binary for test execution
add_executable(
    sfi_tests
    main.cpp
    test_bb_info.cpp
    test_func_info.cpp
    test_io.cpp
    test_llvm_utils.cpp
)

# link gtest as static library
target_link_libraries(
    sfi_tests
    gtest_main
    gmock_main
    libsfi
)

# automatic discovery of unit tests
include(GoogleTest)
gtest_discover_tests(
    sfi_tests
    PROPERTIES LABELS
               "unit"
               DISCOVERY_TIMEOUT # how long to wait (in seconds) before crashing
               240
)
