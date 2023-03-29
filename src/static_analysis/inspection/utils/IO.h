#ifndef PI_IO_H
#define PI_IO_H

#include <string>

using namespace std;

class IO {
  public:
    static string readFile(const string &filepath);

    static void writeFile(const string &filepath, const string &text);
};

#endif  // PI_IO_H
