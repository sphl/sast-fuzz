#include <alloc-inl.h>
#include <math.h>

#include <sfz/target_bb.h>

tbb_info_t *tbb_info_init(float vuln_score) {
    tbb_info_t *info = ck_alloc(sizeof(tbb_info_t));

    info->state = active;
    info->vuln_score = vuln_score;
    info->cov_flag = false;

    info->n_input_execs = 0;
    info->n_cycle_skips = 0;
    info->n_prev_cycle_skips = 1;

    return info;
}

void tbb_info_free(tbb_info_t *info) { ck_free(info); }