#include <alloc-inl.h>

#include <sfz/distance_matrix.h>

uint32_t **dm_create_from_file(const char *filename, uint32_t *n_rows, uint32_t *n_cols) {
    FILE *file = fopen(filename, "r");
    if (file == NULL) {
        printf("ERROR: Could not open matrix file!\n");
        return 0;
    }

    // Read the first line to get the matrix dimensions
    fscanf(file, "%d:%d", n_rows, n_cols);

    // Allocate memory for the matrix
    uint32_t **matrix = ck_alloc(*n_rows * sizeof(uint32_t *));
    for (int i = 0; i < *n_rows; i++) {
        matrix[i] = ck_alloc(*n_cols * sizeof(uint32_t));
    }

    // Read the values from the file
    for (int i = 0; i < *n_rows; i++) {
        for (int j = 0; j < *n_cols; j++) {
            fscanf(file, "%d,", &matrix[i][j]);
        }
    }

    fclose(file);

    return matrix;
}

void dm_free(uint32_t **matrix, uint32_t n_rows) {
    for (int i = 0; i < n_rows; i++) {
        ck_free(matrix[i]);
    }
    ck_free(matrix);
}