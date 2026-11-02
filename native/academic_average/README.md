# EduNova academic average — native proof of concept

**Status: experimental; not used by the production application.**

This crate evaluates a pure weighted-average calculation in Rust and exposes a minimal C ABI so a C caller can exercise the same implementation.

## Scope

- Input: subject averages (0..=20) and positive finite coefficients.
- Output: weighted average as f64.
- No database, filesystem, network, tenant context, authorization, audit, or school-policy loading.
- Maximum input length: 1,000,000 entries.
- C ABI errors do not modify the output value.

## Build and test

From the repository root:

\`\`\`sh
cargo fmt --manifest-path native/academic_average/Cargo.toml -- --check
cargo test --manifest-path native/academic_average/Cargo.toml
cargo clippy --manifest-path native/academic_average/Cargo.toml --all-targets -- -D warnings
cargo build --manifest-path native/academic_average/Cargo.toml --release
cc -std=c11 -Wall -Wextra -Werror \\
  native/academic_average/tests/c_abi_smoke.c \\
  -L native/academic_average/target/release \\
  -ledunova_academic_average \\
  -Wl,-rpath,'$ORIGIN/../target/release' \\
  -o native/academic_average/target/c_abi_smoke
native/academic_average/target/c_abi_smoke
\`\`\`

The C ABI is deliberately small. Pointer validity and memory ownership remain obligations of the C caller. The exported function checks null pointers and bounds before creating Rust slices.

## Integration decision

Do not connect this library to FastAPI or replace the Python calculator until:
1. Python reference tests define required behavior, including rounding and edge cases.
2. Differential tests establish acceptable parity.
3. Benchmarks on realistic school workloads show a useful benefit or a concrete safety requirement justifies the native boundary.
4. Packaging and deployment are validated for every supported target platform.

The production Python service remains the source of truth during this experiment.
