#ifndef SFZ_CYCLE_LENGTH_H
#define SFZ_CYCLE_LENGTH_H

#include <types.h>

extern u64 init_cycle_interval;
extern u64 cycle_interval;

/**
 * Constant cycle interval.
 */
extern void update_cycle_interval_fix();

/**
 * Update cycle interval linearly.
 *
 * @param inc Number of fuzz inputs.
 */
extern void update_cycle_interval_lin(u32 inc);

/**
 * Update cycle interval logarithmically (log2)
 *
 * @param dur Number of minutes spent in the campaign.
 */
extern void update_cycle_interval_log(u32 dur);

#endif  // SFZ_CYCLE_LENGTH_H
