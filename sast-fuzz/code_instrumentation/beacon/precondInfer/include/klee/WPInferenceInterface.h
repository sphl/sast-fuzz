#ifndef WP_INFERENCE_INTERFACE_H
#define WP_INFERENCE_INTERFACE_H

#include "llvm/IR/Module.h"
#include "llvm/IR/Instruction.h"
#include "llvm/ADT/APInt.h"
#include <vector>
#include <set>
#include <unordered_map>
namespace BackwardAI {
  class WPInferenceInterface {
  public:
    struct FunctionResult {
      std::unordered_map<const llvm::Value*, std::vector<std::pair<llvm::APInt, llvm::APInt>>> argResult;
      std::unordered_map<const llvm::Instruction*, std::vector<std::pair<llvm::APInt, llvm::APInt>>> valResult;
      std::unordered_map<const llvm::Instruction *, std::pair<std::set<unsigned>, std::set<unsigned> > > synergyResult;
      std::set<const llvm::BasicBlock *> conditionedBBs;
      std::set<const llvm::BasicBlock *> unreachableBBs;

      FunctionResult(decltype(argResult) argRes, decltype(valResult) valRes, decltype(synergyResult) synergyRes,
                     decltype(conditionedBBs) condbbs, decltype(unreachableBBs) unreachbbs) :
                     argResult(std::move(argRes)), valResult(std::move(valRes)), synergyResult(std::move(synergyRes)),
                     conditionedBBs(std::move(condbbs)), unreachableBBs(std::move(unreachbbs)) {}

      FunctionResult() {}
    };

    WPInferenceInterface(llvm::Module *M, bool isInterProc);
    void setTargets(std::set<const llvm::Instruction*> targets);

    ~WPInferenceInterface();
    void run(bool useSolver);
    void dumpResult();
    void dumpSynergy();


    /// The analysis result is grouped by functions.
    /// Res[f] = funres:FunctionResult
    /// funres.argResult: arg -> range
    ///   -- arg must be inside function f.
    /// funres.valResult: loc -> rng
    ///   -- loc must be inside function f.
    std::unordered_map<const llvm::Function*, FunctionResult> getResult();

    void dumpReachBBs(const std::set<const llvm::BasicBlock*> &);


  private:
    llvm::Module *M;
    std::set<const llvm::Instruction*> targets;
    bool isInterAnalysis;
    std::unordered_map<const llvm::Function*, FunctionResult> analysisResultByFun;
//    PreconditionFixpo infer;

    void runForTarget(const llvm::Instruction *, bool useSolver);
    unsigned getAsmLineAtInst (const llvm::Instruction *inst) const;
    void dumpTime();
    void dumpMem();

  };

  /// use WPInferenceInterface to perform analysis and persist result.
  /// use PersistenceAnalysisData to deserialize result.
  /// CANNOT be used at the same time.
  class PersistenceAnalysisData {
  public:
    static std::unordered_map<const llvm::Function*, WPInferenceInterface::FunctionResult>
      deserialize(const llvm::Module *, const std::string &resultJson);
  };
}
#endif