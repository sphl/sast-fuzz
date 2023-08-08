#ifndef SFZ_CYCLE_LENGTH_H
#define SFZ_CYCLE_LENGTH_H

#include <types.h>

extern uint64_t init_cycle_length;
extern uint64_t cycle_length;

extern void update_cycle_length_fix();

extern void update_cycle_length_lin(uint32_t inc);

extern void update_cycle_length_log(uint32_t dur);

#endif  // SFZ_CYCLE_LENGTH_H
