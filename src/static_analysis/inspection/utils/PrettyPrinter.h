#ifndef PI_PRETTYPRINTER_H
#define PI_PRETTYPRINTER_H

#include "../container/FuncInfo.h"

#include <vector>
#include <string>

class PrettyPrinter {
  public:
    static std::string convertToJSON(std::vector<FuncInfo> funcInfos);
};

#endif  // PI_PRETTYPRINTER_H
