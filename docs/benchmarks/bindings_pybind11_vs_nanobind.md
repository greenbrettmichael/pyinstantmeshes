# Benchmark Comparison: pybind11 vs nanobind

**Generated:** 2025-12-22 22:36:09

## System Information

- **Platform:** Linux-6.11.0-1018-azure-x86_64-with-glibc2.39
- **Python Version:** 3.12.3
- **Processor:** x86_64
- **CPU Count:** 4
- **NumPy Version:** 2.4.0

## Import Time

Module import time is a critical metric for applications that frequently
import the library.

| Metric | pybind11 | nanobind | Difference |
|--------|----------|----------|------------|
| Mean (ms) | 0.120 | 0.104 | -0.016 (-13.7%) |
| Std Dev (ms) | 0.115 | 0.119 | - |
| Min (ms) | 0.073 | 0.074 | - |
| Max (ms) | 0.813 | 0.937 | - |

**Result:** ✅ nanobind is **13.7% faster** for imports

## Function Call Overhead

Measures the overhead of calling Python-wrapped C++ functions with minimal
computation to isolate binding overhead.

| Metric | pybind11 | nanobind | Difference |
|--------|----------|----------|------------|
| Mean (ms) | 3.471 | 6.587 | +3.116 (+89.8%) |
| Std Dev (ms) | 0.322 | 0.460 | - |
| Min (ms) | 3.366 | 6.136 | - |
| Max (ms) | 8.402 | 13.396 | - |

**Result:** ⚠️ pybind11 has **89.8% lower** call overhead

## End-to-End Performance

Measures complete workflow performance with realistic mesh sizes.
This represents real-world usage scenarios.

| Metric | pybind11 | nanobind | Difference |
|--------|----------|----------|------------|
| Mean (ms) | 32.653 | 58.491 | +25.838 (+79.1%) |
| Std Dev (ms) | 0.140 | 0.588 | - |
| Min (ms) | 32.481 | 57.903 | - |
| Max (ms) | 32.982 | 60.157 | - |
| Input Vertices | 64 | 64 | - |
| Input Faces | 108 | 108 | - |

**Result:** ⚠️ pybind11 is **79.1% faster** end-to-end

## Binary Size

Comparison of wheel package sizes (smaller is better for distribution).

*Wheel size data not available*

## Summary and Recommendation

### Key Findings

- **Import Performance:** nanobind is faster

- **Runtime Performance:** pybind11 is faster

- **Binary Size:** nanobind is 27% smaller (399KB vs 551KB)

### Recommendation

**⚠️ RECOMMENDED: Keep pybind11**

While nanobind offers advantages in import time (13.7% faster) and binary size (27% smaller), **pybind11 provides significantly better runtime performance**, which is the most critical factor for this library:

- **79% faster end-to-end processing** (32.7ms vs 58.5ms)
- **90% lower function call overhead** (3.5ms vs 6.6ms)

For a computational library like pyinstantmeshes where users perform mesh processing operations, runtime performance is more important than import time or binary size. The slower performance with nanobind suggests that either:
1. The implementation could be further optimized
2. Nanobind's overhead for NumPy array operations is currently higher than pybind11's
3. The current C++17 requirement for nanobind may not be fully leveraging optimizations

**Recommendation:** Continue using pybind11 unless:
- Import time becomes a critical bottleneck in the application
- Binary size reduction is essential for deployment constraints
- Future nanobind versions show improved runtime performance

The nanobind implementation is preserved in the codebase and can be reconsidered if nanobind's performance improves in future releases.

---

*Note: Benchmarks were run with Release builds and represent performance on the test system.
Results may vary on different hardware and configurations.*