#ifndef SFZ_TARGET_BB_H
#define SFZ_TARGET_BB_H

#include <stdbool.h>
#include <types.h>

enum tbb_status { finished = 0, active = 1, paused = 2 };

typedef enum tbb_status tbb_status_t;

enum tbb_fuzzing_mode { directed = 0, cov_based = 1 };

typedef enum tbb_fuzzing_mode tbb_fuzzing_mode_t;

struct tbb_info {
    tbb_status_t status;
    float vuln_score;
    bool cov_flag;
    uint64_t n_input_execs;
    uint32_t n_cycle_skips;
    uint32_t n_prev_cycle_skips;
};

typedef struct tbb_info tbb_info_t;

extern tbb_info_t *tbb_info_init(float vuln_score);

extern void tbb_info_free(tbb_info_t *info);

extern tbb_fuzzing_mode_t tbb_update_status(tbb_info_t **tbb_infos,
                                            uint32_t n_tbbs_all,
                                            uint64_t cycle_length,
                                            float hc_reduct_factor,
                                            float vuln_score_thres);

#endif  // SFZ_TARGET_BB_H
