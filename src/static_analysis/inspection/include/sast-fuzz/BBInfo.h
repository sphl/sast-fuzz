#ifndef PI_BBINFO_H
#define PI_BBINFO_H

#include <ostream>
#include <sast-fuzz/PITypes.h>

namespace sfi {

class BBInfo {
  private:
    BBId id;
    Lines lineNumbers;
    LineRange lineRange;

  public:
    BBInfo(BBId id, const Lines &lineNumbers, const LineRange &lineRange);

    [[nodiscard]] BBId getId() const;

    [[nodiscard]] const Lines &getLineNumbers() const;

    [[nodiscard]] const LineRange &getLineRange() const;

    bool operator==(const BBInfo &rhs) const;

    bool operator!=(const BBInfo &rhs) const;

    bool operator<(const BBInfo &rhs) const;
};

}  // namespace sfi

#endif  // PI_BBINFO_H
