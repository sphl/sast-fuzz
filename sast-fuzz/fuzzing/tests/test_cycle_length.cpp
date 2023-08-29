#include <gtest/gtest.h>

extern "C" {
#include <sfz/cycle_length.h>

u64 init_cycle_interval;
u64 cycle_interval;
}

class CycleLengthTestSuite : public ::testing::Test {
  protected:
    void SetUp() override {
        init_cycle_interval = 100;
        cycle_interval = init_cycle_interval;
    }
};

TEST_F(CycleLengthTestSuite, UpdateCycleLengthFix) {
    // Arrange + Act
    update_cycle_interval_fix();

    // Assert
    ASSERT_EQ(cycle_interval, init_cycle_interval);
}

TEST_F(CycleLengthTestSuite, UpdateCycleLengthLin) {
    // Arrange
    u32 inc = 50;

    // Act
    update_cycle_interval_lin(inc);

    // Assert
    EXPECT_EQ(cycle_interval, init_cycle_interval + inc);
}

TEST_F(CycleLengthTestSuite, UpdateCycleLengthLog) {
    // Arrange
    u32 dur = 120;

    // Act
    update_cycle_interval_log(dur);

    // Assert
    ASSERT_GT(cycle_interval, init_cycle_interval);
}
