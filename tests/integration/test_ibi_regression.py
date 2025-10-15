"""
Regression Test Suite for IBI Transaction Processing

Prevents calculation changes from affecting accuracy:
- Saves baseline portfolio results
- Compares new results against baseline
- Detects unexpected changes in calculations
- Ensures backward compatibility
"""

import unittest
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.input.excel_reader import ExcelReader
from src.adapters.ibi_adapter import IBIAdapter
from src.json_adapter import JSONAdapter
from src.modules.portfolio_dashboard.builder import PortfolioBuilder
from tests.fixtures.ibi_test_data import get_test_file


class RegressionBaseline:
    """Manages regression test baselines."""

    BASELINE_DIR = Path(__file__).parent / "baselines"

    @classmethod
    def ensure_baseline_dir(cls):
        """Ensure baseline directory exists."""
        cls.BASELINE_DIR.mkdir(parents=True, exist_ok=True)

    @classmethod
    def get_baseline_path(cls, name: str) -> Path:
        """Get path to baseline file."""
        cls.ensure_baseline_dir()
        return cls.BASELINE_DIR / f"{name}.json"

    @classmethod
    def save_baseline(cls, name: str, data: dict):
        """Save baseline data to file."""
        path = cls.get_baseline_path(name)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)

    @classmethod
    def load_baseline(cls, name: str) -> dict:
        """Load baseline data from file."""
        path = cls.get_baseline_path(name)
        if not path.exists():
            return None

        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    @classmethod
    def baseline_exists(cls, name: str) -> bool:
        """Check if baseline exists."""
        return cls.get_baseline_path(name).exists()


class TestIBIRegression(unittest.TestCase):
    """Regression tests for IBI transaction processing."""

    BASELINE_NAME = "ibi_portfolio_2022_2025"

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        cls.test_file = get_test_file("IBI_2022_2025")

        # Load and process data
        reader = ExcelReader()
        adapter = IBIAdapter()
        json_adapter = JSONAdapter()
        builder = PortfolioBuilder()

        df_raw = reader.read(str(cls.test_file))
        df_transformed = adapter.transform(df_raw)
        cls.transactions = json_adapter.dataframe_to_transactions(df_transformed, adapter)
        cls.positions = builder.build(cls.transactions)

        # Create current results summary
        cls.current_results = cls._create_results_summary(cls.transactions, cls.positions)

    @classmethod
    def _create_results_summary(cls, transactions, positions) -> dict:
        """Create summary of current results for comparison."""
        # Transaction statistics
        tx_categories = {}
        for tx in transactions:
            cat = tx.transaction_category
            tx_categories[cat] = tx_categories.get(cat, 0) + 1

        # Position statistics
        position_summary = {}
        for pos in positions:
            position_summary[pos.security_symbol] = {
                "quantity": round(pos.quantity, 4),
                "average_cost": round(pos.average_cost, 4),
                "total_invested": round(pos.total_invested, 2),
                "currency": pos.currency
            }

        return {
            "metadata": {
                "test_file": str(cls.test_file.name),
                "run_timestamp": datetime.now().isoformat(),
                "total_transactions": len(transactions),
                "total_positions": len(positions)
            },
            "transaction_categories": tx_categories,
            "positions": position_summary
        }

    def test_01_create_or_update_baseline(self):
        """Create baseline if it doesn't exist, or show differences if it does."""
        print(f"\n{'='*80}")
        print(f"Regression Test 1: Baseline Management")
        print(f"{'='*80}")

        baseline = RegressionBaseline.load_baseline(self.BASELINE_NAME)

        if baseline is None:
            # No baseline exists - create it
            print("\n  [INFO] No baseline found - creating new baseline")
            RegressionBaseline.save_baseline(self.BASELINE_NAME, self.current_results)
            print(f"  [INFO] Baseline saved to: {RegressionBaseline.get_baseline_path(self.BASELINE_NAME)}")
            print(f"  [INFO] Transaction count: {self.current_results['metadata']['total_transactions']}")
            print(f"  [INFO] Position count: {self.current_results['metadata']['total_positions']}")
            print("\n[PASS] Baseline created successfully")
        else:
            # Baseline exists - show what's different
            print("\n  [INFO] Baseline exists - comparing results")
            print(f"  Baseline timestamp: {baseline['metadata']['run_timestamp']}")
            print(f"  Current timestamp: {self.current_results['metadata']['run_timestamp']}")

            # Compare metadata
            baseline_tx_count = baseline['metadata']['total_transactions']
            current_tx_count = self.current_results['metadata']['total_transactions']

            baseline_pos_count = baseline['metadata']['total_positions']
            current_pos_count = self.current_results['metadata']['total_positions']

            print(f"\n  Transaction counts:")
            print(f"    Baseline: {baseline_tx_count}")
            print(f"    Current:  {current_tx_count}")
            if baseline_tx_count != current_tx_count:
                print(f"    [WARNING] Difference: {current_tx_count - baseline_tx_count:+d}")

            print(f"\n  Position counts:")
            print(f"    Baseline: {baseline_pos_count}")
            print(f"    Current:  {current_pos_count}")
            if baseline_pos_count != current_pos_count:
                print(f"    [WARNING] Difference: {current_pos_count - baseline_pos_count:+d}")

            print("\n[PASS] Baseline comparison completed")

    def test_02_transaction_counts_stable(self):
        """Test that transaction counts haven't changed unexpectedly."""
        print(f"\n{'='*80}")
        print(f"Regression Test 2: Transaction Count Stability")
        print(f"{'='*80}")

        baseline = RegressionBaseline.load_baseline(self.BASELINE_NAME)

        if baseline is None:
            self.skipTest("No baseline exists yet - run test_01 first")

        baseline_count = baseline['metadata']['total_transactions']
        current_count = self.current_results['metadata']['total_transactions']

        print(f"\n  Baseline transactions: {baseline_count}")
        print(f"  Current transactions:  {current_count}")

        # Transaction count should be exactly the same
        self.assertEqual(current_count, baseline_count,
                        f"Transaction count changed: {current_count} != {baseline_count}")

        print("\n[PASS] Transaction count is stable")

    def test_03_position_counts_stable(self):
        """Test that position counts haven't changed unexpectedly."""
        print(f"\n{'='*80}")
        print(f"Regression Test 3: Position Count Stability")
        print(f"{'='*80}")

        baseline = RegressionBaseline.load_baseline(self.BASELINE_NAME)

        if baseline is None:
            self.skipTest("No baseline exists yet - run test_01 first")

        baseline_count = baseline['metadata']['total_positions']
        current_count = self.current_results['metadata']['total_positions']

        print(f"\n  Baseline positions: {baseline_count}")
        print(f"  Current positions:  {current_count}")

        # Position count should be exactly the same
        self.assertEqual(current_count, baseline_count,
                        f"Position count changed: {current_count} != {baseline_count}")

        print("\n[PASS] Position count is stable")

    def test_04_position_quantities_stable(self):
        """Test that position quantities match baseline."""
        print(f"\n{'='*80}")
        print(f"Regression Test 4: Position Quantities Stability")
        print(f"{'='*80}")

        baseline = RegressionBaseline.load_baseline(self.BASELINE_NAME)

        if baseline is None:
            self.skipTest("No baseline exists yet - run test_01 first")

        baseline_positions = baseline['positions']
        current_positions = self.current_results['positions']

        # Check all positions
        differences = []
        for symbol in current_positions:
            if symbol not in baseline_positions:
                differences.append(f"NEW: {symbol}")
                continue

            baseline_qty = baseline_positions[symbol]['quantity']
            current_qty = current_positions[symbol]['quantity']

            if abs(current_qty - baseline_qty) > 0.0001:  # Allow tiny floating point errors
                differences.append(
                    f"{symbol}: {baseline_qty:.4f} -> {current_qty:.4f}"
                )

        # Check for removed positions
        for symbol in baseline_positions:
            if symbol not in current_positions:
                differences.append(f"REMOVED: {symbol}")

        print(f"\n  Total positions compared: {len(current_positions)}")
        print(f"  Differences found: {len(differences)}")

        if differences:
            print("\n  Position differences (first 10):")
            for diff in differences[:10]:
                print(f"    {diff}")

        # Assert no differences
        self.assertEqual(len(differences), 0,
                        f"Found {len(differences)} position quantity changes")

        print("\n[PASS] All position quantities match baseline")

    def test_05_average_costs_stable(self):
        """Test that average costs match baseline."""
        print(f"\n{'='*80}")
        print(f"Regression Test 5: Average Cost Stability")
        print(f"{'='*80}")

        baseline = RegressionBaseline.load_baseline(self.BASELINE_NAME)

        if baseline is None:
            self.skipTest("No baseline exists yet - run test_01 first")

        baseline_positions = baseline['positions']
        current_positions = self.current_results['positions']

        # Check average costs
        differences = []
        for symbol in current_positions:
            if symbol not in baseline_positions:
                continue  # New position - skip

            baseline_cost = baseline_positions[symbol]['average_cost']
            current_cost = current_positions[symbol]['average_cost']

            # Allow 0.01% difference for floating point errors
            if baseline_cost > 0:
                pct_diff = abs(current_cost - baseline_cost) / baseline_cost
                if pct_diff > 0.0001:
                    differences.append(
                        f"{symbol}: {baseline_cost:.4f} -> {current_cost:.4f} ({pct_diff*100:.4f}%)"
                    )

        print(f"\n  Positions compared: {len([s for s in current_positions if s in baseline_positions])}")
        print(f"  Cost differences found: {len(differences)}")

        if differences:
            print("\n  Average cost differences (first 10):")
            for diff in differences[:10]:
                print(f"    {diff}")

        # Assert no significant differences
        self.assertEqual(len(differences), 0,
                        f"Found {len(differences)} average cost changes")

        print("\n[PASS] All average costs match baseline")

    def test_06_transaction_categories_stable(self):
        """Test that transaction category counts are stable."""
        print(f"\n{'='*80}")
        print(f"Regression Test 6: Transaction Category Stability")
        print(f"{'='*80}")

        baseline = RegressionBaseline.load_baseline(self.BASELINE_NAME)

        if baseline is None:
            self.skipTest("No baseline exists yet - run test_01 first")

        baseline_cats = baseline['transaction_categories']
        current_cats = self.current_results['transaction_categories']

        # Compare categories
        differences = []
        all_categories = set(list(baseline_cats.keys()) + list(current_cats.keys()))

        for cat in all_categories:
            baseline_count = baseline_cats.get(cat, 0)
            current_count = current_cats.get(cat, 0)

            if baseline_count != current_count:
                differences.append(
                    f"{cat}: {baseline_count} -> {current_count} ({current_count - baseline_count:+d})"
                )

        print(f"\n  Categories compared: {len(all_categories)}")
        print(f"  Differences found: {len(differences)}")

        if differences:
            print("\n  Category count differences:")
            for diff in differences:
                print(f"    {diff}")

        # Assert no differences
        self.assertEqual(len(differences), 0,
                        f"Found {len(differences)} category count changes")

        print("\n[PASS] Transaction categories match baseline")


def run_regression_tests():
    """Run all regression tests and display summary."""
    print("\n" + "="*80)
    print("IBI REGRESSION TEST SUITE")
    print("="*80)
    print("\nPrevents calculation changes from affecting portfolio accuracy")
    print("="*80)

    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test class
    suite.addTests(loader.loadTestsFromTestCase(TestIBIRegression))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "="*80)
    print("REGRESSION TEST SUMMARY")
    print("="*80)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")

    if result.wasSuccessful():
        print("\n[PASS] ALL REGRESSION TESTS PASSED")
        print("Portfolio calculations are stable and match baseline")
    else:
        print("\n[FAIL] SOME REGRESSION TESTS FAILED")
        print("Portfolio calculations have changed - review changes carefully")

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_regression_tests()
    sys.exit(0 if success else 1)
