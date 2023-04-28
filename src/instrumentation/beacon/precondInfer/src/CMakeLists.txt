klee_get_llvm_libs(LLVM_LIBS irreader)

add_subdirectory(Support)
add_subdirectory(Expr)
add_subdirectory(BackwardAnalysis)

add_executable(precondInfer backward-ai.cpp)
target_link_libraries(precondInfer PRIVATE backwardAI ${LLVM_LIBS})