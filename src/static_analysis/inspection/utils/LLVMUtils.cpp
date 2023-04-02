#include "LLVMUtils.h"

#include "llvm/IR/DebugInfo.h"

#include <filesystem>
#include <set>

using namespace std;
using namespace std::filesystem;
using namespace llvm;

string LLVMUtils::getFilename(const Function &func) {
    return path(func.getSubprogram()->getFilename().str()).filename();
}

LineRange LLVMUtils::computeRange(const Lines &lineNumbers) {
    LineNumber min = *min_element(lineNumbers.begin(), lineNumbers.end());
    LineNumber max = *max_element(lineNumbers.begin(), lineNumbers.end());

    return LineRange(min, max);
}

optional<Lines> LLVMUtils::getBBLines(const BasicBlock &bb) {
    Lines lineNumbers;

    const Function *parentFunc = bb.getParent();

    for (auto &inst : bb) {
        //if (inst.hasMetadata()) {
        auto &debugLoc = inst.getDebugLoc();
        if (debugLoc) {
            LineNumber line = debugLoc.getLine();
            if (line > 0) {
                assert(line >= parentFunc->getSubprogram()->getLine() &&
                       "ERROR: One of the analyzed instructions is located outside the corresponding function, e.g. in "
                       "a C macro, and the passed bitcode file was not compiled with '-g -O0 -fno-inline'. In this "
                       "case, we cannot reliably determine the line range of the function!");
                lineNumbers.insert(line);
            }
        }
        //}
    }

    if (lineNumbers.empty()) {
        return nullopt;
    } else {
        return lineNumbers;
    }
}

optional<LineRange> LLVMUtils::getBBLineRange(const BasicBlock &bb) {
    auto optLines = getBBLines(bb);

    if (!optLines.has_value()) {
        return nullopt;
    } else {
        Lines lineNumbers = optLines.value();

        return computeRange(lineNumbers);
    }
}

optional<Lines> LLVMUtils::getFunctionLines(const Function &func) {
    assert(!func.isDeclaration());

    if (!func.hasMetadata()) {
        return nullopt;
    }

    Lines lineNumbers;

    for (auto &bb : func) {
        auto optLines = getBBLines(bb);

        if (optLines.has_value()) {
            lineNumbers.merge(optLines.value());
        }
    }

    if (lineNumbers.empty()) {
        return nullopt;
    } else {
        return lineNumbers;
    }
}

optional<LineRange> LLVMUtils::getFunctionLineRange(const Function &func) {
    auto optLines = getFunctionLines(func);

    if (!optLines.has_value()) {
        return nullopt;
    } else {
        Lines lineNumbers = optLines.value();

        return computeRange(lineNumbers);
    }
}
