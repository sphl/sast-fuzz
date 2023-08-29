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

TEST_F(CycleLengthTestSuite, UpdateCycleLengthLin) {
    // Arrange
    u32 increase = 50;

    // Act
    cycle_interval = lin_cycle_interval(init_cycle_interval, increase);

    // Assert
    EXPECT_EQ(cycle_interval, init_cycle_interval + increase);
}

TEST_F(CycleLengthTestSuite, UpdateCycleLengthLog) {
    // Arrange
    u32 duration = 120;

    // Act
    cycle_interval = log_cycle_interval(init_cycle_interval, duration);

    // Assert
    ASSERT_GT(cycle_interval, init_cycle_interval);
}
