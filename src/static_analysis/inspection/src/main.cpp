#include <SVF-FE/LLVMUtil.h>
#include <SVF-FE/PAGBuilder.h>
#include <WPA/Andersen.h>

#include <sfi/func_info.h>
#include <sfi/io.h>
#include <sfi/llvm_utils.h>
#include <sfi/pretty_printer.h>

#define LLVM_MODULE(moduleSet) ((moduleSet)->getMainLLVMModule())
#define LLVM_DWARF_VERSION(moduleSet) (LLVM_MODULE(moduleSet)->getDwarfVersion())

using namespace std;
using namespace sfi;

static llvm::cl::opt<std::string> inputFile(llvm::cl::Positional, llvm::cl::desc("<bitcode file>"));

static llvm::cl::opt<std::string> outputFile(llvm::cl::Positional, llvm::cl::desc("<JSON file>"));

vector<FuncInfo> getFuncInfo(SVF::PAG *pag) {
    SVF::Andersen *ander = SVF::AndersenWaveDiff::createAndersenWaveDiff(pag);

    SVF::PTACallGraph *callGraph = ander->getPTACallGraph();

    vector<FuncInfo> funcInfos;

    for (auto callNode : *callGraph) {
        const llvm::Function &llvmFunc = *callNode.second->getFunction()->getLLVMFun();
        if (!llvmFunc.isDeclaration()) {
            auto optLineNumbers = llvm_utils::getFunctionLines(llvmFunc);
            if (optLineNumbers.has_value()) {
                string name = llvmFunc.getName().str();
                string filename = llvm_utils::getFilename(llvmFunc);
                Lines lineNumbers = optLineNumbers.value();
                LineRange lineRange = llvm_utils::computeRange(lineNumbers);
                bool reachableFromMain = callNode.second->isReachableFromProgEntry();

                set<BBInfo> blockInfos;
                for (auto &bb : llvmFunc) {
                    auto optBBLineNumbers = llvm_utils::getBBLines(bb);
                    if (optBBLineNumbers.has_value()) {
                        BBId id = llvm_utils::getBBId(bb).value();
                        Lines bbLines = optBBLineNumbers.value();
                        LineRange bbLineRange = llvm_utils::computeRange(bbLines);

                        blockInfos.insert(BBInfo(id, bbLines, bbLineRange));
                    }
                }

                funcInfos.emplace_back(FuncInfo(name, filename, lineNumbers, lineRange, reachableFromMain, blockInfos));
            }
        }
    }

    return funcInfos;
}

map<BBId, set<BBId>> getICFGInfo(SVF::PAG *pag) {
    SVF::ICFG *icfg = pag->getICFG();

    map<BBId, set<BBId>> icfgInfo;

    for (auto nodeInfo : *icfg) {
        SVF::ICFGNode *srcNode = nodeInfo.second;

        if (srcNode->getBB() != nullptr) {
            // TODO: Check return values!
            BBId srcBBId = llvm_utils::getBBId(*srcNode->getBB()).value();

            cout << "Node-ID: " << srcNode->getId() << " --> BB-ID: " << srcBBId << endl;

            for (auto edge : srcNode->getOutEdges()) {
                assert(srcNode->getId() == edge->getSrcNode()->getId());

                SVF::ICFGNode *dstNode = edge->getDstNode();

                if (dstNode->getBB() != nullptr) {
                    BBId dstBBId = llvm_utils::getBBId(*dstNode->getBB()).value();

                    // TODO: Only allow "srcBBId == dstBBId" if rec. function call (... or loop iteration)
                    icfgInfo[srcBBId].insert(dstBBId);
                }
            }
        }
    }

    return icfgInfo;
}

int main(int argc, char **argv) {
    int arg_num = 0;
    char **arg_value = new char *[argc];
    std::vector<std::string> moduleNameVec;
    SVF::SVFUtil::processArguments(argc, argv, arg_num, arg_value, moduleNameVec);
    llvm::cl::ParseCommandLineOptions(arg_num, arg_value, "SASTFuzz Inspector\n");

    SVF::SVFModule *svfModule = SVF::LLVMModuleSet::getLLVMModuleSet()->buildSVFModule(moduleNameVec);

    assert(LLVM_DWARF_VERSION(SVF::LLVMModuleSet::getLLVMModuleSet()) > 0 &&
           "ERROR: Bitcode file doesn't contain debug information!");

    SVF::PAGBuilder builder;
    SVF::PAG *pag = builder.build(svfModule);

    llvm_utils::setBBIds(*LLVM_MODULE(SVF::LLVMModuleSet::getLLVMModuleSet()));

    auto funcInfos = getFuncInfo(pag);
    auto icfgInfos = getICFGInfo(pag);

    JSONPrinter printer;

    printer.printToFile(outputFile, funcInfos, icfgInfos);

    return 0;
}