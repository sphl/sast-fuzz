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
target_link_libraries(
    backwardAI
    PUBLIC kleaverExpr
           kleeSupport
           ${SVF_LIB}
           ${SVF_CUDD_LIB}
           ${LLVM_LIBS}
)
