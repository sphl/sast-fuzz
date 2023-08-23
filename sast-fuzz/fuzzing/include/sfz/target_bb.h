#ifndef SFZ_TARGET_BB_H
#define SFZ_TARGET_BB_H

#include <stdbool.h>
#include <types.h>

enum tbb_state { finished = 0, active = 1, paused = 2 };

struct tbb_info {
    enum tbb_state state;    //< Current state of the target BB.
    float vuln_score;        //< Vulnerability score of the target BB.
    bool cov_flag;           //< Flag if target BB was covered in the current cycle.
    u64 n_input_execs;       //< Number of target BB executions (i.e., # inputs).
    u64 n_cycle_skips;       //< Number of current cycle skips.
    u64 n_prev_cycle_skips;  //< Number of previous cycle skips.
};

typedef struct tbb_info tbb_info_t;

/**
 * Create a new target BB info object.
 *
 * @param vuln_score Vulnerability score of the target BB.
 * @return
 */
extern tbb_info_t *tbb_info_create(float vuln_score);

/**
 * Free a target BB info object.
 *
 * @param info
 */
extern void tbb_info_free(tbb_info_t *info);

#endif  // SFZ_TARGET_BB_H
