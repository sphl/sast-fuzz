#ifndef SFZ_CYCLE_LENGTH_H
#define SFZ_CYCLE_LENGTH_H

#include <types.h>

/**
 * Get linear cycle interval increase.
 *
 * @param init_interval Initial cycle interval
 * @param increase Seconds
 */
extern u32 lin_cycle_interval(u32 init_interval, u32 increase);

/**
 * Get logarithmic (log2) cycle interval increase.
 *
 * @param init_interval Initial cycle interval
 * @param duration Seconds in the campaign.
 */
extern u32 log_cycle_interval(u32 init_interval, u32 duration);

#endif  // SFZ_CYCLE_LENGTH_H
