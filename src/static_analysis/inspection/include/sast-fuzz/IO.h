#ifndef PI_IO_H
#define PI_IO_H

#include <string>

namespace sfi {

namespace IO {
std::string readFile(const std::string &filepath);

void writeFile(const std::string &filepath, const std::string &text);
};  // namespace IO

}  // namespace sfi

#endif  // PI_IO_H
