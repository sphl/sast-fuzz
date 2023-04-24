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

add_executable(
    pi
    pi.cpp
    container/FuncInfo.cpp
    container/BBInfo.cpp
    utils/IO.cpp
    utils/LLVMUtils.cpp
    utils/PrettyPrinter.cpp
)
target_include_directories(pi PUBLIC include)

target_compile_options(pi PRIVATE -O3 -fno-rtti -fPIC)
target_include_directories(pi PRIVATE ${SVF_INCLUDE_DIR})
target_link_libraries(pi PRIVATE ${SVF_LIB} ${LLVM_LIBS})
