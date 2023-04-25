#ifndef PI_LLVMUTILS_H
#define PI_LLVMUTILS_H

#include <llvm/IR/BasicBlock.h>
#include <llvm/IR/Function.h>
#include <llvm/IR/Module.h>
#include <sast-fuzz/PITypes.h>
#include <string>

namespace sfi {

namespace LLVMUtils {
LineRange computeRange(const Lines &lineNumbers);

std::string getFilename(const llvm::Function &func);

void setBBId(llvm::BasicBlock &bb, BBId id);

void setBBIds(llvm::Module &mod);

std::optional<BBId> getBBId(const llvm::BasicBlock &bb);

std::optional<Lines> getBBLines(const llvm::BasicBlock &bb);

std::optional<LineRange> getBBLineRange(const llvm::BasicBlock &bb);

std::optional<Lines> getFunctionLines(const llvm::Function &func);

std::optional<LineRange> getFunctionLineRange(const llvm::Function &func);
};  // namespace LLVMUtils

}  // namespace sfi

#endif  // PI_LLVMUTILS_H
