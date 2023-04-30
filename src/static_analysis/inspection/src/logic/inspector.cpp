#include <SVF-FE/LLVMUtil.h>
#include <SVF-FE/PAGBuilder.h>
#include <WPA/Andersen.h>

#include <sfi/inspector.h>
#include <sfi/llvm_utils.h>

using namespace std;
using namespace sfi;

/**
 * Macro to get the main LLVM module from a given set of modules.
 *
 * @param moduleSet A pointer to the set of modules.
 * @return The main LLVM module of the given module set.
 */
#define LLVM_MODULE(moduleSet) ((moduleSet)->getMainLLVMModule())

/**
 * Macro to get the DWARF version of the main LLVM module in a given set of modules.
 *
 * @param moduleSet A pointer to the set of modules.
 * @return The DWARF version of the main LLVM module of the given module set.
 */
#define LLVM_DWARF_VERSION(moduleSet) (LLVM_MODULE(moduleSet)->getDwarfVersion())

Inspector::Inspector(string bitcodeFile) noexcept(false) {
    // Build an SVFModule object from the bitcode file
    SVF::SVFModule *svfModule = SVF::LLVMModuleSet::getLLVMModuleSet()->buildSVFModule({bitcodeFile});

    // Check if the DWARF version of the LLVM module is 0, which means there is missing debug information
    if (LLVM_DWARF_VERSION(SVF::LLVMModuleSet::getLLVMModuleSet()) == 0) {
        // Throw a MissingDebugInfoException if debug information is missing
        throw MissingDebugInfoException();
    }
    // Set basic block IDs for the LLVM module
    llvm_utils::setBBIds(*LLVM_MODULE(SVF::LLVMModuleSet::getLLVMModuleSet()));

    // Build a PAG (Pointer Analysis Graph) object from the SVFModule object using a PAGBuilder
    SVF::PAGBuilder builder;
    pag = unique_ptr<SVF::PAG>(builder.build(svfModule));
}

vector<FuncInfo> Inspector::getFuncInfos() {
    // Create an Andersen wave-diff pointer analysis object from the PAG
    SVF::Andersen *ander = SVF::AndersenWaveDiff::createAndersenWaveDiff(pag.get());

    // Get the pointer analysis call graph
    SVF::PTACallGraph *callGraph = ander->getPTACallGraph();

    // Create an empty vector of function infos
    vector<FuncInfo> funcInfos;

    // Iterate over all the call nodes in the call graph
    for (auto callNode : *callGraph) {
        // Get the LLVM function from the call node
        const llvm::Function &llvmFunc = *callNode.second->getFunction()->getLLVMFun();

        // Check if the function is not a declaration
        if (!llvmFunc.isDeclaration()) {
            // Get the line numbers of the function if available
            auto optLineNumbers = llvm_utils::getFunctionLines(llvmFunc);

            // Check if the line numbers are available
            if (optLineNumbers.has_value()) {
                // Extract the required information of the function
                string name = llvmFunc.getName().str();
                string filename = llvm_utils::getFilename(llvmFunc);
                Lines lineNumbers = optLineNumbers.value();
                LineRange lineRange = llvm_utils::computeRange(lineNumbers);
                bool reachableFromMain = callNode.second->isReachableFromProgEntry();

                // Create an empty set of basic block infos
                set<BBInfo> blockInfos;

                // Iterate over all the basic blocks in the function
                for (auto &bb : llvmFunc) {
                    // Get the line numbers of the basic block if available
                    auto optBBLineNumbers = llvm_utils::getBBLines(bb);

                    // Check if the line numbers are available
                    if (optBBLineNumbers.has_value()) {
                        // Extract the required information of the basic block
                        BBId id = llvm_utils::getBBId(bb).value();
                        Lines bbLines = optBBLineNumbers.value();
                        LineRange bbLineRange = llvm_utils::computeRange(bbLines);

                        // Insert the basic block info into the set
                        blockInfos.insert(BBInfo(id, bbLines, bbLineRange));
                    }
                }
                // Create a FuncInfo object from the extracted information and insert it into the vector
                funcInfos.emplace_back(FuncInfo(name, filename, lineNumbers, lineRange, reachableFromMain, blockInfos));
            }
        }
    }
    // Return the vector of function infos
    return funcInfos;
}
