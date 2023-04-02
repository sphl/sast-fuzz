#ifndef PI_LINETYPES_H
#define PI_LINETYPES_H

#include <set>

typedef unsigned long LineNumber;
typedef std::set<LineNumber> Lines;
typedef std::pair<LineNumber, LineNumber> LineRange;

typedef unsigned long BBId;

#endif  // PI_LINETYPES_H
