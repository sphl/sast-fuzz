#ifndef SFZ_DISTANCE_MATRIX_H
#define SFZ_DISTANCE_MATRIX_H

#include <types.h>

extern uint32_t **dm_create_from_file(const char *filename, uint32_t *n_rows, uint32_t *n_cols);

extern void dm_free(uint32_t **matrix, uint32_t n_rows);

#endif  // SFZ_DISTANCE_MATRIX_H
