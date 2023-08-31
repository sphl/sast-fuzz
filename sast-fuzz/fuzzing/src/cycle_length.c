#include <math.h>

#include <sfz/cycle_length.h>

u32 lin_cycle_interval(u32 init_interval, u32 increase) { return (init_interval + increase); }

u32 log_cycle_interval(u32 init_interval, u32 duration) {
    return (init_interval + (u32)(log2f(((float)duration / 3600.0f) + 1.0f) * 150.0f));
}