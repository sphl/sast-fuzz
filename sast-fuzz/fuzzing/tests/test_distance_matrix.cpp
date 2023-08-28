#include <gtest/gtest.h>

extern "C" {
#include <sfz/distance_matrix.h>
}

TEST(DMTestSuite, CompareWithGivenMatrix) {
    // Arrange
    u32 n_rows, n_cols;
    u32 expected[3][3] = {{1, 2, 3}, {4, 5, 6}, {7, 8, 9}};

    // Act
    int32_t **matrix = dm_create_from_file("data/matrix.txt", &n_rows, &n_cols);

    // Assert
    ASSERT_NE(matrix, nullptr);
    ASSERT_EQ(n_rows, 3);
    ASSERT_EQ(n_cols, 3);

    for (u32 i = 0; i < n_rows; i++) {
        for (u32 j = 0; j < n_cols; j++) {
            ASSERT_EQ(matrix[i][j], expected[i][j]);
        }
    }

    dm_free(matrix, n_rows);
}
