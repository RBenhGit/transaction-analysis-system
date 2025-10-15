"""
Performance Testing Suite for IBI Transaction Processing

Tests system performance with large transaction volumes:
- Load times for large Excel files
- Transformation throughput
- Portfolio building performance
- Memory usage
"""

import unittest
import sys
import time
import tracemalloc
from pathlib import Path
from typing import Dict

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.input.excel_reader import ExcelReader
from src.adapters.ibi_adapter import IBIAdapter
from src.json_adapter import JSONAdapter
from src.modules.portfolio_dashboard.builder import PortfolioBuilder
from tests.fixtures.ibi_test_data import get_test_file


class PerformanceMetrics:
    """Helper class to track performance metrics."""

    def __init__(self, operation_name: str):
        self.operation_name = operation_name
        self.start_time = None
        self.end_time = None
        self.start_memory = None
        self.end_memory = None
        self.peak_memory = None

    def __enter__(self):
        """Start timing and memory tracking."""
        tracemalloc.start()
        self.start_memory = tracemalloc.get_traced_memory()[0]
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop timing and memory tracking."""
        self.end_time = time.perf_counter()
        current, peak = tracemalloc.get_traced_memory()
        self.end_memory = current
        self.peak_memory = peak
        tracemalloc.stop()

    @property
    def duration(self) -> float:
        """Get operation duration in seconds."""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return 0.0

    @property
    def memory_used_mb(self) -> float:
        """Get memory used in MB."""
        if self.start_memory and self.end_memory:
            return (self.end_memory - self.start_memory) / (1024 * 1024)
        return 0.0

    @property
    def peak_memory_mb(self) -> float:
        """Get peak memory in MB."""
        if self.peak_memory:
            return self.peak_memory / (1024 * 1024)
        return 0.0

    def print_summary(self):
        """Print performance summary."""
        print(f"\n  Performance Metrics for '{self.operation_name}':")
        print(f"    Duration: {self.duration:.3f} seconds")
        print(f"    Memory used: {self.memory_used_mb:.2f} MB")
        print(f"    Peak memory: {self.peak_memory_mb:.2f} MB")


class TestIBIPerformance(unittest.TestCase):
    """Performance tests for IBI transaction processing."""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        cls.test_file = get_test_file("IBI_2022_2025")

        # Performance thresholds (can be adjusted based on requirements)
        cls.THRESHOLDS = {
            "excel_load_seconds": 5.0,        # Max 5 seconds to load Excel
            "transform_seconds": 3.0,         # Max 3 seconds to transform
            "parse_seconds": 5.0,             # Max 5 seconds to parse to objects
            "portfolio_build_seconds": 2.0,   # Max 2 seconds to build portfolio
            "total_workflow_seconds": 15.0,   # Max 15 seconds for complete workflow
            "memory_mb": 500.0,               # Max 500 MB memory usage
        }

    def test_01_excel_loading_performance(self):
        """Test Excel file loading performance."""
        print(f"\n{'='*80}")
        print(f"Performance Test 1: Excel Loading")
        print(f"{'='*80}")

        reader = ExcelReader()

        with PerformanceMetrics("Excel Loading") as metrics:
            df = reader.read(str(self.test_file))

        metrics.print_summary()

        # Assertions
        self.assertLess(metrics.duration, self.THRESHOLDS["excel_load_seconds"],
                       f"Excel loading took too long: {metrics.duration:.2f}s")

        print(f"\n[PASS] Excel loading completed within threshold ({self.THRESHOLDS['excel_load_seconds']}s)")
        print(f"  Loaded {len(df)} rows")

    def test_02_transformation_performance(self):
        """Test IBI adapter transformation performance."""
        print(f"\n{'='*80}")
        print(f"Performance Test 2: Data Transformation")
        print(f"{'='*80}")

        reader = ExcelReader()
        adapter = IBIAdapter()

        # Load data first (not timed)
        df = reader.read(str(self.test_file))

        with PerformanceMetrics("Data Transformation") as metrics:
            df_transformed = adapter.transform(df)

        metrics.print_summary()

        # Assertions
        self.assertLess(metrics.duration, self.THRESHOLDS["transform_seconds"],
                       f"Transformation took too long: {metrics.duration:.2f}s")

        print(f"\n[PASS] Transformation completed within threshold ({self.THRESHOLDS['transform_seconds']}s)")
        print(f"  Transformed {len(df_transformed)} transactions")

    def test_03_transaction_parsing_performance(self):
        """Test transaction parsing to objects performance."""
        print(f"\n{'='*80}")
        print(f"Performance Test 3: Transaction Parsing")
        print(f"{'='*80}")

        reader = ExcelReader()
        adapter = IBIAdapter()
        json_adapter = JSONAdapter()

        # Load and transform first (not timed)
        df = reader.read(str(self.test_file))
        df_transformed = adapter.transform(df)

        with PerformanceMetrics("Transaction Parsing") as metrics:
            transactions = json_adapter.dataframe_to_transactions(df_transformed, adapter)

        metrics.print_summary()

        # Assertions
        self.assertLess(metrics.duration, self.THRESHOLDS["parse_seconds"],
                       f"Parsing took too long: {metrics.duration:.2f}s")

        print(f"\n[PASS] Parsing completed within threshold ({self.THRESHOLDS['parse_seconds']}s)")
        print(f"  Parsed {len(transactions)} Transaction objects")

        # Calculate throughput
        throughput = len(transactions) / metrics.duration
        print(f"  Throughput: {throughput:.0f} transactions/second")

    def test_04_portfolio_building_performance(self):
        """Test portfolio building performance."""
        print(f"\n{'='*80}")
        print(f"Performance Test 4: Portfolio Building")
        print(f"{'='*80}")

        reader = ExcelReader()
        adapter = IBIAdapter()
        json_adapter = JSONAdapter()
        builder = PortfolioBuilder()

        # Load, transform, and parse first (not timed)
        df = reader.read(str(self.test_file))
        df_transformed = adapter.transform(df)
        transactions = json_adapter.dataframe_to_transactions(df_transformed, adapter)

        with PerformanceMetrics("Portfolio Building") as metrics:
            positions = builder.build(transactions)

        metrics.print_summary()

        # Assertions
        self.assertLess(metrics.duration, self.THRESHOLDS["portfolio_build_seconds"],
                       f"Portfolio building took too long: {metrics.duration:.2f}s")

        print(f"\n[PASS] Portfolio building completed within threshold ({self.THRESHOLDS['portfolio_build_seconds']}s)")
        print(f"  Built {len(positions)} positions from {len(transactions)} transactions")

    def test_05_end_to_end_performance(self):
        """Test complete end-to-end workflow performance."""
        print(f"\n{'='*80}")
        print(f"Performance Test 5: Complete End-to-End Workflow")
        print(f"{'='*80}")

        reader = ExcelReader()
        adapter = IBIAdapter()
        json_adapter = JSONAdapter()
        builder = PortfolioBuilder()

        with PerformanceMetrics("Complete Workflow") as metrics:
            # Complete workflow
            df = reader.read(str(self.test_file))
            df_transformed = adapter.transform(df)
            transactions = json_adapter.dataframe_to_transactions(df_transformed, adapter)
            positions = builder.build(transactions)

        metrics.print_summary()

        # Assertions
        self.assertLess(metrics.duration, self.THRESHOLDS["total_workflow_seconds"],
                       f"End-to-end workflow took too long: {metrics.duration:.2f}s")

        print(f"\n[PASS] End-to-end workflow completed within threshold ({self.THRESHOLDS['total_workflow_seconds']}s)")
        print(f"  Processed {len(transactions)} transactions into {len(positions)} positions")

    def test_06_memory_usage(self):
        """Test memory usage during complete workflow."""
        print(f"\n{'='*80}")
        print(f"Performance Test 6: Memory Usage")
        print(f"{'='*80}")

        reader = ExcelReader()
        adapter = IBIAdapter()
        json_adapter = JSONAdapter()
        builder = PortfolioBuilder()

        with PerformanceMetrics("Memory Usage Test") as metrics:
            df = reader.read(str(self.test_file))
            df_transformed = adapter.transform(df)
            transactions = json_adapter.dataframe_to_transactions(df_transformed, adapter)
            positions = builder.build(transactions)

        metrics.print_summary()

        # Assertions
        self.assertLess(metrics.peak_memory_mb, self.THRESHOLDS["memory_mb"],
                       f"Memory usage too high: {metrics.peak_memory_mb:.2f} MB")

        print(f"\n[PASS] Memory usage within threshold ({self.THRESHOLDS['memory_mb']} MB)")


class TestIBIScalability(unittest.TestCase):
    """Test scalability with repeated processing."""

    def test_multiple_runs_consistency(self):
        """Test that performance is consistent across multiple runs."""
        print(f"\n{'='*80}")
        print(f"Scalability Test: Multiple Runs Consistency")
        print(f"{'='*80}")

        test_file = get_test_file("IBI_2022_2025")
        reader = ExcelReader()
        adapter = IBIAdapter()
        json_adapter = JSONAdapter()

        num_runs = 5
        durations = []

        print(f"\n  Running {num_runs} iterations...")

        for i in range(num_runs):
            start = time.perf_counter()

            df = reader.read(str(test_file))
            df_transformed = adapter.transform(df)
            transactions = json_adapter.dataframe_to_transactions(df_transformed, adapter)

            duration = time.perf_counter() - start
            durations.append(duration)
            print(f"    Run {i+1}: {duration:.3f}s")

        # Calculate statistics
        avg_duration = sum(durations) / len(durations)
        min_duration = min(durations)
        max_duration = max(durations)
        variance = max_duration - min_duration

        print(f"\n  Performance Statistics:")
        print(f"    Average: {avg_duration:.3f}s")
        print(f"    Min: {min_duration:.3f}s")
        print(f"    Max: {max_duration:.3f}s")
        print(f"    Variance: {variance:.3f}s")

        # Check consistency (variance should be less than 50% of average)
        max_acceptable_variance = avg_duration * 0.5
        self.assertLess(variance, max_acceptable_variance,
                       f"Performance variance too high: {variance:.3f}s")

        print(f"\n[PASS] Performance is consistent across {num_runs} runs")


def run_performance_tests():
    """Run all performance tests and display summary."""
    print("\n" + "="*80)
    print("IBI PERFORMANCE TESTING SUITE")
    print("="*80)

    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestIBIPerformance))
    suite.addTests(loader.loadTestsFromTestCase(TestIBIScalability))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "="*80)
    print("PERFORMANCE TEST SUMMARY")
    print("="*80)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")

    if result.wasSuccessful():
        print("\n[PASS] ALL PERFORMANCE TESTS PASSED")
    else:
        print("\n✗ SOME PERFORMANCE TESTS FAILED")

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_performance_tests()
    sys.exit(0 if success else 1)
