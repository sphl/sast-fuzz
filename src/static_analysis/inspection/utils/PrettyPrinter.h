#ifndef PI_PRETTYPRINTER_H
#define PI_PRETTYPRINTER_H

#include "../container/FuncInfo.h"

#include <string>
#include <vector>

class PrettyPrinter {
  public:
    static std::string convertToJSON(std::vector<FuncInfo> &funcInfos);
};

#endif  // PI_PRETTYPRINTER_H
