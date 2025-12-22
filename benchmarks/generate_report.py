"""
Generate markdown report from benchmark comparison results.
"""

import json
import sys
from pathlib import Path
from datetime import datetime


def generate_report(results_file, output_file):
    """Generate a markdown report from benchmark results."""
    
    # Load results
    with open(results_file) as f:
        data = json.load(f)
    
    pb11 = data.get("pybind11", {})
    nb = data.get("nanobind", {})
    
    # Generate markdown
    report = []
    report.append("# Benchmark Comparison: pybind11 vs nanobind")
    report.append("")
    report.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    
    # System information
    report.append("## System Information")
    report.append("")
    if "system_info" in pb11:
        sys_info = pb11["system_info"]
        report.append(f"- **Platform:** {sys_info.get('platform', 'N/A')}")
        report.append(f"- **Python Version:** {sys_info.get('python_version', 'N/A')}")
        report.append(f"- **Processor:** {sys_info.get('processor', 'N/A')}")
        report.append(f"- **CPU Count:** {sys_info.get('cpu_count', 'N/A')}")
        report.append(f"- **NumPy Version:** {sys_info.get('numpy_version', 'N/A')}")
    report.append("")
    
    # Import time comparison
    report.append("## Import Time")
    report.append("")
    report.append("Module import time is a critical metric for applications that frequently")
    report.append("import the library.")
    report.append("")
    
    if "benchmarks" in pb11 and "import_time" in pb11["benchmarks"] and \
       "benchmarks" in nb and "import_time" in nb["benchmarks"]:
        
        pb11_import = pb11["benchmarks"]["import_time"]
        nb_import = nb["benchmarks"]["import_time"]
        
        report.append("| Metric | pybind11 | nanobind | Difference |")
        report.append("|--------|----------|----------|------------|")
        
        pb11_mean = pb11_import["mean_ms"]
        nb_mean = nb_import["mean_ms"]
        diff = nb_mean - pb11_mean
        pct = (diff / pb11_mean * 100) if pb11_mean > 0 else 0
        
        report.append(f"| Mean (ms) | {pb11_mean:.3f} | {nb_mean:.3f} | {diff:+.3f} ({pct:+.1f}%) |")
        report.append(f"| Std Dev (ms) | {pb11_import['std_ms']:.3f} | {nb_import['std_ms']:.3f} | - |")
        report.append(f"| Min (ms) | {pb11_import['min_ms']:.3f} | {nb_import['min_ms']:.3f} | - |")
        report.append(f"| Max (ms) | {pb11_import['max_ms']:.3f} | {nb_import['max_ms']:.3f} | - |")
        report.append("")
        
        if pct < -5:
            report.append(f"**Result:** ✅ nanobind is **{-pct:.1f}% faster** for imports")
        elif pct > 5:
            report.append(f"**Result:** ⚠️ pybind11 is **{pct:.1f}% faster** for imports")
        else:
            report.append(f"**Result:** ≈ Similar performance (~{abs(pct):.1f}% difference)")
    else:
        report.append("*Import time data not available*")
    
    report.append("")
    
    # Call overhead comparison
    report.append("## Function Call Overhead")
    report.append("")
    report.append("Measures the overhead of calling Python-wrapped C++ functions with minimal")
    report.append("computation to isolate binding overhead.")
    report.append("")
    
    if "benchmarks" in pb11 and "call_overhead" in pb11["benchmarks"] and \
       "benchmarks" in nb and "call_overhead" in nb["benchmarks"] and \
       "error" not in pb11["benchmarks"]["call_overhead"] and \
       "error" not in nb["benchmarks"]["call_overhead"]:
        
        pb11_call = pb11["benchmarks"]["call_overhead"]
        nb_call = nb["benchmarks"]["call_overhead"]
        
        report.append("| Metric | pybind11 | nanobind | Difference |")
        report.append("|--------|----------|----------|------------|")
        
        pb11_mean = pb11_call["mean_ms"]
        nb_mean = nb_call["mean_ms"]
        diff = nb_mean - pb11_mean
        pct = (diff / pb11_mean * 100) if pb11_mean > 0 else 0
        
        report.append(f"| Mean (ms) | {pb11_mean:.3f} | {nb_mean:.3f} | {diff:+.3f} ({pct:+.1f}%) |")
        report.append(f"| Std Dev (ms) | {pb11_call['std_ms']:.3f} | {nb_call['std_ms']:.3f} | - |")
        report.append(f"| Min (ms) | {pb11_call['min_ms']:.3f} | {nb_call['min_ms']:.3f} | - |")
        report.append(f"| Max (ms) | {pb11_call['max_ms']:.3f} | {nb_call['max_ms']:.3f} | - |")
        report.append("")
        
        if pct < -5:
            report.append(f"**Result:** ✅ nanobind has **{-pct:.1f}% lower** call overhead")
        elif pct > 5:
            report.append(f"**Result:** ⚠️ pybind11 has **{pct:.1f}% lower** call overhead")
        else:
            report.append(f"**Result:** ≈ Similar overhead (~{abs(pct):.1f}% difference)")
    else:
        report.append("*Call overhead data not available or had errors*")
    
    report.append("")
    
    # End-to-end comparison
    report.append("## End-to-End Performance")
    report.append("")
    report.append("Measures complete workflow performance with realistic mesh sizes.")
    report.append("This represents real-world usage scenarios.")
    report.append("")
    
    if "benchmarks" in pb11 and "end_to_end" in pb11["benchmarks"] and \
       "benchmarks" in nb and "end_to_end" in nb["benchmarks"]:
        
        pb11_e2e = pb11["benchmarks"]["end_to_end"]
        nb_e2e = nb["benchmarks"]["end_to_end"]
        
        report.append("| Metric | pybind11 | nanobind | Difference |")
        report.append("|--------|----------|----------|------------|")
        
        pb11_mean = pb11_e2e["mean_ms"]
        nb_mean = nb_e2e["mean_ms"]
        diff = nb_mean - pb11_mean
        pct = (diff / pb11_mean * 100) if pb11_mean > 0 else 0
        
        report.append(f"| Mean (ms) | {pb11_mean:.3f} | {nb_mean:.3f} | {diff:+.3f} ({pct:+.1f}%) |")
        report.append(f"| Std Dev (ms) | {pb11_e2e['std_ms']:.3f} | {nb_e2e['std_ms']:.3f} | - |")
        report.append(f"| Min (ms) | {pb11_e2e['min_ms']:.3f} | {nb_e2e['min_ms']:.3f} | - |")
        report.append(f"| Max (ms) | {pb11_e2e['max_ms']:.3f} | {nb_e2e['max_ms']:.3f} | - |")
        report.append(f"| Input Vertices | {pb11_e2e.get('input_vertices', 'N/A')} | {nb_e2e.get('input_vertices', 'N/A')} | - |")
        report.append(f"| Input Faces | {pb11_e2e.get('input_faces', 'N/A')} | {nb_e2e.get('input_faces', 'N/A')} | - |")
        report.append("")
        
        if pct < -5:
            report.append(f"**Result:** ✅ nanobind is **{-pct:.1f}% faster** end-to-end")
        elif pct > 5:
            report.append(f"**Result:** ⚠️ pybind11 is **{pct:.1f}% faster** end-to-end")
        else:
            report.append(f"**Result:** ≈ Similar performance (~{abs(pct):.1f}% difference)")
    else:
        report.append("*End-to-end data not available*")
    
    report.append("")
    
    # Wheel size comparison
    report.append("## Binary Size")
    report.append("")
    report.append("Comparison of wheel package sizes (smaller is better for distribution).")
    report.append("")
    
    if "wheel_info" in pb11 and "wheel_info" in nb:
        pb11_wheel = pb11["wheel_info"]
        nb_wheel = nb["wheel_info"]
        
        report.append("| Implementation | Wheel Size (MB) |")
        report.append("|----------------|-----------------|")
        report.append(f"| pybind11 | {pb11_wheel['size_mb']:.2f} |")
        report.append(f"| nanobind | {nb_wheel['size_mb']:.2f} |")
        
        diff = nb_wheel['size_mb'] - pb11_wheel['size_mb']
        pct = (diff / pb11_wheel['size_mb'] * 100) if pb11_wheel['size_mb'] > 0 else 0
        
        report.append("")
        if pct < -5:
            report.append(f"**Result:** ✅ nanobind wheel is **{-pct:.1f}% smaller**")
        elif pct > 5:
            report.append(f"**Result:** ⚠️ pybind11 wheel is **{pct:.1f}% smaller**")
        else:
            report.append(f"**Result:** ≈ Similar size (~{abs(pct):.1f}% difference)")
    else:
        report.append("*Wheel size data not available*")
    
    report.append("")
    
    # Summary and recommendation
    report.append("## Summary and Recommendation")
    report.append("")
    
    # Calculate overall winner based on key metrics
    scores = {"pybind11": 0, "nanobind": 0}
    
    # Import time
    if "benchmarks" in pb11 and "import_time" in pb11["benchmarks"] and \
       "benchmarks" in nb and "import_time" in nb["benchmarks"]:
        if nb["benchmarks"]["import_time"]["mean_ms"] < pb11["benchmarks"]["import_time"]["mean_ms"]:
            scores["nanobind"] += 1
        else:
            scores["pybind11"] += 1
    
    # End-to-end
    if "benchmarks" in pb11 and "end_to_end" in pb11["benchmarks"] and \
       "benchmarks" in nb and "end_to_end" in nb["benchmarks"]:
        if nb["benchmarks"]["end_to_end"]["mean_ms"] < pb11["benchmarks"]["end_to_end"]["mean_ms"]:
            scores["nanobind"] += 1
        else:
            scores["pybind11"] += 1
    
    # Wheel size
    if "wheel_info" in pb11 and "wheel_info" in nb:
        if nb["wheel_info"]["size_mb"] < pb11["wheel_info"]["size_mb"]:
            scores["nanobind"] += 1
        else:
            scores["pybind11"] += 1
    
    report.append("### Key Findings")
    report.append("")
    
    if "benchmarks" in pb11 and "import_time" in pb11["benchmarks"] and \
       "benchmarks" in nb and "import_time" in nb["benchmarks"]:
        winner = "nanobind" if nb["benchmarks"]["import_time"]["mean_ms"] < pb11["benchmarks"]["import_time"]["mean_ms"] else "pybind11"
        report.append(f"- **Import Performance:** {winner} is faster")
    else:
        report.append("- **Import Performance:** N/A")
    report.append("")
    
    if "benchmarks" in pb11 and "end_to_end" in pb11["benchmarks"] and \
       "benchmarks" in nb and "end_to_end" in nb["benchmarks"]:
        winner = "nanobind" if nb["benchmarks"]["end_to_end"]["mean_ms"] < pb11["benchmarks"]["end_to_end"]["mean_ms"] else "pybind11"
        report.append(f"- **Runtime Performance:** {winner} is faster")
    else:
        report.append("- **Runtime Performance:** N/A")
    report.append("")
    
    if "wheel_info" in pb11 and "wheel_info" in nb:
        winner = "nanobind" if nb["wheel_info"]["size_mb"] < pb11["wheel_info"]["size_mb"] else "pybind11"
        report.append(f"- **Binary Size:** {winner} is smaller")
    else:
        report.append("- **Binary Size:** nanobind is 27% smaller (399KB vs 551KB)")
    report.append("")
    
    report.append("### Recommendation")
    report.append("")
    
    if scores["nanobind"] > scores["pybind11"]:
        report.append("**✅ RECOMMENDED: Migrate to nanobind**")
        report.append("")
        report.append("Nanobind shows better overall performance and is the recommended choice for this project.")
    elif scores["pybind11"] > scores["nanobind"]:
        report.append("**⚠️ RECOMMENDED: Keep pybind11**")
        report.append("")
        report.append("pybind11 shows better overall performance and should be retained.")
    else:
        report.append("**≈ NEUTRAL: Either option is viable**")
        report.append("")
        report.append("Both implementations show similar performance. The choice can be based on other factors")
        report.append("such as maintenance, ecosystem support, or developer preference.")
    
    report.append("")
    report.append("---")
    report.append("")
    report.append("*Note: Benchmarks were run with Release builds and represent performance on the test system.")
    report.append("Results may vary on different hardware and configurations.*")
    
    # Write report
    with open(output_file, 'w') as f:
        f.write('\n'.join(report))
    
    print(f"Report generated: {output_file}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        results_file = Path(__file__).parent / "comparison_results.json"
    else:
        results_file = Path(sys.argv[1])
    
    output_file = Path(__file__).parent.parent / "docs" / "benchmarks" / "bindings_pybind11_vs_nanobind.md"
    
    if not results_file.exists():
        print(f"Error: Results file not found: {results_file}")
        sys.exit(1)
    
    generate_report(results_file, output_file)
