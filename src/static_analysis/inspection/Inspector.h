#ifndef PI_INSPECTOR_H
#define PI_INSPECTOR_H

#include "SVF-FE/LLVMUtil.h"
#include "container/FuncInfo.h"

#include <vector>

class Inspector {
  public:
    static std::vector<FuncInfo> getFuncInfo(SVF::SVFModule *svfModule);
};

#endif  // PI_INSPECTOR_H
