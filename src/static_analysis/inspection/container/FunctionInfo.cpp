#include "FunctionInfo.h"

FunctionInfo::FunctionInfo(const std::string &name,
                           const std::string &filename,
                           const Lines &lines,
                           const LineRange &lineRange,
                           bool reachableFromMain)
    : name(name), filename(filename), lines(lines), lineRange(lineRange), reachableFromMain(reachableFromMain) {}

const std::string &FunctionInfo::getName() const { return name; }

const std::string &FunctionInfo::getFilename() const { return filename; }

const Lines &FunctionInfo::getLines() const { return lines; }

const LineRange &FunctionInfo::getLineRange() const { return lineRange; }

bool FunctionInfo::isReachableFromMain() const { return reachableFromMain; }

bool FunctionInfo::operator==(const FunctionInfo &rhs) const {
    return name == rhs.name && filename == rhs.filename && lines == rhs.lines && lineRange == rhs.lineRange &&
           reachableFromMain == rhs.reachableFromMain;
}

bool FunctionInfo::operator!=(const FunctionInfo &rhs) const { return !(rhs == *this); }

std::ostream &operator<<(std::ostream &os, const FunctionInfo &info) {
    os << info.filename << ":" << info.name << (info.reachableFromMain ? "*" : "") << "[" << info.lineRange.first << ","
       << info.lineRange.second << "]";
    return os;
}
