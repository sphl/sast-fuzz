#include "FuncInfo.h"

FuncInfo::FuncInfo(const std::string &name,
                   const std::string &filename,
                   const Lines &lines,
                   const LineRange &lineRange,
                   bool reachableFromMain)
    : name(name), filename(filename), lines(lines), lineRange(lineRange), reachableFromMain(reachableFromMain) {}

const std::string &FuncInfo::getName() const { return name; }

const std::string &FuncInfo::getFilename() const { return filename; }

const Lines &FuncInfo::getLines() const { return lines; }

const LineRange &FuncInfo::getLineRange() const { return lineRange; }

bool FuncInfo::isReachableFromMain() const { return reachableFromMain; }

bool FuncInfo::operator==(const FuncInfo &rhs) const {
    return name == rhs.name && filename == rhs.filename && lines == rhs.lines && lineRange == rhs.lineRange &&
           reachableFromMain == rhs.reachableFromMain;
}

bool FuncInfo::operator!=(const FuncInfo &rhs) const { return !(rhs == *this); }

std::ostream &operator<<(std::ostream &os, const FuncInfo &info) {
    os << info.filename << ":" << info.name << (info.reachableFromMain ? "*" : "") << "[" << info.lineRange.first << ","
       << info.lineRange.second << "]";
    return os;
}
