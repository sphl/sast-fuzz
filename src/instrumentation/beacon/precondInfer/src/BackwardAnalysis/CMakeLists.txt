# SPDX-FileCopyrightText: 2023 Stephan Lipp, Technical University of Munich (TUM), et al.
# SPDX-License-Identifier: Apache-2.0
klee_get_llvm_libs(
        LLVM_LIBS
        bitwriter
        core
        passes
        support
)

klee_add_component(
        backwardAI
        AbstractState.cpp
        AliasICFG.cpp
        BackwardAnalysis.cpp
        InstructionDbgInfo.cpp
        RangeAnalysis.cpp
        RangeComputeInterface.cpp
        WPCondition.cpp
        WPInferenceInterface.cpp
)
target_include_directories(backwardAI PUBLIC "${SVF_INCLUDE_DIR}")
target_link_libraries(backwardAI PUBLIC ${SVF_LIB} ${SVF_CUDD_LIB} ${LLVM_LIBS})
target_link_libraries(backwardAI PRIVATE kleaverExpr kleeSupport)
