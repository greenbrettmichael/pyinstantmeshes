"""
Benchmark suite for comparing pybind11 and nanobind implementations.

This module provides comprehensive benchmarks to compare performance between
pybind11 and nanobind Python bindings for pyinstantmeshes.
"""

import time
import sys
import os
import platform
import subprocess
import json
import numpy as np
from pathlib import Path


class BenchmarkRunner:
    """Runner for benchmark tests."""
    
    def __init__(self):
        self.results = {
            "system_info": self.get_system_info(),
            "benchmarks": {}
        }
    
    def get_system_info(self):
        """Collect system information."""
        return {
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "processor": platform.processor(),
            "cpu_count": os.cpu_count(),
            "numpy_version": np.__version__,
        }
    
    def benchmark_import_time(self, num_iterations=50):
        """Benchmark module import time."""
        import_times = []
        
        for _ in range(num_iterations):
            # Remove module from cache
            if 'pyinstantmeshes' in sys.modules:
                del sys.modules['pyinstantmeshes']
            if '_pyinstantmeshes' in sys.modules:
                del sys.modules['_pyinstantmeshes']
            
            # Measure import time
            start = time.perf_counter()
            import pyinstantmeshes
            end = time.perf_counter()
            
            import_times.append((end - start) * 1000)  # Convert to ms
        
        return {
            "mean_ms": np.mean(import_times),
            "std_ms": np.std(import_times),
            "min_ms": np.min(import_times),
            "max_ms": np.max(import_times),
            "iterations": num_iterations
        }
    
    def benchmark_call_overhead(self, num_iterations=1000):
        """Benchmark function call overhead with minimal data."""
        import pyinstantmeshes
        
        # Create minimal test mesh (tetrahedron)
        vertices = np.array([
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [0.5, 0.866, 0.0],
            [0.5, 0.433, 0.816]
        ], dtype=np.float32)
        
        faces = np.array([
            [0, 1, 2],
            [0, 1, 3],
            [0, 2, 3],
            [1, 2, 3]
        ], dtype=np.int32)
        
        call_times = []
        
        for _ in range(num_iterations):
            start = time.perf_counter()
            try:
                output_vertices, output_faces = pyinstantmeshes.remesh(
                    vertices, faces, 
                    target_vertex_count=10,
                    deterministic=True
                )
            except Exception as e:
                # Some configurations may fail with very small meshes
                print(f"Warning: Call failed with {e}")
                continue
            end = time.perf_counter()
            
            call_times.append((end - start) * 1000)  # Convert to ms
        
        if not call_times:
            return {"error": "All iterations failed"}
        
        return {
            "mean_ms": np.mean(call_times),
            "std_ms": np.std(call_times),
            "min_ms": np.min(call_times),
            "max_ms": np.max(call_times),
            "iterations": len(call_times)
        }
    
    def benchmark_end_to_end(self, num_iterations=10):
        """Benchmark end-to-end meshing workflow."""
        import pyinstantmeshes
        
        # Create a more substantial mesh (subdivided cube)
        vertices, faces = self._create_subdivided_cube(subdivisions=3)
        
        processing_times = []
        
        for _ in range(num_iterations):
            start = time.perf_counter()
            output_vertices, output_faces = pyinstantmeshes.remesh(
                vertices, faces,
                target_vertex_count=500,
                deterministic=True
            )
            end = time.perf_counter()
            
            processing_times.append((end - start) * 1000)  # Convert to ms
        
        return {
            "mean_ms": np.mean(processing_times),
            "std_ms": np.std(processing_times),
            "min_ms": np.min(processing_times),
            "max_ms": np.max(processing_times),
            "iterations": num_iterations,
            "input_vertices": len(vertices),
            "input_faces": len(faces)
        }
    
    def _create_subdivided_cube(self, subdivisions=2):
        """Create a subdivided cube mesh for testing."""
        # Create initial cube vertices
        vertices = []
        step = 1.0 / subdivisions
        
        for i in range(subdivisions + 1):
            for j in range(subdivisions + 1):
                for k in range(subdivisions + 1):
                    vertices.append([i * step, j * step, k * step])
        
        vertices = np.array(vertices, dtype=np.float32)
        
        # Create faces (simplified - just enough for testing)
        faces = []
        def index(i, j, k):
            return i * (subdivisions + 1) * (subdivisions + 1) + j * (subdivisions + 1) + k
        
        # Generate faces for each cube cell
        for i in range(subdivisions):
            for j in range(subdivisions):
                for k in range(subdivisions):
                    # Front face
                    v0 = index(i, j, k)
                    v1 = index(i+1, j, k)
                    v2 = index(i+1, j+1, k)
                    v3 = index(i, j+1, k)
                    faces.extend([[v0, v1, v2], [v0, v2, v3]])
                    
                    # Back face
                    v4 = index(i, j, k+1)
                    v5 = index(i+1, j, k+1)
                    v6 = index(i+1, j+1, k+1)
                    v7 = index(i, j+1, k+1)
                    faces.extend([[v4, v6, v5], [v4, v7, v6]])
        
        faces = np.array(faces, dtype=np.int32)
        
        return vertices, faces
    
    def run_all_benchmarks(self):
        """Run all benchmarks and collect results."""
        print("Running import time benchmark...")
        self.results["benchmarks"]["import_time"] = self.benchmark_import_time()
        
        print("Running call overhead benchmark...")
        self.results["benchmarks"]["call_overhead"] = self.benchmark_call_overhead()
        
        print("Running end-to-end benchmark...")
        self.results["benchmarks"]["end_to_end"] = self.benchmark_end_to_end()
        
        return self.results
    
    def save_results(self, filename):
        """Save results to JSON file."""
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
    
    def print_results(self):
        """Print results in a readable format."""
        print("\n" + "="*70)
        print("BENCHMARK RESULTS")
        print("="*70)
        
        print("\nSystem Information:")
        for key, value in self.results["system_info"].items():
            print(f"  {key}: {value}")
        
        print("\nBenchmark Results:")
        for bench_name, bench_results in self.results["benchmarks"].items():
            print(f"\n{bench_name.upper()}:")
            for key, value in bench_results.items():
                if isinstance(value, float):
                    print(f"  {key}: {value:.3f}")
                else:
                    print(f"  {key}: {value}")


def get_wheel_size():
    """Get the size of the built wheel."""
    dist_dir = Path("dist")
    if not dist_dir.exists():
        return None
    
    wheels = list(dist_dir.glob("*.whl"))
    if not wheels:
        return None
    
    # Get the most recent wheel
    latest_wheel = max(wheels, key=lambda p: p.stat().st_mtime)
    size_mb = latest_wheel.stat().st_size / (1024 * 1024)
    
    return {
        "filename": latest_wheel.name,
        "size_mb": size_mb
    }


if __name__ == "__main__":
    runner = BenchmarkRunner()
    results = runner.run_all_benchmarks()
    
    # Add wheel size if available
    wheel_info = get_wheel_size()
    if wheel_info:
        results["wheel_info"] = wheel_info
    
    # Save and print results
    runner.print_results()
    
    # Save to JSON
    output_file = "benchmark_results.json"
    runner.save_results(output_file)
    print(f"\nResults saved to {output_file}")
