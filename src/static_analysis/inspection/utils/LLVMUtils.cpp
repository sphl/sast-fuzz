#include "LLVMUtils.h"

#include "llvm/IR/DebugInfo.h"

#include <filesystem>
#include <set>

using namespace std::filesystem;

string LLVMUtils::getFilename(const Function *func) {
    return path(func->getSubprogram()->getFilename().str()).filename();
}

optional<pair<LineNumber, LineNumber>> LLVMUtils::getLineRange(const Function *func) {
    assert(!func->isDeclaration());

    if (!func->hasMetadata()) {
        return nullopt;
    }

    set<LineNumber> lineNumbers;

    for (auto &BB : *func) {
        for (auto &inst : BB) {
            //if (inst.hasMetadata()) {
            auto &debugLoc = inst.getDebugLoc();
            if (debugLoc) {
                LineNumber line = debugLoc.getLine();
                if (line > 0) {
                    assert(line >= func->getSubprogram()->getLine() &&
                           "ERROR: One of the analyzed instructions is located outside the corresponding function, "
                           "e.g. in a C macro, and the passed bitcode file was not compiled with '-g -O0 -fno-inline'. "
                           "In this case, we cannot reliably determine the line range of the function!");
                    lineNumbers.insert(line);
                }
            }
            //}
        }
    }

    if (lineNumbers.empty()) {
        return nullopt;
    } else {
        LineNumber min = *min_element(lineNumbers.begin(), lineNumbers.end());
        LineNumber max = *max_element(lineNumbers.begin(), lineNumbers.end());

        return pair<LineNumber, LineNumber>(min, max);
    }
}
