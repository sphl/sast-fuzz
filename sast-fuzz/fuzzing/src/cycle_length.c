#include <math.h>

#include <sfz/cycle_length.h>

void update_cycle_length_fix() { cycle_length = init_cycle_length; }

void update_cycle_length_lin(u32 inc) { cycle_length = (cycle_length + inc); }

void update_cycle_length_log(u32 dur) { cycle_length = (u64)(log2f(((float)dur / 60) + 1) * 1000) + init_cycle_length; }