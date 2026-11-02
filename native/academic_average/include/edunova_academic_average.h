#ifndef EDUNOVA_ACADEMIC_AVERAGE_H
#define EDUNOVA_ACADEMIC_AVERAGE_H

#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

/*
 * Computes a weighted average on the 0..=20 scale.
 * Returns 0 on success, 1 for invalid pointer/length, 2 for invalid data.
 * On error, out_result is unchanged. The caller owns all memory.
 */
int edunova_weighted_average(
    const double *averages,
    const double *coefficients,
    size_t len,
    double *out_result
);

#ifdef __cplusplus
}
#endif

#endif
