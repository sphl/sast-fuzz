#ifndef PI_PRETTYPRINTER_H
#define PI_PRETTYPRINTER_H

#include "../container/FuncInfo.h"
#include "IO.h"

#include <string>
#include <vector>

class Printer {
  public:
    virtual std::string format(std::vector<FuncInfo> &funcInfos) = 0;

    void printToFile(std::string &filepath, std::vector<FuncInfo> &funcInfos) {
        IO::writeFile(filepath, format(funcInfos));
    }
};

class JSONPrinter : public Printer {
  public:
    std::string format(std::vector<FuncInfo> &funcInfos) override;
};

#endif  // PI_PRETTYPRINTER_H
