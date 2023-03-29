klee_get_llvm_libs(
    LLVM_LIBS
    analysis
    bitwriter
    instrumentation
    irreader
)

add_executable(cbi cbi.cpp)
target_compile_options(cbi PRIVATE -fno-rtti -fPIC)
target_include_directories(cbi PRIVATE "${SVF_INCLUDE_DIR}")
target_link_libraries(cbi PRIVATE ${SVF_LIB} ${SVF_CUDD_LIB} ${LLVM_LIBS})
