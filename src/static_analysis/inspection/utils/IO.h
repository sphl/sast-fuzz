#ifndef PI_IO_H
#define PI_IO_H

#include <string>

class IO {
  public:
    static std::string readFile(const std::string &filepath);

    static void writeFile(const std::string &filepath, const std::string &text);
};

#endif  // PI_IO_H
