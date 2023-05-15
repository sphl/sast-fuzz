// SPDX-FileCopyrightText: 2023 Stephan Lipp, Technical University of Munich (TUM), et al.
// SPDX-License-Identifier: Apache-2.0
#include <filesystem>
#include <map>
#include <set>

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

    template <typename Container, typename T> bool contains(const Container &container, const T &element) {
        return std::find(container.begin(), container.end(), element) != container.end();
    }

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

TEST_F(LLVMUtilsTestSuite, GetFunctionLineRange) {
    // Arrange
    std::map<std::string, std::map<std::string, std::set<LineNumber>>> expected = {
            {"swap", {{"start", {6, 7}}, {"end", {9, 10}}}},
            {"partition", {{"start", {13, 14, 15}}, {"end", {37, 38}}}},
            {"quickSort", {{"start", {40, 41}}, {"end", {51, 52, 53}}}},
            {"printArray", {{"start", {56, 57}}, {"end", {60, 61}}}},
            {"main", {{"start", {64, 65}}, {"end", {76, 77}}}},
    };

    for (auto &func : *llvmModule) {
        std::string funcName = func.getName().str();

        // Act
        auto actual = llvm_utils::getFunctionLineRange(func);

        // Assert
        ASSERT_TRUE(actual.has_value());

        ASSERT_TRUE(contains(expected[funcName]["start"], actual.value().first));
        ASSERT_TRUE(contains(expected[funcName]["end"], actual.value().second));
    }
}