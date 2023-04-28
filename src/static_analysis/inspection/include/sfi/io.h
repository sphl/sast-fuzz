#ifndef SFI_IO_H
#define SFI_IO_H

#include <string>

namespace sfi::io {

std::string readFile(const std::string &filepath);

void writeFile(const std::string &filepath, const std::string &text);

}  // namespace sfi::io

#endif  // SFI_IO_H
