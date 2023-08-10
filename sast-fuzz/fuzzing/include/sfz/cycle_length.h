#ifndef SFZ_CYCLE_LENGTH_H
#define SFZ_CYCLE_LENGTH_H

#include <types.h>

extern uint64_t init_cycle_length;
extern uint64_t cycle_length;

/**
 * Constant cycle length.
 */
extern void update_cycle_length_fix();

/**
 * Update cycle length linearly.
 *
 * @param inc Number of fuzz inputs.
 */
extern void update_cycle_length_lin(uint32_t inc);

/**
 * Update cycle length logarithmically (log2)
 *
 * @param dur Number of minutes spent in the campaign.
 */
extern void update_cycle_length_log(uint32_t dur);

#endif  // SFZ_CYCLE_LENGTH_H
