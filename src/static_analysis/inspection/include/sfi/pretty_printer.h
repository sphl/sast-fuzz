#ifndef SFI_PRETTY_PRINTER_H
#define SFI_PRETTY_PRINTER_H

#include <map>
#include <set>
#include <string>
#include <vector>

#include <sfi/func_info.h>
#include <sfi/io.h>

namespace sfi {

class Printer {
  public:
    virtual std::string format(std::vector<FuncInfo> &funcInfos, std::map<BBId, std::set<BBId>> &icfgInfos) = 0;

    void
    printToFile(std::string &filepath, std::vector<FuncInfo> &funcInfos, std::map<BBId, std::set<BBId>> &icfgInfos) {
        io::writeFile(filepath, format(funcInfos, icfgInfos));
    }
};

class JSONPrinter : public Printer {
  public:
    std::string format(std::vector<FuncInfo> &funcInfos, std::map<BBId, std::set<BBId>> &icfgInfos) override;
};

}  // namespace sfi

#endif  // SFI_PRETTY_PRINTER_H
