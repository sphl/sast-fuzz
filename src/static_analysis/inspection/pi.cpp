#include "SVF-FE/LLVMUtil.h"
#include "SVF-FE/PAGBuilder.h"
#include "Util/Options.h"
#include "WPA/Andersen.h"
#include "utils/LLVMUtils.h"

#include <iostream>

using namespace llvm;
using namespace SVF;

static llvm::cl::opt<std::string> InputFilename(cl::Positional, llvm::cl::desc("<input bitcode>"), llvm::cl::init("-"));

int main(int argc, char **argv) {
    int arg_num = 0;
    char **arg_value = new char *[argc];
    std::vector<std::string> moduleNameVec;
    SVFUtil::processArguments(argc, argv, arg_num, arg_value, moduleNameVec);
    cl::ParseCommandLineOptions(arg_num, arg_value, "SVF test program\n");

    SVFModule *svfModule = LLVMModuleSet::getLLVMModuleSet()->buildSVFModule(moduleNameVec);

    assert(LLVMModuleSet::getLLVMModuleSet()->getMainLLVMModule()->getDwarfVersion() > 0 &&
           "ERROR: Bitcode file doesn't contain debug information!");

    PAGBuilder builder;
    PAG *pag = builder.build(svfModule);

    Andersen *ander = AndersenWaveDiff::createAndersenWaveDiff(pag);

    PTACallGraph *callGraph = ander->getPTACallGraph();

    for (auto callNode : *callGraph) {
        const SVFFunction *svfFunc = callNode.second->getFunction();
        if (!svfFunc->isDeclaration()) {
            auto lineRange = LLVMUtils::getFunctionLineRange(*svfFunc->getLLVMFun());

            std::cout << callNode.first << ":" << LLVMUtils::getFilename(*svfFunc->getLLVMFun()) << ":"
                      << svfFunc->getName().str() << (callNode.second->isReachableFromProgEntry() ? "*" : "") << ":";
            if (!lineRange.has_value()) {
                std::cout << "-\n";
            } else {
                std::cout << "[" << lineRange.value().first << "," << lineRange.value().second << "]\n";
            }
        }
    }

    return 0;
}