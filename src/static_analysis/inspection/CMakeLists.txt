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
    container/BBInfo.cpp
    container/FuncInfo.cpp
    utils/IO.cpp
    utils/LLVMUtils.cpp
    utils/PrettyPrinter.cpp
)

target_include_directories(libpi PUBLIC include)
target_link_libraries(libpi PRIVATE ${LLVM_LIBS})
set_target_properties(libpi PROPERTIES PREFIX "")

add_executable(pi pi.cpp)

target_compile_options(pi PRIVATE -O3 -fno-rtti -fPIC)
target_include_directories(pi PRIVATE ${SVF_INCLUDE_DIR})
target_link_libraries(pi PRIVATE libpi ${SVF_LIB})
