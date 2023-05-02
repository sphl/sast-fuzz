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

add_library(
    libsfi STATIC
    container/bb_info.cpp
    container/func_info.cpp
    logic/inspector.cpp
    utils/io.cpp
    utils/llvm_utils.cpp
    utils/pretty_printer.cpp
)

target_include_directories(libsfi PUBLIC ${SVF_INCLUDE_DIR} ${SFI_INCLUDE_DIR})
target_link_libraries(libsfi PRIVATE ${LLVM_LIBS} ${SVF_LIB})
set_target_properties(libsfi PROPERTIES PREFIX "")

add_executable(sfi main.cpp)

target_compile_options(sfi PRIVATE -O3 -fno-rtti -fPIC)
target_link_libraries(sfi PRIVATE libsfi ${SVF_LIB})
