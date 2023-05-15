# SPDX-FileCopyrightText: 2023 Stephan Lipp, Technical University of Munich (TUM), et al.
# SPDX-License-Identifier: Apache-2.0
klee_get_llvm_libs(LLVM_LIBS irreader)

add_subdirectory(Support)
add_subdirectory(Expr)
add_subdirectory(BackwardAnalysis)

add_executable(precondInfer backward-ai.cpp)
target_link_libraries(precondInfer PRIVATE backwardAI ${LLVM_LIBS})