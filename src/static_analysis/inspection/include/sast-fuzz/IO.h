#ifndef PI_IO_H
#define PI_IO_H

#include <string>

namespace IO {
    std::string readFile(const std::string &filepath);

    void writeFile(const std::string &filepath, const std::string &text);
};

#endif  // PI_IO_H
