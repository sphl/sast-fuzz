#include <filesystem>

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

namespace fs = std::filesystem;

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

TEST_F(LLVMUtilsTestSuite, GetFilenameTest) {
    // Arrange
    std::string expected = fs::path(bitcodeFile).filename();

    for (auto &func : *llvmModule) {
        // Act
        auto actual = llvm_utils::getFilename(func);

        // Assert
        ASSERT_EQ(expected, actual);
    }
}

TEST_F(LLVMUtilsTestSuite, SetGetBBIdTest) {
    // Arrange
    BBId expected = 42;

    for (auto &func : *llvmModule) {
        for (auto &bb : func) {
            // Act
            llvm_utils::setBBId(bb, expected);

            auto actual = llvm_utils::getBBId(bb);

            // Assert
            ASSERT_TRUE(actual.has_value());
            ASSERT_EQ(expected, actual.value());
        }
    }
}