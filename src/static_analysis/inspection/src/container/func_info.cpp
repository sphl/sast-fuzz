// SPDX-FileCopyrightText: 2023 Stephan Lipp, Technical University of Munich (TUM), et al.
// SPDX-License-Identifier: Apache-2.0
#include <sfi/func_info.h>

using namespace sfi;

FuncInfo::FuncInfo(const std::string &name,
                   const std::string &filename,
                   const Lines &lineNumbers,
                   const LineRange &lineRange,
                   bool reachableFromMain,
                   std::set<BBInfo> blockInfos)
    : name(name), filename(filename), lineNumbers(lineNumbers), lineRange(lineRange),
      reachableFromMain(reachableFromMain), blockInfos(std::move(blockInfos)) {}

const std::string &FuncInfo::getName() const { return name; }

const std::string &FuncInfo::getFilename() const { return filename; }

const Lines &FuncInfo::getLineNumbers() const { return lineNumbers; }

const LineRange &FuncInfo::getLineRange() const { return lineRange; }

bool FuncInfo::isReachableFromMain() const { return reachableFromMain; }

const std::set<BBInfo> &FuncInfo::getBlockInfos() const { return blockInfos; }

bool FuncInfo::operator==(const FuncInfo &rhs) const {
    return name == rhs.name && filename == rhs.filename && lineNumbers == rhs.lineNumbers &&
           lineRange == rhs.lineRange && reachableFromMain == rhs.reachableFromMain && blockInfos == rhs.blockInfos;
}

bool FuncInfo::operator!=(const FuncInfo &rhs) const { return !(rhs == *this); }
