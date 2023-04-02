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
    container/BBInfo.cpp
    container/BBInfo.h
    container/FuncInfo.cpp
    container/FuncInfo.h
    pi.cpp
    PITypes.h
    utils/IO.cpp
    utils/IO.h
    utils/LLVMUtils.cpp
    utils/LLVMUtils.h
    utils/PrettyPrinter.cpp
    utils/PrettyPrinter.h
)
target_compile_options(pi PRIVATE -fno-rtti -fPIC)
target_include_directories(pi PRIVATE ${SVF_INCLUDE_DIR})
target_link_libraries(pi PRIVATE ${SVF_LIB} ${LLVM_LIBS})
