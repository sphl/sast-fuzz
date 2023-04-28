#ifndef SFI_LLVM_UTILS_H
#define SFI_LLVM_UTILS_H

#include <string>

#include <llvm/IR/BasicBlock.h>
#include <llvm/IR/Function.h>
#include <llvm/IR/Module.h>

#include <sfi/types.h>

namespace sfi::llvm_utils {

LineRange computeRange(const Lines &lineNumbers);

std::string getFilename(const llvm::Function &func);

void setBBId(llvm::BasicBlock &bb, BBId id);

void setBBIds(llvm::Module &mod);

std::optional<BBId> getBBId(const llvm::BasicBlock &bb);

std::optional<Lines> getBBLines(const llvm::BasicBlock &bb);

std::optional<LineRange> getBBLineRange(const llvm::BasicBlock &bb);

std::optional<Lines> getFunctionLines(const llvm::Function &func);

std::optional<LineRange> getFunctionLineRange(const llvm::Function &func);

}  // namespace sfi::llvm_utils

#endif  // SFI_LLVM_UTILS_H
