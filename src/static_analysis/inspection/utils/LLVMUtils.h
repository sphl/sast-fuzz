#ifndef PI_LLVMUTILS_H
#define PI_LLVMUTILS_H

#include "../LineTypes.h"

#include "llvm/IR/Module.h"
#include "llvm/IR/Function.h"
#include "llvm/IR/BasicBlock.h"

#include <string>

typedef unsigned long BBId;

class LLVMUtils {
  public:
    static LineRange computeRange(const Lines &lineNumbers);

    static std::string getFilename(const llvm::Function &func);

    static void setBBId(llvm::BasicBlock &bb, BBId id);

    static void setBBIds(llvm::Module &mod);

    static std::optional<BBId> getBBId(const llvm::BasicBlock &bb);

    static std::optional<Lines> getBBLines(const llvm::BasicBlock &bb);

    static std::optional<LineRange> getBBLineRange(const llvm::BasicBlock &bb);

    static std::optional<Lines> getFunctionLines(const llvm::Function &func);

    static std::optional<LineRange> getFunctionLineRange(const llvm::Function &func);
};

#endif  // PI_LLVMUTILS_H
