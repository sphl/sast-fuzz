#include <llvm/IR/LLVMContext.h>
#include <llvm/IR/Module.h>
#include <llvm/IRReader/IRReader.h>
#include <llvm/Support/SourceMgr.h>

#include <gtest/gtest.h>

#include <sfi/llvm_utils.h>
#include <sfi/types.h>

using namespace testing;
using namespace llvm;
using namespace sfi;

class LLVMUtilsTestSuite : public Test {
  protected:
    std::unique_ptr<Module> llvmModule;
    std::string bitcodeFile = "./artifacts/llvm_bc/quicksort.bc";

    void SetUp() override {
        LLVMContext ctx;
        SMDiagnostic error;

        llvmModule = parseIRFile(bitcodeFile, error, ctx);

        if (llvmModule == nullptr) {
            error.print("LLVMUtilsTestSuite", errs());
            FAIL();
        }
    }

    void TearDown() override { llvmModule.release(); }
};

TEST_F(LLVMUtilsTestSuite, SetGetBBIdTest) {
    // Arrange
    BBId bbId = 42;

    for (auto &func : *llvmModule) {
        for (auto &bb : func) {
            // Act
            llvm_utils::setBBId(bb, bbId);

            auto ret = llvm_utils::getBBId(bb);

            // Assert
            ASSERT_TRUE(ret.has_value());
            ASSERT_EQ(ret.value(), bbId);
        }
    }
}