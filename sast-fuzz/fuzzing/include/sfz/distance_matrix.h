#ifndef SFZ_DISTANCE_MATRIX_H
#define SFZ_DISTANCE_MATRIX_H

#include <types.h>

/**
 * Create the distance matrix from a file.
 *
 * @param filename Path of the file.
 * @param n_rows Number of matrix rows.
 * @param n_cols Number of matrix columns.
 * @return Pointer to distance matrix (2D array).
 */
extern uint32_t **dm_create_from_file(const char *filename, uint32_t *n_rows, uint32_t *n_cols);

/**
 * Free a distance matrix.
 *
 * @param matrix Pointer to distance matrix.
 * @param n_rows Number of matrix rows.
 */
extern void dm_free(uint32_t **matrix, uint32_t n_rows);

#endif  // SFZ_DISTANCE_MATRIX_H
