#ifndef PI_FUNCTIONINFO_H
#define PI_FUNCTIONINFO_H

#include "../PITypes.h"

#include <ostream>
#include <string>

class FuncInfo {
  private:
    std::string name;
    std::string filename;
    Lines lines;
    LineRange lineRange;
    bool reachableFromMain;

  public:
    FuncInfo(const std::string &name,
             const std::string &filename,
             const Lines &lines,
             const LineRange &lineRange,
             bool reachableFromMain);

    [[nodiscard]] const std::string &getName() const;

    [[nodiscard]] const std::string &getFilename() const;

    [[nodiscard]] const Lines &getLines() const;

    [[nodiscard]] const LineRange &getLineRange() const;

    [[nodiscard]] bool isReachableFromMain() const;

    bool operator==(const FuncInfo &rhs) const;

    bool operator!=(const FuncInfo &rhs) const;

    friend std::ostream &operator<<(std::ostream &os, const FuncInfo &info);
};

#endif  // PI_FUNCTIONINFO_H
