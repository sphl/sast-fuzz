/*
    Instrument critical BBs
*/

#include "SVF-FE/LLVMUtil.h"
#include "SVF-FE/PAGBuilder.h"
#include "WPA/Andersen.h"
#include "llvm/IR/CFG.h"

#include <fstream>
#include <sstream>

using namespace SVF;
using namespace llvm;
using namespace std;

#define MAP_SIZE_POW2 16
#define MAP_SIZE (1 << MAP_SIZE_POW2)

static llvm::cl::opt<std::string> InputFilename(cl::Positional, llvm::cl::desc("<input bitcode>"), llvm::cl::init("-"));

static llvm::cl::opt<std::string> TargetsFile("targets", llvm::cl::desc("specify targes file"), llvm::cl::Required);

// clang-format off
SVFModule *svfModule; /**< An instance of the current SVF module.   */
ICFG *icfg;           /**< An instance of the current inter-procedural control-flow graph (iCFG). */
Module *M;            /**< An instance of the current LLVM module.  */
LLVMContext *C;       /**< An instance of the current LLVM context. */

std::map<const SVFFunction *, double> dTf;    /**< A map storing the function distance (harmonic mean) to each target.    */
std::map<BasicBlock *, double> dTb;           /**< A map storing the basic block distance (harmonic mean) to each target. */
std::set<const BasicBlock *> targets_llvm_bb; /**< A set of LLVM basic blocks representing the target blocks.             */
std::map<BasicBlock *, std::set<BasicBlock *>> critical_bbs; /**< A map storing the critical blocks for each basic block. */
std::map<BasicBlock *, std::set<BasicBlock *>> solved_bbs;   /**< A map storing the solved blocks for each basic block.   */
std::map<Function *, std::set<BasicBlock *>> taint_bbs;      /**< A map storing the tainted blocks for each function.     */
std::map<Function *, std::set<BasicBlock *>> func_targets;   /**< A map storing the target blocks for each function.      */

std::map<llvm::BasicBlock *, std::vector<std::string>> condition_infos;  /**< A map storing the condition information for each basic block. */
std::map<llvm::BasicBlock *, std::vector<llvm::Value *>> condition_vals; /**< A map storing the condition values for each basic block.      */
std::map<llvm::BasicBlock *, uint32_t> condition_ids; /**< A map storing the condition IDs for each basic block. */
std::map<llvm::BasicBlock *, uint32_t> critical_ids;  /**< A map storing the critical IDs for each basic block.  */
uint32_t cond_instrument_num = 0; /**< The number of if-condition instrumentations. */
// clang-format on

GlobalVariable *cvar_map_ptr;
GlobalVariable *cond_map_ptr;

/**
 * Retrieves the debug information (source location) associated with a given basic block.
 *
 * @param bb The basic block to retrieve the debug information from.
 * @return The debug information (source location) as a string.
 */
std::string getDebugInfo(BasicBlock *bb) {
    for (auto & it : *bb) {
        std::string str = SVFUtil::getSourceLoc(&it);
        if (str != "{  }" && str.find("ln: 0  cl: 0") == std::string::npos) {
            return str;
        }
    }
    return "{ }";
}

/**
 * Checks if there is a control-flow edge forming a loop between two basic blocks.
 *
 * @param loop_info Pointer to the LoopInfoBase object.
 * @param src The source basic block.
 * @param dst The destination basic block.
 * @return True if there is a loop edge, false otherwise.
 */
bool isCircleEdge(llvm::LoopInfoBase<llvm::BasicBlock, llvm::Loop> *loop_info, BasicBlock *src, BasicBlock *dst) {
    if (loop_info->getLoopFor(src) == loop_info->getLoopFor(dst)) {
        if (!(loop_info->isLoopHeader(src)) && loop_info->isLoopHeader(dst)) {
            return true;
        }
    }
    return false;
}

/**
 * Counts the control-flow graph distance between the specified target nodes and their respective functions.
 *
 * @param ids A vector of target node IDs.
 */
void countCGDistance(const std::vector<NodeID> &ids) {
    FIFOWorkList<const FunEntryBlockNode *> worklist;
    std::vector<std::map<const SVFFunction *, uint32_t>> dtf;

    // Calculate the function distance to each target.
    for (NodeID id : ids) {
        std::set<const FunEntryBlockNode *> visited;

        ICFGNode *iNode = icfg->getICFGNode(id);
        FunEntryBlockNode *fNode = icfg->getFunEntryBlockNode(iNode->getFun());
        worklist.push(fNode);

        std::map<const SVFFunction *, uint32_t> df;
        df[iNode->getFun()] = 1;

        while (!worklist.empty()) {
            const FunEntryBlockNode *vNode = worklist.pop();

            for (auto it = vNode->InEdgeBegin(), eit = vNode->InEdgeEnd(); it != eit; ++it) {
                ICFGEdge *edge = *it;
                ICFGNode *srcNode = edge->getSrcNode();
                const SVFFunction *svffunc = srcNode->getFun();
                FunEntryBlockNode *vfNode = icfg->getFunEntryBlockNode(svffunc);

                if ((df.count(svffunc) == 0) || (df[svffunc] > (df[vNode->getFun()] + 1))) {
                    df[svffunc] = df[vNode->getFun()] + 1;
                    worklist.push(vfNode);
                }
            }
        }
        dtf.push_back(df);
    }

    // Calculate the (harmonic) distance to all targets
    for (auto svffun : *svfModule) {
        double df_tmp = 0;
        bool flag = false;

        for (auto df : dtf) {
            if (df.count(svffun) != 0) {
                if (df[svffun] != 0) {
                    df_tmp += (double)1 / df[svffun];
                }
                flag = true;
            }
        }

        if (flag) {
            if (df_tmp != 0) {
                dTf[svffun] = (double)1 / df_tmp;
            } else {
                dTf[svffun] = 0;
            }
        }
    }
}

/**
 * Counts the control-flow graph distance between basic blocks within a function.
 *
 * @param svffun A SVFFunction pointer representing the function.
 */
void countCFGDistance(const SVFFunction *svffun) {
    std::map<BasicBlock *, std::map<BasicBlock *, uint32_t>> dtb;
    std::set<BasicBlock *> target_bbs;

    for (auto &bit : *svffun->getLLVMFun()) {
        BasicBlock *bb = &bit;
        for (BasicBlock::iterator it = bb->begin(), eit = bb->end(); it != eit; ++it) {
            Instruction *inst = &(*it);
            if (auto *CB = dyn_cast<CallBase>(inst)) {
                if (!CB->getCalledFunction()) {
                    continue;
                }

                const SVFFunction *svffunc_tmp = svfModule->getSVFFunction(CB->getCalledFunction());

                if (dTf.count(svffunc_tmp) != 0) {
                    if (target_bbs.find(bb) != target_bbs.end()) {
                        if (dTb[bb] > 10 * dTf[svffunc_tmp]) {
                            dTb[bb] = 10 * dTf[svffunc_tmp];
                        }
                    } else {
                        target_bbs.insert(bb);
                        dTb[bb] = 10 * dTf[svffunc_tmp];
                    }
                }
            }
        }

        if (targets_llvm_bb.find(bb) != targets_llvm_bb.end()) {
            dTb[bb] = 0;
            target_bbs.insert(bb);
        }
    }

    func_targets[svffun->getLLVMFun()] = target_bbs;

    std::set<BasicBlock *> tmp_taint_bbs;

    llvm::DominatorTree DT = llvm::DominatorTree();
    llvm::PostDominatorTree PDT = llvm::PostDominatorTree();
    auto *LoopInfo = new llvm::LoopInfoBase<llvm::BasicBlock, llvm::Loop>();

    if (!(svffun->getLLVMFun()->isDeclaration())) {
        DT.recalculate(*(svffun->getLLVMFun()));
        PDT.recalculate(*(svffun->getLLVMFun()));
        LoopInfo->releaseMemory();
        LoopInfo->analyze(DT);
    }

    for (BasicBlock *bb : target_bbs) {
        FIFOWorkList<BasicBlock *> worklist;
        std::set<BasicBlock *> visited;
        worklist.push(bb);
        while (!worklist.empty()) {
            BasicBlock *vbb = worklist.pop();
            tmp_taint_bbs.insert(vbb);
            for (BasicBlock *srcbb : predecessors(vbb)) {
                if (visited.find(srcbb) == visited.end() && !isCircleEdge(LoopInfo, srcbb, vbb)) {
                    worklist.push(srcbb);
                    visited.insert(srcbb);
                }
            }
        }
    }

    taint_bbs[svffun->getLLVMFun()] = tmp_taint_bbs;

    for (BasicBlock *bb : target_bbs) {
        std::map<BasicBlock *, uint32_t> db;
        db[bb] = 0;
        FIFOWorkList<BasicBlock *> worklist;
        std::set<BasicBlock *> visited;
        worklist.push(bb);
        while (!worklist.empty()) {
            BasicBlock *vbb = worklist.pop();
            for (BasicBlock *srcbb : predecessors(vbb)) {
                if ((db.count(srcbb) == 0) || (db[srcbb] > (db[vbb] + 1))) {
                    db[srcbb] = db[vbb] + 1;
                    worklist.push(srcbb);
                }
            }
        }
        dtb[bb] = db;
    }

    for (auto &bit : *svffun->getLLVMFun()) {
        BasicBlock *bb = &bit;

        if (target_bbs.find(bb) != target_bbs.end()) {
            continue;
        }

        double db_tmp = 0;
        bool flag = false;
        for (auto db : dtb) {
            if (db.second.count(bb)) {
                db_tmp += (double)1 / (db.second[bb] + dTb[db.first]);
                flag = true;
            }
        }

        if (flag) {
            dTb[bb] = (double)1 / db_tmp;
        }
    }
}

/**
 * Counts the vanilla distance (control-flow graph and call graph distance) between target nodes.
 *
 * @param target_ids A vector of target node IDs.
 */
void countVanillaDistance(const std::vector<NodeID> &target_ids) {
    FIFOWorkList<const ICFGNode *> worklist;
    std::set<const ICFGNode *> visited;

    for (NodeID id : target_ids) {
        ICFGNode *iNode = icfg->getICFGNode(id);
        targets_llvm_bb.insert(iNode->getBB());
    }

    countCGDistance(target_ids);

    for (auto svffun : *svfModule) {
        countCFGDistance(svffun);
    }
}

/**
 * Identifies the critical basic blocks in the program based on control-flow and taint analysis.
 */
void identifyCriticalBB() {
    for (auto svffun : *svfModule) {
        for (Function::iterator bit = svffun->getLLVMFun()->begin(), ebit = svffun->getLLVMFun()->end(); bit != ebit;
             ++bit) {
            BasicBlock *bb = &*(bit);
            std::set<BasicBlock *> tmp_critical_bbs;
            std::set<BasicBlock *> tmp_solved_bbs;
            if (!bb->getSingleSuccessor() && taint_bbs.count(svffun->getLLVMFun()) &&
                taint_bbs[svffun->getLLVMFun()].count(bb)) {
                for (BasicBlock *dstbb : successors(bb)) {
                    if (taint_bbs[svffun->getLLVMFun()].count(dstbb) == 0) {
                        tmp_critical_bbs.insert(dstbb);
                    } else {
                        tmp_solved_bbs.insert(dstbb);
                    }
                }
            }
            if (!tmp_critical_bbs.empty()) {
                critical_bbs[bb] = tmp_critical_bbs;
                solved_bbs[bb] = tmp_solved_bbs;
            }
        }
    }

    int temp_count = 0;
    int temp_count2 = 0;
    int temp_count3 = 0;
    for (const auto &item : critical_bbs) {
        llvm::BasicBlock *bb = item.first;
        llvm::Instruction &inst = bb->back();
        if (auto *br = dyn_cast<BranchInst>(&inst)) {
            Value *br_v = br->getOperand(0);
            temp_count2++;
            if (auto *cmp = dyn_cast<CmpInst>(br_v)) {
                temp_count++;
            }
        } else if (dyn_cast<SwitchInst>(&inst)) {
            temp_count3++;
        }
    }
}

/**
 * Instruments the program by adding the necessary code to collect distance information.
 */
void instrument() {
    ofstream outfile("distance.txt", std::ios::out);
    ofstream outfile2("functions.txt", std::ios::out);
    ofstream outfile3("targets.txt", std::ios::out);
    uint32_t bb_id = 0;
    uint32_t func_id = 0;
    uint32_t target_id = 0;
    uint32_t v_instrument_num = 0;
    uint32_t c_instrument_num = 0;

    IntegerType *Int8Ty = IntegerType::getInt8Ty(*C);
    IntegerType *Int32Ty = IntegerType::getInt32Ty(*C);
    IntegerType *Int64Ty = IntegerType::getInt64Ty(*C);

    GlobalVariable *AFLMapPtr = (GlobalVariable *)M->getOrInsertGlobal(
            "__afl_area_ptr", PointerType::get(IntegerType::getInt8Ty(*C), 0), []() -> GlobalVariable * {
                return new GlobalVariable(*M, PointerType::get(IntegerType::getInt8Ty(M->getContext()), 0), false,
                                          GlobalValue::ExternalLinkage, nullptr, "__afl_area_ptr");
            });

    GlobalVariable *CBMapPtr = (GlobalVariable *)M->getOrInsertGlobal(
            "__critical_bb_ptr", PointerType::get(IntegerType::getInt8Ty(*C), 0), []() -> GlobalVariable * {
                return new GlobalVariable(*M, PointerType::get(IntegerType::getInt8Ty(M->getContext()), 0), false,
                                          GlobalValue::ExternalLinkage, nullptr, "__critical_bb_ptr");
            });

    // TODO: Check if this variable is needed?
    GlobalVariable *DBMapPtr = (GlobalVariable *)M->getOrInsertGlobal(
            "__distance_bb_ptr", PointerType::get(IntegerType::getInt8Ty(*C), 0), []() -> GlobalVariable * {
                return new GlobalVariable(*M, PointerType::get(IntegerType::getInt8Ty(M->getContext()), 0), false,
                                          GlobalValue::ExternalLinkage, nullptr, "__distance_bb_ptr");
            });

    IntegerType *LargestType = Int64Ty;
    ConstantInt *MapCntLoc = ConstantInt::get(LargestType, MAP_SIZE + 8);

    ConstantInt *MapDistLoc = ConstantInt::get(LargestType, MAP_SIZE);
    ConstantInt *One = ConstantInt::get(LargestType, 1);

    for (auto svffun : *svfModule) {
        bool flag = false;
        for (auto &bit : *svffun->getLLVMFun()) {
            BasicBlock *bb = &bit;
            if (dTb.count(bb)) {
                auto distance = (uint32_t)(100 * dTb[bb]);

                ConstantInt *Distance = ConstantInt::get(LargestType, (unsigned)distance);

                BasicBlock::iterator IP = bb->getFirstInsertionPt();
                llvm::IRBuilder<> IRB(&(*IP));

                /* Load SHM pointer */

                LoadInst *MapPtr = IRB.CreateLoad(AFLMapPtr);
                MapPtr->setMetadata(M->getMDKindID("nosanitize"), MDNode::get(*C, None));

                /* Add distance to shm[MAPSIZE] */

                Value *MapDistPtr = IRB.CreateBitCast(IRB.CreateGEP(MapPtr, MapDistLoc), LargestType->getPointerTo());
                LoadInst *MapDist = IRB.CreateLoad(MapDistPtr);
                MapDist->setMetadata(M->getMDKindID("nosanitize"), MDNode::get(*C, None));

                Value *IncrDist = IRB.CreateAdd(MapDist, Distance);
                IRB.CreateStore(IncrDist, MapDistPtr)->setMetadata(M->getMDKindID("nosanitize"), MDNode::get(*C, None));

                /* Increase count at shm[MAPSIZE + (4 or 8)] */

                Value *MapCntPtr = IRB.CreateBitCast(IRB.CreateGEP(MapPtr, MapCntLoc), LargestType->getPointerTo());
                LoadInst *MapCnt = IRB.CreateLoad(MapCntPtr);
                MapCnt->setMetadata(M->getMDKindID("nosanitize"), MDNode::get(*C, None));

                Value *IncrCnt = IRB.CreateAdd(MapCnt, One);
                IRB.CreateStore(IncrCnt, MapCntPtr)->setMetadata(M->getMDKindID("nosanitize"), MDNode::get(*C, None));

                if (distance == 0) {
                    ConstantInt *TFlagLoc = ConstantInt::get(LargestType, MAP_SIZE + 16 + target_id);
                    Value *TFlagPtr = IRB.CreateGEP(MapPtr, TFlagLoc);
                    ConstantInt *FlagOne = ConstantInt::get(Int8Ty, 1);
                    IRB.CreateStore(FlagOne, TFlagPtr)
                            ->setMetadata(M->getMDKindID("nosanitize"), MDNode::get(*C, None));
                    outfile3 << target_id << " " << getDebugInfo(bb) << std::endl;
                    target_id++;
                }

                if (critical_bbs.count(bb)) {
                    for (auto cbb : critical_bbs[bb]) {
                        BasicBlock::iterator IP2 = cbb->getFirstInsertionPt();
                        llvm::IRBuilder<> IRB2(&(*IP2));

                        LoadInst *CBPtr = IRB2.CreateLoad(CBMapPtr);
                        CBPtr->setMetadata(M->getMDKindID("nosanitize"), MDNode::get(*C, None));

                        // If a critical BB was executed, the (coverage) flag is set to 1 (even if the BB was exercised
                        // multiple times), otherwise the flag is 0.
                        ConstantInt *CBIdx = ConstantInt::get(Int32Ty, bb_id);
                        ConstantInt *CBOne = ConstantInt::get(Int8Ty, 1);
                        Value *CBIdxPtr = IRB2.CreateGEP(CBPtr, CBIdx);
                        IRB2.CreateStore(CBOne, CBIdxPtr)
                                ->setMetadata(M->getMDKindID("nosanitize"), MDNode::get(*C, None));
                        c_instrument_num++;
                    }
                    critical_ids[bb] = bb_id;
                }

                if (solved_bbs.count(bb)) {
                    for (auto sbb : solved_bbs[bb]) {
                        BasicBlock::iterator IP2 = sbb->getFirstInsertionPt();
                        llvm::IRBuilder<> IRB2(&(*IP2));

                        LoadInst *CBPtr = IRB2.CreateLoad(CBMapPtr);
                        CBPtr->setMetadata(M->getMDKindID("nosanitize"), MDNode::get(*C, None));

                        ConstantInt *CBIdx = ConstantInt::get(Int32Ty, bb_id);
                        ConstantInt *CBOne = ConstantInt::get(Int8Ty, 2);
                        Value *CBIdxPtr = IRB2.CreateGEP(CBPtr, CBIdx);
                        IRB2.CreateStore(CBOne, CBIdxPtr)
                                ->setMetadata(M->getMDKindID("nosanitize"), MDNode::get(*C, None));
                    }
                }

                outfile << bb_id << " " << distance << " ";
                if (critical_bbs.count(bb)) {
                    outfile << 1 << " ";
                } else {
                    outfile << 0 << " ";
                }
                outfile << getDebugInfo(bb) << std::endl;

                bb_id++;

                flag = true;
                v_instrument_num++;
            }
        }

        if (flag) {
            outfile2 << func_id << " " << SVFUtil::getSourceLocOfFunction(svffun->getLLVMFun()) << std::endl;
            func_id++;
        }
    }

    outfile.close();
    outfile2.close();
    outfile3.close();
}

/**
 * Analyzes the if-conditions in the given SVF module.
 */
void analyzeCondition() {
    u32_t condition_id = 1;

    for (auto svffun : *svfModule) {
        for (auto &bit : *svffun->getLLVMFun()) {
            BasicBlock *bb = &bit;
            if (bb->getSingleSuccessor()) {
                continue;
            }
            llvm::Instruction &inst = bb->back();
            if (auto *br = dyn_cast<BranchInst>(&inst)) {
                Value *br_v = br->getOperand(0);
                if (auto *cmp = dyn_cast<CmpInst>(br_v)) {
                    std::vector<std::string> condition_info;
                    std::vector<llvm::Value *> condition_val;
                    Value *op1 = cmp->getOperand(0);
                    Value *op2 = cmp->getOperand(1);
                    std::string op1_ty = "none";
                    std::string op2_ty = "none";
                    std::string op1_val = "none";
                    std::string op2_val = "none";
                    bool need_record = false;
                    // if (llvm::LoadInst::classof(op1)) {
                    if (op1->getType()->isIntegerTy()) {
                        auto *int_ty = dyn_cast<IntegerType>(op1->getType());
                        op1_ty = "";
                        op1_ty += "int";
                        op1_ty += std::to_string(int_ty->getBitWidth());
                        if (int_ty->getBitWidth() >= 32) {
                            need_record = true;
                        }
                    }

                    if (op2->getType()->isIntegerTy()) {
                        auto *int_ty2 = dyn_cast<IntegerType>(op1->getType());
                        op2_ty = "";
                        op2_ty += "int";
                        op2_ty += std::to_string(int_ty2->getBitWidth());
                    }

                    if (!llvm::Constant::classof(op1)) {
                        op1_val = "var";
                    } else {
                        if (auto *constantint = llvm::dyn_cast<llvm::ConstantInt>(op1)) {
                            op1_val = std::to_string(constantint->getSExtValue());
                        }
                    }

                    if (!llvm::Constant::classof(op2)) {
                        op2_val = "var";
                    } else {
                        if (auto *constantint = llvm::dyn_cast<llvm::ConstantInt>(op2)) {
                            op2_val = std::to_string(constantint->getSExtValue());
                        }
                    }
                    if (auto *CB = dyn_cast<CallBase>(op1)) {
                        if (CB->getCalledFunction()) {
                            if (CB->getCalledFunction()->getName().str() == "strcmp") {
                                Value *arg1 = CB->getArgOperand(0);
                                Value *arg2 = CB->getArgOperand(1);
                                if (auto *get_element = dyn_cast<GetElementPtrInst>(arg2)) {
                                    if (auto *str_global = dyn_cast<GlobalVariable>(get_element->getPointerOperand())) {
                                        if (auto *str_val = dyn_cast<ConstantDataArray>(str_global->getInitializer())) {
                                            op1_ty = "str";
                                            op1_val = "var";
                                            op2_ty = "str_const";
                                            if (str_val->isString()) {
                                                // op2_val = str_val->getAsCString().str();
                                                op2_val = str_val->getAsString().str();
                                                op1 = arg1;
                                                op2 = arg2;
                                                if (op2_val.length() <= 8) {
                                                    need_record = true;
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                    if (need_record) {
                        condition_val.push_back(op1);
                        condition_val.push_back(op2);
                        condition_info.push_back(op1_ty);
                        condition_info.push_back(op2_ty);
                        condition_info.push_back(op1_val);
                        condition_info.push_back(op2_val);
                        condition_infos[bb] = condition_info;
                        condition_vals[bb] = condition_val;
                        condition_ids[bb] = condition_id;
                        condition_id++;
                    }
                }
            }
        }
    }
    ofstream outfile;
    outfile.open("condition_info.txt", std::ios::out);

    if (!outfile.is_open()) {
        std::cerr << "EError opening file" << std::endl;
        exit(1);
    }

    for (auto info : condition_infos) {
        if (critical_bbs.count(info.first)) {
            outfile << condition_ids[info.first] << " " << critical_ids[info.first] << " " << info.second[0] << " "
                    << info.second[1] << " " << info.second[2] << " " << info.second[3] << " " << std::endl;
        } else {
            outfile << condition_ids[info.first] << " none " << info.second[0] << " " << info.second[1] << " "
                    << info.second[2] << " " << info.second[3] << " " << std::endl;
        }
    }

    outfile.close();
}

/**
 * Instruments the basic block with the given variable and index.
 *
 * @param bb The basic block to instrument.
 * @param var The variable to instrument.
 * @param idx The index of the instrumented condition.
 */
void instrumentBB(llvm::BasicBlock *bb, llvm::Value *var, uint8_t idx) {
    // llvm::Instruction* I = &(bb->back());
    auto *term_inst = dyn_cast<Instruction>(bb->getTerminator());
    if (term_inst == nullptr) {
        return;
    }
    llvm::IRBuilder<> IRB(term_inst);
    auto *branch = dyn_cast<BranchInst>(term_inst);
    Value *branch_val = IRB.CreateZExt(branch->getCondition(), IRB.getInt8Ty());
    llvm::LoadInst *c_map_ptr = IRB.CreateLoad(cond_map_ptr);
    llvm::Value *cond_map_ptr_idx =
            IRB.CreateGEP(c_map_ptr, ConstantInt::get(IntegerType::getInt32Ty(*C), condition_ids[bb]));
    branch_val = IRB.CreateAdd(branch_val, ConstantInt::get(IntegerType::getInt8Ty(*C), 1));
    IRB.CreateStore(branch_val, cond_map_ptr_idx);
    llvm::LoadInst *map_ptr = IRB.CreateLoad(cvar_map_ptr);
    ConstantInt *cur_id = llvm::ConstantInt::get(IntegerType::getInt32Ty(*C), 2 * condition_ids[bb] + idx);
    llvm::Value *map_ptr_idx = IRB.CreateGEP(map_ptr, cur_id);
    Value *var_64 = IRB.CreateIntCast(var, IntegerType::getInt64Ty(*C), true);
    IRB.CreateStore(var_64, map_ptr_idx);
    cond_instrument_num++;
}

/**
 * Instruments the basic block with the given string variable.
 *
 * @param bb The basic block to instrument.
 * @param var The string variable to instrument.
 */
void instrumentString(llvm::BasicBlock *bb, llvm::Value *var) {
    // llvm::Instruction* I = &(bb->back());
    auto *term_inst = dyn_cast<Instruction>(bb->getTerminator());
    if (term_inst == nullptr) {
        return;
    }
    llvm::IRBuilder<> IRB(term_inst);
    auto *branch = dyn_cast<BranchInst>(term_inst);
    Value *branch_val = IRB.CreateZExt(branch->getCondition(), IRB.getInt8Ty());
    llvm::LoadInst *c_map_ptr = IRB.CreateLoad(cond_map_ptr);
    llvm::Value *cond_map_ptr_idx =
            IRB.CreateGEP(c_map_ptr, ConstantInt::get(IntegerType::getInt32Ty(*C), condition_ids[bb]));
    branch_val = IRB.CreateAdd(branch_val, ConstantInt::get(IntegerType::getInt8Ty(*C), 1));
    IRB.CreateStore(branch_val, cond_map_ptr_idx);

    // llvm::IRBuilder<> IRB(I);
    llvm::LoadInst *map_ptr = IRB.CreateLoad(cvar_map_ptr);
    ConstantInt *cur_id = llvm::ConstantInt::get(IntegerType::getInt32Ty(*C), 2 * condition_ids[bb]);
    llvm::Value *map_ptr_idx = IRB.CreateGEP(map_ptr, cur_id);
    llvm::Value *ptr_64 = IRB.CreatePointerCast(var, PointerType::get(IntegerType::getInt64Ty(*C), 0));
    llvm::Value *var_64 = IRB.CreateLoad(ptr_64);
    IRB.CreateStore(var_64, map_ptr_idx);
    cond_instrument_num++;
}

/**
 * Instruments the conditions based on the analyzed information.
 */
void instrumentCondition() {
    IntegerType *Int64Ty = IntegerType::getInt64Ty(*C);
    IntegerType *Int8Ty = IntegerType::getInt8Ty(*C);
    cvar_map_ptr =
            new GlobalVariable(*(LLVMModuleSet::getLLVMModuleSet()->getMainLLVMModule()), PointerType::get(Int64Ty, 0),
                               false, GlobalValue::ExternalLinkage, 0, "__cvar_map_ptr");
    cond_map_ptr =
            new GlobalVariable(*(LLVMModuleSet::getLLVMModuleSet()->getMainLLVMModule()), PointerType::get(Int8Ty, 0),
                               false, GlobalValue::ExternalLinkage, 0, "__cond_map_ptr");

    for (auto info : condition_infos) {
        // if ((info.second[0] == "int32" || info.second[0] == "int64") && (info.second[2] == "var")) {
        if ((info.second[0].find("int") != std::string::npos) && (info.second[2] == "var")) {
            // instrument here
            instrumentBB(info.first, condition_vals[info.first][0], 0);
        }

        // if ((info.second[1] == "int32" || info.second[1] == "int64") && (info.second[3] == "var")) {
        if ((info.second[1].find("int") != std::string::npos) && (info.second[3] == "var")) {
            // instrument here
            instrumentBB(info.first, condition_vals[info.first][1], 1);
        }

        if (info.second[1] == "str_const") {
            instrumentString(info.first, condition_vals[info.first][0]);
        }
    }
}

/**
 * Loads the target NodeIDs from the given file.
 *
 * @param filename The name of the file containing the targets.
 * @param delimiter The delimiter used in the file (default: ',').
 * @return A vector of loaded target NodeIDs.
 */
std::vector<NodeID> loadTargets(const std::string &filename, char delimiter = ',') {
    ifstream inFile(filename);
    if (!inFile) {
        std::cerr << "can't open target file!" << std::endl;
        exit(1);
    }

    std::cout << "loading targets..." << std::endl;

    std::vector<NodeID> result;
    std::vector<std::pair<std::string, u32_t>> targets;

    std::string csvLine;
    while (getline(inFile, csvLine)) {
        std::string token, func;
        uint32_t line;

        std::istringstream iss(csvLine);
        getline(iss, token, delimiter);
        // Skip first value (tool)
        getline(iss, token, delimiter);
        func = token;
        getline(iss, token, delimiter);
        line = stoi(token);

        targets.emplace_back(func, line);
    }

    // Iterate over all basic blocks and located the target NodeIDs
    for (auto fun : *svfModule) {
        Function *F = fun->getLLVMFun();
        std::string file_name;

        if (llvm::DISubprogram *SP = F->getSubprogram()) {
            if (SP->describes(F)) {
                file_name = (SP->getFilename()).str();
            }
        }

        bool flag = false;
        for (const auto &target : targets) {
            auto idx = file_name.find(target.first);
            if (idx != string::npos) {
                flag = true;
                break;
            }
        }

        if (!flag) {
            continue;
        }

        for (auto &bit : *fun->getLLVMFun()) {
            BasicBlock *bb = &bit;
            std::string tmp_string = getDebugInfo(bb);
            for (auto &it : *bb) {
                uint32_t line_num = 0;
                Instruction *inst = &it;
                std::string str = SVFUtil::getSourceLoc(inst);
                // if (str != "{  }" && str.find("ln: 0  cl: 0") == str.npos) {

                if (SVFUtil::isa<AllocaInst>(inst)) {
                    for (llvm::DbgInfoIntrinsic *DII : FindDbgAddrUses(const_cast<Instruction *>(inst))) {
                        if (auto *DDI = SVFUtil::dyn_cast<llvm::DbgDeclareInst>(DII)) {
                            auto *DIVar = SVFUtil::cast<llvm::DIVariable>(DDI->getVariable());
                            line_num = DIVar->getLine();
                        }
                    }
                } else if (MDNode *N = inst->getMetadata("dbg")) {
                    auto *Loc = SVFUtil::cast<llvm::DILocation>(N);
                    line_num = Loc->getLine();
                }

                // If the line number matches that in targets then add to the result set
                for (const auto &target : targets) {
                    auto idx = file_name.find(target.first);
                    if (idx != string::npos && (idx == 0 || file_name[idx - 1] == '/')) {
                        if (target.second == line_num) {
                            result.push_back(icfg->getBlockICFGNode(inst)->getId());
                        }
                    }
                }
            }
        }
    }
    inFile.close();
    return result;
}

int main(int argc, char **argv) {
    int arg_num = 0;
    char **arg_value = new char *[argc];
    std::vector<std::string> moduleNameVec;
    SVFUtil::processArguments(argc, argv, arg_num, arg_value, moduleNameVec);
    cl::ParseCommandLineOptions(arg_num, arg_value, "analyze the vinilla distance of bb\n");

    svfModule = LLVMModuleSet::getLLVMModuleSet()->buildSVFModule(moduleNameVec);

    icfg = new ICFG();
    ICFGBuilder builder(icfg);
    builder.build(svfModule);

    M = LLVMModuleSet::getLLVMModuleSet()->getMainLLVMModule();
    C = &(LLVMModuleSet::getLLVMModuleSet()->getContext());

    std::vector<NodeID> target_ids = loadTargets(TargetsFile);
    std::cout << "caculate vanilla distance..." << std::endl;
    countVanillaDistance(target_ids);
    std::cout << "identiy critical bb..." << std::endl;
    identifyCriticalBB();
    std::cout << "instrument distance..." << std::endl;
    instrument();
    std::cout << "analyze condition..." << std::endl;
    analyzeCondition();
    std::cout << "instrument condition..." << std::endl;
    instrumentCondition();

    LLVMModuleSet::getLLVMModuleSet()->dumpModulesToFile(".ci.bc");

    delete icfg;

    return 0;
}