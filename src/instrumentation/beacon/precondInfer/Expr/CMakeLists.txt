# ===----------------------------------------------------------------------------------------------------------------===
#
# The KLEE Symbolic Virtual Machine
#
# This file is distributed under the University of Illinois Open Source License. See LICENSE.TXT for details.
#
# ===----------------------------------------------------------------------------------------------------------------===
klee_get_llvm_libs(LLVM_LIBS support)

klee_add_component(
    kleaverExpr
    ArrayCache.cpp
    ArrayExprOptimizer.cpp
    ArrayExprRewriter.cpp
    ArrayExprVisitor.cpp
    Assigment.cpp
    AssignmentGenerator.cpp
    Constraints.cpp
    Expr.cpp
    ExprBuilder.cpp
    ExprEvaluator.cpp
    ExprPPrinter.cpp
    ExprUtil.cpp
    ExprVisitor.cpp
    Updates.cpp
)
target_link_libraries(kleaverExpr PUBLIC ${LLVM_LIBS})
