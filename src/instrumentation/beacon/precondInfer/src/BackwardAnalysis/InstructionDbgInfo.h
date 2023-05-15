// SPDX-FileCopyrightText: 2023 Stephan Lipp, Technical University of Munich (TUM), et al.
// SPDX-License-Identifier: Apache-2.0
#ifndef INSTRUCTION_DBG_INFO_H
#define INSTRUCTION_DBG_INFO_H

#include <llvm/Analysis/AliasAnalysis.h>
#include <llvm/IR/BasicBlock.h>
#include <llvm/IR/Instruction.h>
#include <llvm/IR/PassManager.h>

namespace BackwardAI {

class InstructionDbgInfo {
  public:
    static unsigned instToLine(const llvm::Instruction *);
    static bool hasLineInfo(const llvm::Instruction *);
    static const llvm::Instruction *lineToInst(unsigned);
    static void registerModule(const llvm::Module *M);

  private:
    InstructionDbgInfo() {}
    std::map<unsigned, const llvm::Instruction *> asmLineToInst;
    std::map<const llvm::Instruction *, unsigned> instToAsmLine;
    void buildLineInfoTable(const llvm::Module *M);
    void sanityCheck(const llvm::Module *M);
    static InstructionDbgInfo *instance;
};

}  // namespace BackwardAI
#endif