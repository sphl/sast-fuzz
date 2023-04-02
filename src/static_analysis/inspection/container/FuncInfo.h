#ifndef PI_FUNCTIONINFO_H
#define PI_FUNCTIONINFO_H

#include "../LineTypes.h"

#include <ostream>
#include <string>

class FuncInfo {
  private:
    std::string name;
    std::string filename;
    Lines lineNumbers;
    LineRange lineRange;
    bool reachableFromMain;

  public:
    FuncInfo(const std::string &name,
             const std::string &filename,
             const Lines &lineNumbers,
             const LineRange &lineRange,
             bool reachableFromMain);

    [[nodiscard]] const std::string &getName() const;

    [[nodiscard]] const std::string &getFilename() const;

    [[nodiscard]] const Lines &getLineNumbers() const;

    [[nodiscard]] const LineRange &getLineRange() const;

    [[nodiscard]] bool isReachableFromMain() const;

    bool operator==(const FuncInfo &rhs) const;

    bool operator!=(const FuncInfo &rhs) const;

    friend std::ostream &operator<<(std::ostream &os, const FuncInfo &info);
};

#endif  // PI_FUNCTIONINFO_H
