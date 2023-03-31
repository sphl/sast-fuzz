#include "Inspector.h"
#include "SVF-FE/LLVMUtil.h"
#include "utils/LLVMUtils.h"

#include <iostream>

#define LLVM_DWARF_VERSION(moduleSet) ((moduleSet)->getMainLLVMModule()->getDwarfVersion())

using namespace std;

static llvm::cl::opt<std::string>
        InputFilename(llvm::cl::Positional, llvm::cl::desc("<input bitcode>"), llvm::cl::init("-"));

int main(int argc, char **argv) {
    int arg_num = 0;
    char **arg_value = new char *[argc];
    std::vector<std::string> moduleNameVec;
    SVF::SVFUtil::processArguments(argc, argv, arg_num, arg_value, moduleNameVec);
    llvm::cl::ParseCommandLineOptions(arg_num, arg_value, "SASTFuzz Program Inspector\n");

    SVF::SVFModule *svfModule = SVF::LLVMModuleSet::getLLVMModuleSet()->buildSVFModule(moduleNameVec);

    assert(LLVM_DWARF_VERSION(SVF::LLVMModuleSet::getLLVMModuleSet()) > 0 &&
           "ERROR: Bitcode file doesn't contain debug information!");

    vector<FuncInfo> funcInfos = Inspector::getFuncInfo(svfModule);

    for (auto func : funcInfos) {
        cout << func << endl;
    }

    return 0;
}