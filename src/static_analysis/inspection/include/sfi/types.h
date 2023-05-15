// SPDX-FileCopyrightText: 2023 Stephan Lipp, Technical University of Munich (TUM), et al.
// SPDX-License-Identifier: Apache-2.0
#ifndef SFI_TYPES_H
#define SFI_TYPES_H

#include <set>
#include <utility>

namespace sfi {

using LineNumber = unsigned long;
using Lines = std::set<LineNumber>;
using LineRange = std::pair<LineNumber, LineNumber>;

using BBId = unsigned long;

}  // namespace sfi

#endif  // SFI_TYPES_H
