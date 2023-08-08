#ifndef SFZ_TARGET_BB_H
#define SFZ_TARGET_BB_H

#include <stdbool.h>
#include <types.h>

enum tbb_state { finished = 0, active = 1, paused = 2 };

struct tbb_info {
    enum tbb_state state;
    float vuln_score;
    bool cov_flag;
    uint64_t n_input_execs;
    uint32_t n_cycle_skips;
    uint32_t n_prev_cycle_skips;
};

typedef struct tbb_info tbb_info_t;

extern tbb_info_t *tbb_info_create(float vuln_score);

extern void tbb_info_free(tbb_info_t *info);

#endif  // SFZ_TARGET_BB_H
