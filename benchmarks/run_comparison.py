#!/usr/bin/env python3
"""
Script to build both pybind11 and nanobind versions and run comparative benchmarks.
"""

import os
import sys
import subprocess
import shutil
import json
from pathlib import Path


class ComparativeBenchmark:
    """Build and benchmark both binding implementations."""
    
    def __init__(self, repo_root):
        self.repo_root = Path(repo_root)
        self.benchmarks_dir = self.repo_root / "benchmarks"
        self.build_dir = self.repo_root / "build"
        self.results = {}
    
    def clean_build(self):
        """Clean previous build artifacts."""
        print("Cleaning previous build artifacts...")
        
        # Remove build directory
        if self.build_dir.exists():
            shutil.rmtree(self.build_dir)
        
        # Remove dist directory
        dist_dir = self.repo_root / "dist"
        if dist_dir.exists():
            shutil.rmtree(dist_dir)
        
        # Uninstall pyinstantmeshes if installed
        subprocess.run([sys.executable, "-m", "pip", "uninstall", "-y", "pyinstantmeshes"],
                      capture_output=True)
    
    def build_pybind11(self):
        """Build the pybind11 version."""
        print("\n" + "="*70)
        print("Building pybind11 version...")
        print("="*70)
        
        self.clean_build()
        
        # Copy pybind11 pyproject.toml
        shutil.copy(
            self.repo_root / "pyproject.toml.pybind11",
            self.repo_root / "pyproject.toml"
        )
        
        # Install dependencies
        subprocess.run([sys.executable, "-m", "pip", "install", "pybind11>=2.10.0"],
                      check=True)
        
        # Build and install
        subprocess.run([sys.executable, "-m", "pip", "install", "-e", ".", "-v"],
                      cwd=self.repo_root, check=True)
        
        print("✓ pybind11 version built successfully")
    
    def build_nanobind(self):
        """Build the nanobind version."""
        print("\n" + "="*70)
        print("Building nanobind version...")
        print("="*70)
        
        self.clean_build()
        
        # Copy nanobind pyproject.toml
        shutil.copy(
            self.repo_root / "pyproject.toml.nanobind",
            self.repo_root / "pyproject.toml"
        )
        
        # Install dependencies
        subprocess.run([sys.executable, "-m", "pip", "install", "nanobind>=2.0.0"],
                      check=True)
        
        # Build and install
        subprocess.run([sys.executable, "-m", "pip", "install", "-e", ".", "-v"],
                      cwd=self.repo_root, check=True)
        
        print("✓ nanobind version built successfully")
    
    def run_benchmarks(self, binding_type):
        """Run benchmarks for the current build."""
        print(f"\nRunning benchmarks for {binding_type}...")
        
        # Run benchmark script
        result = subprocess.run(
            [sys.executable, "benchmarks/benchmark_bindings.py"],
            cwd=self.repo_root,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print(f"Error running benchmarks: {result.stderr}")
            return None
        
        print(result.stdout)
        
        # Load results
        results_file = self.repo_root / "benchmark_results.json"
        if results_file.exists():
            with open(results_file) as f:
                return json.load(f)
        
        return None
    
    def compare_results(self):
        """Compare and analyze results from both implementations."""
        print("\n" + "="*70)
        print("COMPARATIVE ANALYSIS")
        print("="*70)
        
        if "pybind11" not in self.results or "nanobind" not in self.results:
            print("Error: Missing benchmark results")
            return
        
        pb11 = self.results["pybind11"]
        nb = self.results["nanobind"]
        
        print("\nImport Time Comparison:")
        self._compare_metric(
            "Mean import time",
            pb11["benchmarks"]["import_time"]["mean_ms"],
            nb["benchmarks"]["import_time"]["mean_ms"],
            "ms"
        )
        
        print("\nCall Overhead Comparison:")
        if "error" not in pb11["benchmarks"]["call_overhead"] and \
           "error" not in nb["benchmarks"]["call_overhead"]:
            self._compare_metric(
                "Mean call time",
                pb11["benchmarks"]["call_overhead"]["mean_ms"],
                nb["benchmarks"]["call_overhead"]["mean_ms"],
                "ms"
            )
        else:
            print("  Note: Call overhead benchmark had errors")
        
        print("\nEnd-to-End Performance Comparison:")
        self._compare_metric(
            "Mean processing time",
            pb11["benchmarks"]["end_to_end"]["mean_ms"],
            nb["benchmarks"]["end_to_end"]["mean_ms"],
            "ms"
        )
        
        if "wheel_info" in pb11 and "wheel_info" in nb:
            print("\nWheel Size Comparison:")
            self._compare_metric(
                "Wheel size",
                pb11["wheel_info"]["size_mb"],
                nb["wheel_info"]["size_mb"],
                "MB"
            )
    
    def _compare_metric(self, name, pybind11_val, nanobind_val, unit):
        """Compare and print a specific metric."""
        if pybind11_val is None or nanobind_val is None:
            print(f"  {name}: N/A")
            return
        
        diff = nanobind_val - pybind11_val
        pct_change = (diff / pybind11_val) * 100 if pybind11_val > 0 else 0
        
        print(f"  {name}:")
        print(f"    pybind11: {pybind11_val:.3f} {unit}")
        print(f"    nanobind: {nanobind_val:.3f} {unit}")
        print(f"    Difference: {diff:+.3f} {unit} ({pct_change:+.1f}%)")
        
        if pct_change < -5:
            print(f"    → nanobind is {-pct_change:.1f}% faster ✓")
        elif pct_change > 5:
            print(f"    → pybind11 is {pct_change:.1f}% faster ✓")
        else:
            print(f"    → Performance is similar (~)")
    
    def save_comparison_report(self):
        """Save detailed comparison report."""
        report_file = self.benchmarks_dir / "comparison_results.json"
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\nDetailed results saved to {report_file}")
    
    def run_full_comparison(self):
        """Run the complete comparison workflow."""
        try:
            # Build and benchmark pybind11
            self.build_pybind11()
            self.results["pybind11"] = self.run_benchmarks("pybind11")
            
            # Build and benchmark nanobind
            self.build_nanobind()
            self.results["nanobind"] = self.run_benchmarks("nanobind")
            
            # Compare results
            self.compare_results()
            
            # Save comparison report
            self.save_comparison_report()
            
            return True
            
        except Exception as e:
            print(f"\nError during comparison: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        finally:
            # Restore original pyproject.toml (pybind11 version)
            if (self.repo_root / "pyproject.toml.pybind11").exists():
                shutil.copy(
                    self.repo_root / "pyproject.toml.pybind11",
                    self.repo_root / "pyproject.toml"
                )


if __name__ == "__main__":
    repo_root = Path(__file__).parent.parent
    
    print("="*70)
    print("Comparative Benchmark: pybind11 vs nanobind")
    print("="*70)
    
    benchmark = ComparativeBenchmark(repo_root)
    success = benchmark.run_full_comparison()
    
    if success:
        print("\n" + "="*70)
        print("Benchmark completed successfully!")
        print("="*70)
        sys.exit(0)
    else:
        print("\n" + "="*70)
        print("Benchmark failed!")
        print("="*70)
        sys.exit(1)
