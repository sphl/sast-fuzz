#ifndef PI_LLVMUTILS_H
#define PI_LLVMUTILS_H

#include "llvm/IR/Function.h"

#include <string>

using namespace std;
using namespace llvm;

typedef unsigned int LineNumber;

class LLVMUtils {
  public:
    static string getFilename(const Function *func);

    static optional<pair<LineNumber, LineNumber>> getFunctionLineRange(const Function *func);
};

#endif  // PI_LLVMUTILS_H
