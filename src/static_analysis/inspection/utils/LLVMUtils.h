#ifndef PI_LLVMUTILS_H
#define PI_LLVMUTILS_H

#include "llvm/IR/Function.h"

#include <string>

typedef unsigned int LineNumber;
typedef std::pair<LineNumber, LineNumber> LineRange;

class LLVMUtils {
  public:
    static std::string getFilename(const llvm::Function &func);

    static std::optional<LineRange> getBBLineRange(const llvm::BasicBlock &bb);

    static std::optional<LineRange> getFunctionLineRange(const llvm::Function &func);
};

#endif  // PI_LLVMUTILS_H
