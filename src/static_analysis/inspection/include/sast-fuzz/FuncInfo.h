#ifndef PI_FUNCTIONINFO_H
#define PI_FUNCTIONINFO_H

#include <ostream>
#include <set>
#include <sast-fuzz/BBInfo.h>
#include <sast-fuzz/PITypes.h>
#include <string>

namespace sfi {

class FuncInfo {
  private:
    std::string name;
    std::string filename;
    Lines lineNumbers;
    LineRange lineRange;
    bool reachableFromMain;
    std::set<BBInfo> blockInfos;

  public:
    FuncInfo(const std::string &name,
             const std::string &filename,
             const Lines &lineNumbers,
             const LineRange &lineRange,
             bool reachableFromMain,
             std::set<BBInfo> blockInfos);

    [[nodiscard]] const std::string &getName() const;

    [[nodiscard]] const std::string &getFilename() const;

    [[nodiscard]] const Lines &getLineNumbers() const;

    [[nodiscard]] const LineRange &getLineRange() const;

    [[nodiscard]] bool isReachableFromMain() const;

    [[nodiscard]] const std::set<BBInfo> &getBlockInfos() const;

    bool operator==(const FuncInfo &rhs) const;

    bool operator!=(const FuncInfo &rhs) const;
};

}  // namespace sfi

#endif  // PI_FUNCTIONINFO_H
