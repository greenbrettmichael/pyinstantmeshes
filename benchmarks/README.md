# Benchmark Suite

This directory contains benchmarks for comparing pybind11 and nanobind Python bindings.

## Files

- `benchmark_bindings.py` - Core benchmark implementation
- `run_comparison.py` - Automated script to build and benchmark both implementations
- `generate_report.py` - Generate markdown report from results
- `comparison_results.json` - Latest benchmark results (auto-generated)
- `pybind11_results.json` - pybind11-only results
- `nanobind_results.json` - nanobind-only results

## Running Benchmarks

### Quick Manual Run

To benchmark the currently installed version:

```bash
python benchmarks/benchmark_bindings.py
```

### Full Comparison

To automatically build both versions and compare:

```bash
python benchmarks/run_comparison.py
```

This will:
1. Build and test pybind11 version
2. Build and test nanobind version
3. Run comprehensive benchmarks on both
4. Generate comparison report

### Generate Report

To generate a markdown report from existing results:

```bash
python benchmarks/generate_report.py benchmarks/comparison_results.json
```

Report will be saved to `docs/benchmarks/bindings_pybind11_vs_nanobind.md`

## Benchmark Metrics

The suite measures:

1. **Import Time** - Module import overhead (50 iterations)
2. **Call Overhead** - Function call binding overhead (1000 iterations)
3. **End-to-End** - Real-world mesh processing time (10 iterations)
4. **Binary Size** - Compiled wheel size comparison

## Requirements

- Python 3.11+
- NumPy
- pybind11 >= 2.10.0 (for pybind11 build)
- nanobind >= 2.0.0 (for nanobind build)
- scikit-build-core
- CMake >= 3.15

## Results

See the full benchmark report: [`docs/benchmarks/bindings_pybind11_vs_nanobind.md`](../docs/benchmarks/bindings_pybind11_vs_nanobind.md)

## Notes

- All benchmarks use Release builds for fair comparison
- Results may vary across different hardware and Python versions
- The benchmark suite is deterministic where possible (using `deterministic=True` flag)
- Import time includes warm-up iterations to account for module caching
