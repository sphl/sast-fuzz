#include <gmock/gmock.h>

#include <filesystem>
#include <fstream>

#include <gtest/gtest.h>

#include <sfi/io.h>

using namespace testing;
using namespace sfi;

namespace fs = std::filesystem;

class IOUtilTestSuite : public Test {
  protected:
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

    fs::path tempFile;
};

TEST_F(IOUtilTestSuite, ReadyEmptyFile) {
    std::ofstream ofs(tempFile);
    ofs.close();
    auto actual = io::readFile(tempFile);
    ASSERT_TRUE(actual.empty());
}

TEST_F(IOUtilTestSuite, WriteAndRead) {
    io::writeFile("foo", tempFile);
    ASSERT_TRUE(fs::exists(tempFile));
    auto actual = io::readFile(tempFile);
    ASSERT_EQ(actual, "foo");
}