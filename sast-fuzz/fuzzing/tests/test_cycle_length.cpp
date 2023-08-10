#include <gtest/gtest.h>

extern "C" {
#include <sfz/cycle_length.h>

uint64_t init_cycle_length;
uint64_t cycle_length;
}

class CycleLengthTestSuite : public ::testing::Test {
  protected:
    void SetUp() override {
        init_cycle_length = 100;
        cycle_length = init_cycle_length;
    }
};

TEST_F(CycleLengthTestSuite, UpdateCycleLengthFix) {
    // Arrange + Act
    update_cycle_length_fix();

    // Assert
    ASSERT_EQ(cycle_length, init_cycle_length);
}

TEST_F(CycleLengthTestSuite, UpdateCycleLengthLin) {
    // Arrange
    uint32_t inc = 50;

    // Act
    update_cycle_length_lin(inc);

    // Assert
    EXPECT_EQ(cycle_length, init_cycle_length + inc);
}

TEST_F(CycleLengthTestSuite, UpdateCycleLengthLog) {
    // Arrange
    uint32_t dur = 120;

    // Act
    update_cycle_length_log(dur);

    // Assert
    ASSERT_GT(cycle_length, init_cycle_length);
}
