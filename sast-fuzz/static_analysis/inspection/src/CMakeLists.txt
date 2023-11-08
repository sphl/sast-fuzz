klee_get_llvm_libs(
    LLVM_LIBS
    bitwriter
    core
    ipo
    irreader
    instcombine
    instrumentation
    target
    linker
    analysis
    scalaropts
    support
)

if (CMAKE_BUILD_TYPE STREQUAL "Debug")
    set(SFI_COMPILE_OPTIONS -g -O0)
else ()
    set(SFI_COMPILE_OPTIONS -O3)
endif ()

add_library(
    libsfi STATIC
    container/bb_info.cpp
    container/func_info.cpp
    logic/inspector.cpp
    utils/io.cpp
    utils/llvm_utils.cpp
    utils/pretty_printer.cpp
)

if (CMAKE_BUILD_TYPE STREQUAL "Release")
    # Disable asserts
    target_compile_definitions(libsfi PUBLIC NDEBUG)
endif ()

target_compile_options(libsfi PRIVATE ${SFI_COMPILE_OPTIONS})
target_include_directories(libsfi PUBLIC ${SVF_INCLUDE_DIR} ${SFI_INCLUDE_DIR} ${LLVM_INCLUDE_DIRS})
target_link_libraries(libsfi PRIVATE ${LLVM_LIBS} ${SVF_LIB})
set_target_properties(libsfi PROPERTIES PREFIX "")

add_executable(sfi main.cpp)

target_compile_options(sfi PRIVATE -fno-rtti -fPIC ${SFI_COMPILE_OPTIONS})
# Note that creating static libraries does not involve a linking steps, so we need to link "sfi" against SVF and cannot
# simply use it through "libsfi".
target_link_libraries(sfi PRIVATE libsfi ${SVF_LIB})
add_dependencies(sfi libsfi)
