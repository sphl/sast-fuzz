#include <alloc-inl.h>
#include <math.h>

#include <sfz/target_bb.h>

tbb_info_t *tbb_info_init(float vuln_score) {
    tbb_info_t *info = ck_alloc(sizeof(tbb_info_t));

    info->status = active;
    info->vuln_score = vuln_score;
    info->cov_flag = false;

    info->n_input_execs = 0;
    info->n_cycle_skips = 0;
    info->n_prev_cycle_skips = 1;

    return info;
}

void tbb_info_free(tbb_info_t *info) { ck_free(info); }

tbb_fuzzing_mode_t tbb_update_status(tbb_info_t **tbb_infos,
                                     uint32_t n_tbbs_all,
                                     uint64_t cycle_length,
                                     float hc_reduct_factor,
                                     float vuln_score_thres) {
    tbb_fuzzing_mode_t mode = directed;

    float sum_vuln_score = 0.0f;

    for (int i = 0; i < n_tbbs_all; i++) {
        if (tbb_infos[i]->status == active || tbb_infos[i]->status == paused) {
            sum_vuln_score += tbb_infos[i]->vuln_score;
        }
    }

    uint32_t n_tbbs_paused = 0;
    uint32_t n_tbbs_finished = 0;

    for (int i = 0; i < n_tbbs_all; i++) {
        if (tbb_infos[i]->status == active || tbb_infos[i]->status == paused) {

            int64_t n_req_input_execs =
                    (int64_t)roundf((float)cycle_length * (tbb_infos[i]->vuln_score / sum_vuln_score));

            if (hc_reduct_factor == 1.0f) {
                n_req_input_execs = 1;
            } else {
                n_req_input_execs -= (int64_t)((float)n_req_input_execs * hc_reduct_factor);
            }

            int64_t exec_diff = (n_req_input_execs - (int64_t)tbb_infos[i]->n_input_execs);

            if (exec_diff <= 0) {

                // We do not care if the target BB is activated or paused. When it has been executed frequently enough
                // by the generated fuzzy inputs, we mark it as finished
                tbb_infos[i]->status = finished;

            } else {

                if (tbb_infos[i]->cov_flag) {

                    // Each executed target BB will automatically be activated in the next cycle, regardless if paused
                    // or already activated
                    tbb_infos[i]->status = active;
                    tbb_infos[i]->n_cycle_skips = 0;
                    tbb_infos[i]->n_prev_cycle_skips = 1;

                } else {

                    if (tbb_infos[i]->n_cycle_skips == 0) {

                        tbb_infos[i]->status = paused;
                        tbb_infos[i]->n_cycle_skips = tbb_infos[i]->n_prev_cycle_skips;
                        tbb_infos[i]->n_prev_cycle_skips++;

                    } else {

                        // Reactivate target BB if it has been "sufficiently" paused
                        if ((tbb_infos[i]->n_cycle_skips - 1) == 0) {
                            tbb_infos[i]->status = active;
                            tbb_infos[i]->n_cycle_skips = 0;
                        } else {
                            tbb_infos[i]->n_cycle_skips--;
                        }
                    }
                }
            }

#ifdef SFZ_DEBUG
            char status_str[128];

            if (tbb_infos[i]->status == finished) {
                sprintf(status_str, "x");
            } else {
                if (tbb_infos[i]->status == active) {
                    sprintf(status_str, "...");
                } else {
                    sprintf(status_str, "p (%d|%d)", tbb_infos[i]->n_cycle_skips, tbb_infos[i]->n_prev_cycle_skips);
                }
            }

            printf("sast-fuzz: target BB = %d (%.2f), required = %ld (%.1f), actual = %lu (%ld) %s\n", i,
                   tbb_infos[i]->vuln_score, n_req_input_execs, hc_reduct_factor, tbb_infos[i]->n_input_execs,
                   exec_diff, status_str);
#endif

            tbb_infos[i]->cov_flag = false;
        }

        if (tbb_infos[i]->status == paused) {
            n_tbbs_paused++;
        }

        if (tbb_infos[i]->status == finished) {
            n_tbbs_finished++;
        }
    }

#ifdef SFZ_DEBUG
    printf("sast-fuzz: target BBs finished = %d, active = %d, paused = %d\n", n_tbbs_finished,
           (n_tbbs_all - (n_tbbs_finished + n_tbbs_paused)), n_tbbs_paused);
#endif

    if (n_tbbs_finished == n_tbbs_all) {

        // All target BBs have been finished, so focus on those with a vuln. score of at least X
        for (int i = 0; i < n_tbbs_all; i++) {

            if (tbb_infos[i]->vuln_score >= vuln_score_thres) {
                // Reset target BB infos
                tbb_infos[i]->status = active;
                tbb_infos[i]->cov_flag = false;
                tbb_infos[i]->n_input_execs = 0;
                tbb_infos[i]->n_cycle_skips = 0;
                tbb_infos[i]->n_prev_cycle_skips = 1;
            }
        }
    } else {

        if ((n_tbbs_finished + n_tbbs_paused) == n_tbbs_all) {
            // Seems like we are stuck right now — go into "coverage mode" trying to discover new code regions
            mode = cov_based;
        }
    }

    return mode;
}