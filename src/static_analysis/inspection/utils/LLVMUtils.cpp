#include "LLVMUtils.h"

#include "llvm/IR/DebugInfo.h"

#include <filesystem>
#include <set>

using namespace std;
using namespace std::filesystem;
using namespace llvm;

string LLVMUtils::getFilename(const Function *func) {
    return path(func->getSubprogram()->getFilename().str()).filename();
}

optional<LineRange> LLVMUtils::getBBLineRange(const BasicBlock &bb) {
    set<LineNumber> lineNumbers;

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
        LineNumber min = *min_element(lineNumbers.begin(), lineNumbers.end());
        LineNumber max = *max_element(lineNumbers.begin(), lineNumbers.end());

        return LineRange(min, max);
    }
}

optional<LineRange> LLVMUtils::getFunctionLineRange(const Function *func) {
    assert(!func->isDeclaration());

    if (!func->hasMetadata()) {
        return nullopt;
    }

    LineNumber lineMin = UINT_MAX;
    LineNumber lineMax = 0;

    for (auto &bb : *func) {
        auto lineRange = getBBLineRange(bb);

        if (lineRange.has_value()) {
            lineMin = min(lineMin, lineRange->first);
            lineMax = max(lineMax, lineRange->second);
        }
    }

    if (lineMax == 0) {
        return nullopt;
    } else {
        return LineRange(lineMin, lineMax);
    }
}
