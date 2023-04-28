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
        libpi STATIC
        container/bb_info.cpp
        container/func_info.cpp
        utils/io.cpp
        utils/llvm_utils.cpp
        utils/pretty_printer.cpp
)

target_link_libraries(libpi PRIVATE ${LLVM_LIBS})
set_target_properties(libpi PROPERTIES PREFIX "")

add_executable(pi main.cpp)

target_compile_options(pi PRIVATE -O3 -fno-rtti -fPIC)
target_include_directories(pi PRIVATE ${SVF_INCLUDE_DIR})
target_link_libraries(pi PRIVATE libpi ${SVF_LIB})
