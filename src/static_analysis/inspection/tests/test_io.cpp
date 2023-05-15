// SPDX-FileCopyrightText: 2023 Stephan Lipp, Technical University of Munich (TUM), et al.
// SPDX-License-Identifier: Apache-2.0
#include <gmock/gmock.h>

#include <filesystem>
#include <fstream>

#include <gtest/gtest.h>

#include <sfi/io.h>

using namespace testing;
using namespace sfi;

namespace fs = std::filesystem;

class IOTestSuite : public Test {
  protected:
    fs::path tempFile;

    void SetUp() override {
        tempFile = fs::temp_directory_path() / "test.txt";
        if (fs::exists(tempFile)) {
            fs::remove(tempFile);
        }
    }

    void TearDown() override {
        if (fs::exists(tempFile)) {
            fs::remove(tempFile);
        }
    }
};

TEST_F(IOTestSuite, ReadyEmptyFile) {
    std::ofstream ofs(tempFile);
    ofs.close();
    auto actual = io::readFile(tempFile);
    ASSERT_TRUE(actual.empty());
}

TEST_F(IOTestSuite, WriteAndRead) {
    io::writeFile(tempFile, "foo");
    ASSERT_TRUE(fs::exists(tempFile));
    auto actual = io::readFile(tempFile);
    ASSERT_EQ(actual, "foo");
}