#include <math.h>
#include <stdio.h>

#include "../include/edunova_academic_average.h"

int main(void) {
    const double averages[] = {14.0, 12.0, 16.0};
    const double coefficients[] = {4.0, 3.0, 5.0};
    double result = -1.0;

    const int status = edunova_weighted_average(averages, coefficients, 3, &result);
    if (status != 0) {
        fprintf(stderr, "unexpected status: %d\n", status);
        return 1;
    }
    if (fabs(result - 14.333333333333334) > 1e-12) {
        fprintf(stderr, "unexpected result: %.17g\n", result);
        return 2;
    }

    result = 123.0;
    const double invalid_averages[] = {21.0};
    const double invalid_coefficients[] = {1.0};
    const int invalid_status = edunova_weighted_average(
        invalid_averages, invalid_coefficients, 1, &result
    );
    if (invalid_status != 2 || result != 123.0) {
        fprintf(stderr, "invalid input was not rejected safely\n");
        return 3;
    }

    puts("C ABI smoke test passed");
    return 0;
}
