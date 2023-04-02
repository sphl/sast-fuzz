#include "SVF-FE/LLVMUtil.h"
#include "SVF-FE/PAGBuilder.h"
#include "WPA/Andersen.h"
#include "container/FuncInfo.h"
#include "utils/LLVMUtils.h"

#include <iostream>

#define LLVM_DWARF_VERSION(moduleSet) ((moduleSet)->getMainLLVMModule()->getDwarfVersion())

using namespace std;

static llvm::cl::opt<std::string>
        InputFilename(llvm::cl::Positional, llvm::cl::desc("<input bitcode>"), llvm::cl::init("-"));

vector<FuncInfo> getFuncInfo(SVF::SVFModule *svfModule) {
    SVF::PAGBuilder builder;
    SVF::PAG *pag = builder.build(svfModule);

    SVF::Andersen *ander = SVF::AndersenWaveDiff::createAndersenWaveDiff(pag);

    SVF::PTACallGraph *callGraph = ander->getPTACallGraph();

    vector<FuncInfo> funcInfos;

    for (auto callNode : *callGraph) {
        const llvm::Function &llvmFunc = *callNode.second->getFunction()->getLLVMFun();
        if (!llvmFunc.isDeclaration()) {
            auto optLineNumbers = LLVMUtils::getFunctionLines(llvmFunc);
            if (optLineNumbers.has_value()) {
                string name = llvmFunc.getName().str();
                string filename = LLVMUtils::getFilename(llvmFunc);
                Lines lineNumbers = optLineNumbers.value();
                LineRange lineRange = LLVMUtils::computeRange(lineNumbers);
                bool reachableFromMain = callNode.second->isReachableFromProgEntry();

                funcInfos.emplace_back(FuncInfo(name, filename, lineNumbers, lineRange, reachableFromMain));
            }
        }
    }

    return funcInfos;
}

int main(int argc, char **argv) {
    int arg_num = 0;
    char **arg_value = new char *[argc];
    std::vector<std::string> moduleNameVec;
    SVF::SVFUtil::processArguments(argc, argv, arg_num, arg_value, moduleNameVec);
    llvm::cl::ParseCommandLineOptions(arg_num, arg_value, "SASTFuzz Program Inspector\n");

    SVF::SVFModule *svfModule = SVF::LLVMModuleSet::getLLVMModuleSet()->buildSVFModule(moduleNameVec);

    assert(LLVM_DWARF_VERSION(SVF::LLVMModuleSet::getLLVMModuleSet()) > 0 &&
           "ERROR: Bitcode file doesn't contain debug information!");

    vector<FuncInfo> funcInfos = getFuncInfo(svfModule);

    for (auto func : funcInfos) {
        cout << func << endl;
    }

    return 0;
}