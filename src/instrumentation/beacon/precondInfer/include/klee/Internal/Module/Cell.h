// SPDX-FileCopyrightText: 2023 Stephan Lipp, Technical University of Munich (TUM), et al.
// SPDX-License-Identifier: Apache-2.0
//===-- Cell.h --------------------------------------------------*- C++ -*-===//
//
//                     The KLEE Symbolic Virtual Machine
//
// This file is distributed under the University of Illinois Open Source
// License. See LICENSE.TXT for details.
//
//===----------------------------------------------------------------------===//

#ifndef KLEE_CELL_H
#define KLEE_CELL_H

#include <klee/Expr.h>

namespace klee {
  class MemoryObject;

  struct Cell {
    ref<Expr> value;
  };
}

#endif
