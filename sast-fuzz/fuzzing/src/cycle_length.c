#include <math.h>

#include <sfz/cycle_length.h>

void update_cycle_interval_fix() { cycle_interval = init_cycle_interval; }

void update_cycle_interval_lin(u32 inc) { cycle_interval = (cycle_interval + inc); }

void update_cycle_interval_log(u32 dur) {
    cycle_interval = (u64)(log2f(((float)dur / 3600.0f) + 1.0f) * 300.0f) + init_cycle_interval;
}