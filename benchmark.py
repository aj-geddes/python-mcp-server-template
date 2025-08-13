#!/usr/bin/env python3
"""
Performance benchmark suite for the MCP server template.
Measures startup time, request latency, throughput, and resource usage.
"""

import asyncio
import statistics
import time
from pathlib import Path
from typing import Dict, List, Any
import tempfile
import subprocess
import sys
import json

# Import the server functions for direct testing
sys.path.insert(0, str(Path(__file__).parent))
from mcp_server import (
    echo_impl,
    health_check_impl,
    list_files_impl,
    read_file_impl,
    write_file_impl,
    run_shell_command_impl
)


class PerformanceBenchmark:
    """Performance benchmarking suite for MCP server operations."""
    
    def __init__(self):
        self.results = {}
        self.temp_dir = None
        
    async def setup(self):
        """Setup test environment."""
        self.temp_dir = tempfile.mkdtemp()
        # Create test files for benchmarking
        test_file = Path(self.temp_dir) / "benchmark_test.txt"
        test_content = "A" * 1024  # 1KB test content
        test_file.write_text(test_content)
        
        # Create directory structure
        (Path(self.temp_dir) / "subdir").mkdir()
        for i in range(10):
            (Path(self.temp_dir) / f"file_{i}.txt").write_text(f"Content {i}")
            
    def cleanup(self):
        """Cleanup test environment."""
        if self.temp_dir:
            import shutil
            shutil.rmtree(self.temp_dir)
            
    async def measure_function_latency(self, func, *args, iterations=100):
        """Measure function execution latency."""
        latencies = []
        
        # Warmup
        for _ in range(10):
            await func(*args)
            
        # Actual measurement
        for _ in range(iterations):
            start_time = time.perf_counter()
            await func(*args)
            end_time = time.perf_counter()
            latencies.append((end_time - start_time) * 1000)  # Convert to ms
            
        return {
            "min_ms": min(latencies),
            "max_ms": max(latencies),
            "mean_ms": statistics.mean(latencies),
            "median_ms": statistics.median(latencies),
            "p95_ms": self._percentile(latencies, 95),
            "p99_ms": self._percentile(latencies, 99),
            "iterations": iterations
        }
        
    def _percentile(self, data: List[float], percentile: float) -> float:
        """Calculate percentile of data."""
        sorted_data = sorted(data)
        index = percentile / 100.0 * (len(sorted_data) - 1)
        if index.is_integer():
            return sorted_data[int(index)]
        else:
            lower = sorted_data[int(index)]
            upper = sorted_data[int(index) + 1]
            return lower + (upper - lower) * (index - int(index))
            
    async def benchmark_echo(self):
        """Benchmark echo function."""
        print("🔄 Benchmarking echo function...")
        
        # Test different message sizes
        test_cases = [
            ("small", "Hello"),
            ("medium", "A" * 100),
            ("large", "A" * 1000)
        ]
        
        results = {}
        for case_name, message in test_cases:
            latency = await self.measure_function_latency(echo_impl, message)
            results[case_name] = latency
            print(f"  {case_name}: {latency['mean_ms']:.2f}ms avg, {latency['p95_ms']:.2f}ms p95")
            
        return results
        
    async def benchmark_health_check(self):
        """Benchmark health check function."""
        print("🔄 Benchmarking health check function...")
        
        latency = await self.measure_function_latency(health_check_impl)
        print(f"  Health check: {latency['mean_ms']:.2f}ms avg, {latency['p95_ms']:.2f}ms p95")
        
        return latency
        
    async def benchmark_file_operations(self):
        """Benchmark file operations."""
        print("🔄 Benchmarking file operations...")
        
        # Mock validate_path to use our temp directory
        import mcp_server
        original_validate_path = mcp_server.validate_path
        
        def mock_validate_path(path, base_path=None):
            return Path(self.temp_dir) / path
            
        mcp_server.validate_path = mock_validate_path
        
        try:
            results = {}
            
            # Benchmark list_files
            latency = await self.measure_function_latency(list_files_impl, ".")
            results["list_files"] = latency
            print(f"  List files: {latency['mean_ms']:.2f}ms avg, {latency['p95_ms']:.2f}ms p95")
            
            # Benchmark read_file
            latency = await self.measure_function_latency(read_file_impl, "benchmark_test.txt")
            results["read_file"] = latency
            print(f"  Read file: {latency['mean_ms']:.2f}ms avg, {latency['p95_ms']:.2f}ms p95")
            
            # Benchmark write_file
            test_content = "Benchmark content " * 10
            latency = await self.measure_function_latency(
                write_file_impl, "benchmark_write.txt", test_content
            )
            results["write_file"] = latency
            print(f"  Write file: {latency['mean_ms']:.2f}ms avg, {latency['p95_ms']:.2f}ms p95")
            
            return results
            
        finally:
            mcp_server.validate_path = original_validate_path
            
    async def benchmark_throughput(self):
        """Benchmark overall throughput."""
        print("🔄 Benchmarking throughput...")
        
        async def mixed_workload():
            """Execute a mixed workload of operations."""
            await echo_impl("test message")
            await health_check_impl()
            
        # Measure concurrent operations
        concurrent_levels = [1, 5, 10, 20]
        results = {}
        
        for concurrency in concurrent_levels:
            print(f"  Testing concurrency level: {concurrency}")
            
            start_time = time.perf_counter()
            tasks = [mixed_workload() for _ in range(concurrency * 10)]
            await asyncio.gather(*tasks)
            end_time = time.perf_counter()
            
            total_ops = len(tasks)
            duration = end_time - start_time
            ops_per_second = total_ops / duration
            
            results[f"concurrency_{concurrency}"] = {
                "ops_per_second": ops_per_second,
                "duration_seconds": duration,
                "total_operations": total_ops
            }
            print(f"    {ops_per_second:.1f} ops/sec")
            
        return results
        
    async def benchmark_memory_usage(self):
        """Benchmark memory usage patterns."""
        print("🔄 Benchmarking memory usage...")
        
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        
        # Baseline memory
        baseline_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Execute operations and measure memory growth
        operations = []
        for i in range(100):
            await echo_impl(f"Message {i}")
            if i % 10 == 0:
                current_memory = process.memory_info().rss / 1024 / 1024
                operations.append({
                    "operation": i,
                    "memory_mb": current_memory,
                    "memory_growth_mb": current_memory - baseline_memory
                })
                
        return {
            "baseline_memory_mb": baseline_memory,
            "final_memory_mb": operations[-1]["memory_mb"],
            "memory_growth_mb": operations[-1]["memory_growth_mb"],
            "operations": operations
        }
        
    def measure_startup_time(self):
        """Measure server startup time."""
        print("🔄 Measuring startup time...")
        
        # Create a simple test script that imports the server
        test_script = f"""
import time
import sys
import os
# Redirect stderr to suppress warnings and logging
sys.stderr = open(os.devnull, 'w')
start = time.perf_counter()
sys.path.insert(0, '{Path(__file__).parent}')
import mcp_server
end = time.perf_counter()
print(f"{{(end - start) * 1000:.2f}}")
"""
        
        startup_times = []
        for _ in range(10):
            result = subprocess.run(
                [sys.executable, "-c", test_script],
                capture_output=True,
                text=True,
                env={**os.environ, "MCP_METRICS_PORT": "0"}  # Disable metrics server
            )
            if result.returncode == 0:
                try:
                    # Extract just the number from the output
                    lines = result.stdout.strip().split('\n')
                    time_str = lines[-1]  # Get the last line
                    startup_times.append(float(time_str))
                except (ValueError, IndexError):
                    print(f"Failed to parse startup time from: {result.stdout}")
                    continue
                
        if startup_times:
            return {
                "min_ms": min(startup_times),
                "max_ms": max(startup_times),
                "mean_ms": statistics.mean(startup_times),
                "median_ms": statistics.median(startup_times),
                "iterations": len(startup_times)
            }
        else:
            return {"error": "Failed to measure startup time"}
            
    async def run_all_benchmarks(self):
        """Run all performance benchmarks."""
        print("🚀 Starting Performance Benchmark Suite")
        print("=" * 50)
        
        await self.setup()
        
        try:
            # Startup time
            self.results["startup"] = self.measure_startup_time()
            
            # Individual function benchmarks
            self.results["echo"] = await self.benchmark_echo()
            self.results["health_check"] = await self.benchmark_health_check()
            self.results["file_operations"] = await self.benchmark_file_operations()
            
            # Throughput and concurrency
            self.results["throughput"] = await self.benchmark_throughput()
            
            # Memory usage
            try:
                self.results["memory"] = await self.benchmark_memory_usage()
            except ImportError:
                self.results["memory"] = {"error": "psutil not available for memory benchmarks"}
                
        finally:
            self.cleanup()
            
        print("\n" + "=" * 50)
        print("📊 Benchmark Results Summary")
        print("=" * 50)
        
        self.print_summary()
        return self.results
        
    def print_summary(self):
        """Print benchmark results summary."""
        # Startup performance
        if "startup" in self.results and "mean_ms" in self.results["startup"]:
            startup = self.results["startup"]["mean_ms"]
            print(f"⚡ Startup Time: {startup:.2f}ms")
            if startup > 100:
                print("  ⚠️  WARNING: Startup time >100ms (Dr. Chen's standard)")
                
        # Function latencies
        if "health_check" in self.results:
            hc_latency = self.results["health_check"]["mean_ms"]
            print(f"🔍 Health Check: {hc_latency:.2f}ms avg")
            
        # File operation performance  
        if "file_operations" in self.results:
            for op, metrics in self.results["file_operations"].items():
                print(f"📁 {op.replace('_', ' ').title()}: {metrics['mean_ms']:.2f}ms avg")
                
        # Throughput
        if "throughput" in self.results:
            best_throughput = max(
                result["ops_per_second"] 
                for result in self.results["throughput"].values()
            )
            print(f"🚀 Peak Throughput: {best_throughput:.1f} ops/sec")
            
        # Memory usage
        if "memory" in self.results and "memory_growth_mb" in self.results["memory"]:
            memory_growth = self.results["memory"]["memory_growth_mb"]
            print(f"💾 Memory Growth: {memory_growth:.2f}MB over 100 operations")
            
        # Performance grade based on Dr. Chen's standards
        print(f"\n🎯 Performance Grade: {self.calculate_performance_grade()}")
        
    def calculate_performance_grade(self):
        """Calculate overall performance grade based on Dr. Chen's standards."""
        score = 0
        max_score = 0
        
        # Startup time scoring (sub-100ms target)
        if "startup" in self.results and "mean_ms" in self.results["startup"]:
            startup = self.results["startup"]["mean_ms"]
            if startup <= 50:
                score += 25
            elif startup <= 100:
                score += 20
            elif startup <= 200:
                score += 10
            max_score += 25
            
        # Health check latency (target <1ms)
        if "health_check" in self.results:
            hc_latency = self.results["health_check"]["mean_ms"]
            if hc_latency <= 1:
                score += 25
            elif hc_latency <= 5:
                score += 20
            elif hc_latency <= 10:
                score += 10
            max_score += 25
            
        # Throughput scoring
        if "throughput" in self.results:
            best_throughput = max(
                result["ops_per_second"] 
                for result in self.results["throughput"].values()
            )
            if best_throughput >= 1000:
                score += 25
            elif best_throughput >= 500:
                score += 20
            elif best_throughput >= 100:
                score += 10
            max_score += 25
            
        # Memory efficiency scoring
        if "memory" in self.results and "memory_growth_mb" in self.results["memory"]:
            memory_growth = self.results["memory"]["memory_growth_mb"]
            if memory_growth <= 1:
                score += 25
            elif memory_growth <= 5:
                score += 20
            elif memory_growth <= 10:
                score += 10
            max_score += 25
            
        if max_score == 0:
            return "INSUFFICIENT DATA"
            
        percentage = (score / max_score) * 100
        
        if percentage >= 90:
            return "💎 EXCEPTIONAL (A+)"
        elif percentage >= 80:
            return "⭐ EXCELLENT (A)"
        elif percentage >= 70:
            return "🟢 GOOD (B)"
        elif percentage >= 60:
            return "🟡 NEEDS IMPROVEMENT (C)"
        else:
            return "🔴 CRITICAL (F)"
            
    def save_results(self, filename="benchmark_results.json"):
        """Save benchmark results to JSON file."""
        with open(filename, "w") as f:
            json.dump(self.results, f, indent=2)
        print(f"📄 Results saved to {filename}")


async def main():
    """Main benchmark execution."""
    benchmark = PerformanceBenchmark()
    results = await benchmark.run_all_benchmarks()
    benchmark.save_results()
    
    return results


if __name__ == "__main__":
    # Run benchmarks
    results = asyncio.run(main())