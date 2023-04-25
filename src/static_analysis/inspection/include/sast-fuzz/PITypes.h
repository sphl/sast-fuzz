#ifndef PI_PITYPES_H
#define PI_PITYPES_H

#include <set>
#include <utility>

namespace sfi {

using LineNumber = unsigned long;
using Lines = std::set<LineNumber>;
using LineRange = std::pair<LineNumber, LineNumber>;

using BBId = unsigned long;

}  // namespace sfi

#endif  // PI_PITYPES_H
