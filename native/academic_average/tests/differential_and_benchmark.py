"""Differential checks and non-gating benchmarks for the Rust C ABI."""
import ctypes
import math
import random
import sys
import time
from pathlib import Path
from collections.abc import Callable

library = ctypes.CDLL(str(Path(sys.argv[1])))
function = library.edunova_weighted_average
pointer = ctypes.POINTER(ctypes.c_double)
function.argtypes = [pointer, pointer, ctypes.c_size_t, pointer]
function.restype = ctypes.c_int


def reference(a: list[float], c: list[float]) -> float:
    try:
        total = math.fsum(c)
        weighted = math.fsum(x * y for x, y in zip(a, c))
        result = weighted / total
        if all(map(math.isfinite, (total, weighted, result))):
            return result
    except OverflowError:
        pass
    scale = max(c)
    weights = [x / scale for x in c]
    return math.fsum(x * y for x, y in zip(a, weights)) / math.fsum(weights)


def native(a: list[float], c: list[float]) -> float:
    aa, cc = (ctypes.c_double * len(a))(*a), (ctypes.c_double * len(c))(*c)
    output = ctypes.c_double(-999.0)
    status = function(aa, cc, len(a), ctypes.byref(output))
    if status:
        raise AssertionError(f"native status={status}")
    return output.value


def main() -> None:
    rng = random.Random(20261102)
    cases = [
        ([14.0, 12.0, 16.0], [4.0, 3.0, 5.0]),
        ([10.0, 20.0], [sys.float_info.max, sys.float_info.max]),
        ([0.0, 20.0, 10.0], [1e-300, 1.0, 1e-200]),
        ([0.0, 20.0], [1.0, 1e-16]),
        ([20.0, 0.0], [1.0, 1.0]),
    ]
    for _ in range(1000):
        n = rng.randint(1, 100)
        cases.append((
            [rng.uniform(0.0, 20.0) for _ in range(n)],
            [10.0 ** rng.uniform(-250.0, 250.0) for _ in range(n)],
        ))
    for i, (a, c) in enumerate(cases):
        expected, actual = reference(a, c), native(a, c)
        if not math.isclose(actual, expected, rel_tol=1e-12, abs_tol=1e-12):
            raise AssertionError(f"case {i}: native={actual:.17g}, Python={expected:.17g}")
    print(f"Differential parity passed: {len(cases)} cases")

    print("Non-gating benchmark: median of 5 runs, microseconds/call")
    print("subjects | Python math.fsum | Rust C ABI")
    for n in (10, 100, 1000, 10000):
        a = [rng.uniform(0.0, 20.0) for _ in range(n)]
        c = [float(rng.randint(1, 8)) for _ in range(n)]
        aa, cc = (ctypes.c_double * n)(*a), (ctypes.c_double * n)(*c)
        out = ctypes.c_double()

        def py_call() -> None:
            math.fsum(x * y for x, y in zip(a, c)) / math.fsum(c)

        def rust_call() -> None:
            status = function(aa, cc, n, ctypes.byref(out))
            if status:
                raise RuntimeError(status)

        def measure(call: Callable[[], None]) -> float:
            samples = []
            for _ in range(5):
                start = time.perf_counter()
                for _ in range(100):
                    call()
                samples.append((time.perf_counter() - start) / 100 * 1e6)
            return sorted(samples)[2]

        print(f"{n:8d} | {measure(py_call):16.2f} | {measure(rust_call):10.2f}")


if __name__ == "__main__":
    main()
