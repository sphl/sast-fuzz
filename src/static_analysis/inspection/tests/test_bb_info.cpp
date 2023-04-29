#include <gtest/gtest.h>

#include <sfi/bb_info.h>
#include <sfi/types.h>

using namespace testing;
using namespace sfi;

TEST(BBInfoTestSuite, ConstructorAndGettersTest) {
    // Arrange + Act
    BBId id = 42;
    Lines lineNumbers = {1, 2, 3};
    LineRange lineRange = {1, 3};
    BBInfo bbInfo(id, lineNumbers, lineRange);

    // Assert
    ASSERT_EQ(bbInfo.getId(), id);
    ASSERT_EQ(bbInfo.getLineNumbers(), lineNumbers);
    ASSERT_EQ(bbInfo.getLineRange(), lineRange);
}

TEST(BBInfoTestSuite, EqualityOperatorTest) {
    // Arrange + Act
    BBId id1 = 42;
    Lines lineNumbers1 = {1, 2, 3};
    LineRange lineRange1 = {1, 3};
    BBInfo bbInfo1(id1, lineNumbers1, lineRange1);

    BBId id2 = 42;
    Lines lineNumbers2 = {1, 2, 3};
    LineRange lineRange2 = {1, 3};
    BBInfo bbInfo2(id2, lineNumbers2, lineRange2);

    // Assert
    ASSERT_EQ(bbInfo1, bbInfo2);
}

TEST(BBInfoTestSuite, InequalityOperatorTest) {
    // Arrange + Act
    BBId id1 = 42;
    Lines lineNumbers1 = {1, 2, 3};
    LineRange lineRange1 = {1, 3};
    BBInfo bbInfo1(id1, lineNumbers1, lineRange1);

    BBId id2 = 43;
    Lines lineNumbers2 = {1, 2, 3};
    LineRange lineRange2 = {1, 3};
    BBInfo bbInfo2(id2, lineNumbers2, lineRange2);

    // Assert
    ASSERT_NE(bbInfo1, bbInfo2);
}

TEST(BBInfoTestSuite, LessThanOperatorTest) {
    // Arrange + Act
    BBId id1 = 42;
    Lines lineNumbers1 = {1, 2, 3};
    LineRange lineRange1 = {1, 3};
    BBInfo bbInfo1(id1, lineNumbers1, lineRange1);

    BBId id2 = 43;
    Lines lineNumbers2 = {1, 2, 3};
    LineRange lineRange2 = {1, 3};
    BBInfo bbInfo2(id2, lineNumbers2, lineRange2);

    // Assert
    ASSERT_LT(bbInfo1, bbInfo2);
}