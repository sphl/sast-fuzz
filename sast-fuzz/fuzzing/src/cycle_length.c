#include <math.h>

#include <sfz/cycle_length.h>

void update_cycle_length_fix() { cycle_length = init_cycle_length; }

void update_cycle_length_lin(uint32_t inc) { cycle_length = (cycle_length + inc); }

void update_cycle_length_log(uint32_t dur) {
    cycle_length = (uint64_t)(log2f(((float)dur / 60) + 1) * 1000) + init_cycle_length;
}