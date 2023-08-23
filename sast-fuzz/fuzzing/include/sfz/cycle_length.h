#ifndef SFZ_CYCLE_LENGTH_H
#define SFZ_CYCLE_LENGTH_H

#include <types.h>

extern u64 init_cycle_length;
extern u64 cycle_length;

/**
 * Constant cycle length.
 */
extern void update_cycle_length_fix();

/**
 * Update cycle length linearly.
 *
 * @param inc Number of fuzz inputs.
 */
extern void update_cycle_length_lin(u32 inc);

/**
 * Update cycle length logarithmically (log2)
 *
 * @param dur Number of minutes spent in the campaign.
 */
extern void update_cycle_length_log(u32 dur);

#endif  // SFZ_CYCLE_LENGTH_H
