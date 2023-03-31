#ifndef PI_LLVMUTILS_H
#define PI_LLVMUTILS_H

#include "../PITypes.h"
#include "llvm/IR/Function.h"

#include <string>

class LLVMUtils {
  public:
    static std::string getFilename(const llvm::Function &func);

    static LineRange getLineRange(const Lines  &lineNumbers);

    static std::optional<Lines> getBBLines(const llvm::BasicBlock &bb);

    static std::optional<LineRange> getBBLineRange(const llvm::BasicBlock &bb);

    static std::optional<Lines> getFunctionLines(const llvm::Function &func);

    static std::optional<LineRange> getFunctionLineRange(const llvm::Function &func);
};

#endif  // PI_LLVMUTILS_H
