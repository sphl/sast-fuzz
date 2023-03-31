#ifndef PI_PIHELPER_H
#define PI_PIHELPER_H

#include "SVF-FE/LLVMUtil.h"
#include "container/FuncInfo.h"

#include <vector>

class PIHelper {
  public:
    static std::vector<FuncInfo> getFuncInfo(SVF::SVFModule *svfModule);
};

#endif  // PI_PIHELPER_H
