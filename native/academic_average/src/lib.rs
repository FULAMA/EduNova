//! Experimental, pure weighted-average kernel.
//! No database, network, tenant, authorization, or persistence responsibilities.

use std::panic::{catch_unwind, AssertUnwindSafe};

const MAX_SUBJECTS: usize = 1_000_000;
const STATUS_OK: i32 = 0;
const STATUS_INVALID_ARGUMENT: i32 = 1;
const STATUS_INVALID_DATA: i32 = 2;

fn compensated_add(sum: &mut f64, compensation: &mut f64, value: f64) {
    let next = *sum + value;
    if sum.abs() >= value.abs() {
        *compensation += (*sum - next) + value;
    } else {
        *compensation += (value - next) + *sum;
    }
    *sum = next;
}

/// Computes a weighted average for academic averages on the 0..=20 scale.
pub fn weighted_average(averages: &[f64], coefficients: &[f64]) -> Result<f64, &'static str> {
    if averages.is_empty() || averages.len() != coefficients.len() {
        return Err("input arrays must have the same non-zero length");
    }
    if averages.len() > MAX_SUBJECTS {
        return Err("too many subjects");
    }

    let mut max_coefficient = 0.0_f64;
    for (&average, &coefficient) in averages.iter().zip(coefficients.iter()) {
        if !average.is_finite() || !(0.0..=20.0).contains(&average) {
            return Err("averages must be finite and between 0 and 20");
        }
        if !coefficient.is_finite() || coefficient <= 0.0 {
            return Err("coefficients must be finite and positive");
        }
        max_coefficient = max_coefficient.max(coefficient);
    }

    let mut weight_sum = 0.0;
    let mut weight_compensation = 0.0;
    let mut weighted_sum = 0.0;
    let mut weighted_compensation = 0.0;

    for (&average, &coefficient) in averages.iter().zip(coefficients.iter()) {
        let scaled_weight = coefficient / max_coefficient;
        compensated_add(&mut weight_sum, &mut weight_compensation, scaled_weight);
        compensated_add(
            &mut weighted_sum,
            &mut weighted_compensation,
            average * scaled_weight,
        );
    }

    let result = (weighted_sum + weighted_compensation)
        / (weight_sum + weight_compensation);

    if result.is_finite() && (0.0..=20.0).contains(&result) {
        Ok(result)
    } else {
        Err("calculation produced an invalid result")
    }
}

/// C ABI status: 0 success, 1 invalid pointer/length, 2 invalid data.
///
/// # Safety
/// The two input pointers must each reference len readable f64 values and
/// out_result must reference one writable f64 for the duration of this call.
#[no_mangle]
pub unsafe extern "C" fn edunova_weighted_average(
    averages: *const f64,
    coefficients: *const f64,
    len: usize,
    out_result: *mut f64,
) -> i32 {
    if averages.is_null()
        || coefficients.is_null()
        || out_result.is_null()
        || len == 0
        || len > MAX_SUBJECTS
    {
        return STATUS_INVALID_ARGUMENT;
    }

    let calculation = catch_unwind(AssertUnwindSafe(|| {
        // SAFETY: pointer validity and lengths are the caller's responsibility.
        let averages = unsafe { std::slice::from_raw_parts(averages, len) };
        // SAFETY: pointer validity and lengths are the caller's responsibility.
        let coefficients = unsafe { std::slice::from_raw_parts(coefficients, len) };
        weighted_average(averages, coefficients)
    }));

    match calculation {
        Ok(Ok(value)) => {
            // SAFETY: caller guarantees one writable f64 at out_result.
            unsafe { out_result.write(value) };
            STATUS_OK
        }
        Ok(Err(_)) | Err(_) => STATUS_INVALID_DATA,
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn calculates_weighted_average() {
        let result = weighted_average(&[14.0, 12.0, 16.0], &[4.0, 3.0, 5.0])
            .expect("valid input");
        assert!((result - 14.333333333333334).abs() < 1e-12);
    }

    #[test]
    fn one_subject_returns_its_average() {
        assert_eq!(weighted_average(&[15.0], &[4.0]), Ok(15.0));
    }

    #[test]
    fn scales_large_coefficients_without_overflow() {
        let result = weighted_average(&[10.0, 20.0], &[f64::MAX, f64::MAX])
            .expect("finite scaled calculation");
        assert!((result - 15.0).abs() < 1e-12);
    }

    #[test]
    fn rejects_empty_or_mismatched_inputs() {
        assert!(weighted_average(&[], &[]).is_err());
        assert!(weighted_average(&[10.0], &[1.0, 2.0]).is_err());
    }

    #[test]
    fn rejects_non_finite_and_out_of_range_averages() {
        assert!(weighted_average(&[f64::NAN], &[1.0]).is_err());
        assert!(weighted_average(&[f64::INFINITY], &[1.0]).is_err());
        assert!(weighted_average(&[20.1], &[1.0]).is_err());
        assert!(weighted_average(&[-0.1], &[1.0]).is_err());
    }

    #[test]
    fn rejects_non_positive_or_non_finite_coefficients() {
        assert!(weighted_average(&[10.0], &[0.0]).is_err());
        assert!(weighted_average(&[10.0], &[-1.0]).is_err());
        assert!(weighted_average(&[10.0], &[f64::INFINITY]).is_err());
    }

    #[test]
    fn compensated_sum_limits_loss_of_precision() {
        let result = weighted_average(&[20.0, 0.0, 20.0], &[1.0, 1e-16, 1.0])
            .expect("valid input");
        assert!((result - 20.0).abs() < 1e-12);
    }
}
