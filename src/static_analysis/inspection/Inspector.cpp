#include "Inspector.h"

#include "SVF-FE/PAGBuilder.h"
#include "WPA/Andersen.h"
#include "utils/LLVMUtils.h"

using namespace std;

std::vector<FuncInfo> Inspector::getFuncInfo(SVF::SVFModule *svfModule) {
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
                LineRange lineRange = LLVMUtils::getLineRange(lineNumbers);
                bool reachableFromMain = callNode.second->isReachableFromProgEntry();

                funcInfos.emplace_back(FuncInfo(name, filename, lineNumbers, lineRange, reachableFromMain));
            }
        }
    }

    return funcInfos;
}
