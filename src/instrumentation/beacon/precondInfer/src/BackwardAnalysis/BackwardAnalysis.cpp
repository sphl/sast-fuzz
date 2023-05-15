// SPDX-FileCopyrightText: 2023 Stephan Lipp, Technical University of Munich (TUM), et al.
// SPDX-License-Identifier: Apache-2.0
#include <klee/Expr.h>

using namespace klee;

void testB(ref<Expr> e) { e->dump(); }