// SPDX-FileCopyrightText: 2023 Stephan Lipp, Technical University of Munich (TUM), et al.
// SPDX-License-Identifier: Apache-2.0
#include <sfi/bb_info.h>

using namespace sfi;

BBInfo::BBInfo(BBId id, const Lines &lineNumbers, const LineRange &lineRange)
    : id(id), lineNumbers(lineNumbers), lineRange(lineRange) {}

BBId BBInfo::getId() const { return id; }

const Lines &BBInfo::getLineNumbers() const { return lineNumbers; }

const LineRange &BBInfo::getLineRange() const { return lineRange; }

bool BBInfo::operator==(const BBInfo &rhs) const {
    return id == rhs.id && lineNumbers == rhs.lineNumbers && lineRange == rhs.lineRange;
}

bool BBInfo::operator!=(const BBInfo &rhs) const { return !(rhs == *this); }

bool BBInfo::operator<(const BBInfo &rhs) const { return id < rhs.id; }
