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
    /**
     * This pure virtual method is used to format the given vector of FuncInfo objects and map of BBId to BBId sets
     * (inter-procedural CFG) to a string representation.
     * @param funcInfos Vector of FuncInfo objects.
     * @param icfgInfos Map of BBId to BBId sets (iCFG).
     * @return A string representation of the formatted information.
     */
    virtual std::string format(std::vector<FuncInfo> &funcInfos,
                               std::optional<std::map<BBId, std::set<BBId>>> icfgInfos = std::nullopt) = 0;

    /**
     * This method writes the formatted information to a file.
     * @param filepath String containing the path of the file.
     * @param funcInfos Vector of FuncInfo objects.
     * @param icfgInfos Map of BBId to BBId sets (iCFG).
     */
    void printToFile(std::string &filepath,
                     std::vector<FuncInfo> &funcInfos,
                     std::optional<std::map<BBId, std::set<BBId>>> icfgInfos = std::nullopt) {
        io::writeFile(filepath, format(funcInfos, icfgInfos));
    }
};

class JSONPrinter : public Printer {
  public:
    /**
     * This method formats the given vector of FuncInfo objects and map of BBId to BBId sets (inter-procedural CFG) to
     * a JSON string.
     * @param funcInfos Vector of FuncInfo objects.
     * @param icfgInfos Map of BBId to BBId sets (iCFG).
     * @return A JSON string representation of the formatted information.
     */
    std::string format(std::vector<FuncInfo> &funcInfos,
                       std::optional<std::map<BBId, std::set<BBId>>> icfgInfos = std::nullopt) override;
};

}  // namespace sfi

#endif  // SFI_PRETTY_PRINTER_H
