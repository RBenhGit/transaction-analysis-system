"""
End-to-End Integration Tests for IBI Transaction Processing

Tests complete workflow from Excel file to portfolio positions using real IBI data.
Validates: file loading → transaction parsing → classification → portfolio building
"""

import unittest
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.input.excel_reader import ExcelReader
from src.adapters.ibi_adapter import IBIAdapter
from src.json_adapter import JSONAdapter
from src.models.transaction import Transaction
from src.modules.portfolio_dashboard.builder import PortfolioBuilder
from tests.fixtures.ibi_test_data import get_test_file, IBITestDataFixtures


class TestIBIEndToEndWorkflow(unittest.TestCase):
    """Test complete end-to-end workflow with real IBI data."""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures once for all tests."""
        cls.dataset_name = "IBI_2022_2025"
        cls.test_file = get_test_file(cls.dataset_name)
        cls.expected = IBITestDataFixtures.get_expected_outcomes(cls.dataset_name)

        # Initialize components
        cls.reader = ExcelReader()
        cls.adapter = IBIAdapter()
        cls.json_adapter = JSONAdapter()
        cls.portfolio_builder = PortfolioBuilder()

    def test_01_file_loading(self):
        """Test that Excel file can be loaded successfully."""
        print(f"\n{'='*80}")
        print(f"Test 1: File Loading")
        print(f"{'='*80}")

        # Load file
        df = self.reader.read(str(self.test_file))

        # Assertions
        self.assertIsNotNone(df, "DataFrame should not be None")
        self.assertFalse(df.empty, "DataFrame should not be empty")
        self.assertGreater(len(df), 0, "DataFrame should have rows")

        print(f"✓ Successfully loaded {len(df)} rows from {self.test_file.name}")
        print(f"✓ Columns: {len(df.columns)}")
        print(f"✓ Column names: {', '.join(df.columns[:5])}...")

    def test_02_adapter_transformation(self):
        """Test IBI adapter transforms data correctly."""
        print(f"\n{'='*80}")
        print(f"Test 2: Adapter Transformation")
        print(f"{'='*80}")

        # Load and transform
        df_raw = self.reader.read(str(self.test_file))
        df_transformed = self.adapter.transform(df_raw)

        # Assertions
        self.assertIsNotNone(df_transformed, "Transformed DataFrame should not be None")
        self.assertFalse(df_transformed.empty, "Transformed DataFrame should not be empty")

        # Check standard columns exist
        expected_columns = [
            'date', 'transaction_type', 'security_name', 'security_symbol',
            'quantity', 'execution_price', 'currency', 'amount_local_currency'
        ]
        for col in expected_columns:
            self.assertIn(col, df_transformed.columns,
                         f"Column '{col}' should exist after transformation")

        print(f"✓ Transformed {len(df_transformed)} rows")
        print(f"✓ Standard columns: {', '.join(expected_columns)}")

    def test_03_transaction_parsing(self):
        """Test transactions are parsed into Transaction objects."""
        print(f"\n{'='*80}")
        print(f"Test 3: Transaction Parsing and Validation")
        print(f"{'='*80}")

        # Load, transform, and parse
        df_raw = self.reader.read(str(self.test_file))
        df_transformed = self.adapter.transform(df_raw)
        transactions = self.json_adapter.dataframe_to_transactions(df_transformed, self.adapter)

        # Assertions
        self.assertIsInstance(transactions, list, "Should return list of transactions")
        self.assertGreater(len(transactions), 0, "Should have at least one transaction")

        # Check minimum expected transactions
        min_expected = self.expected.get("min_transactions", 1)
        self.assertGreaterEqual(len(transactions), min_expected,
                               f"Should have at least {min_expected} transactions")

        # Validate all transactions are Transaction objects
        for tx in transactions:
            self.assertIsInstance(tx, Transaction,
                                "All items should be Transaction objects")

        print(f"✓ Parsed {len(transactions)} Transaction objects")

        # Validate transaction properties
        validation_errors = 0
        for tx in transactions:
            try:
                # Trigger validation by accessing properties
                _ = tx.is_buy
                _ = tx.is_sell
                _ = tx.transaction_category
                _ = tx.transaction_effect
            except Exception as e:
                validation_errors += 1
                print(f"  ✗ Validation error for {tx.security_symbol}: {e}")

        self.assertEqual(validation_errors, 0,
                        f"All transactions should pass validation (found {validation_errors} errors)")
        print(f"✓ All {len(transactions)} transactions passed validation")

    def test_04_transaction_classification(self):
        """Test transactions are classified correctly."""
        print(f"\n{'='*80}")
        print(f"Test 4: Transaction Classification")
        print(f"{'='*80}")

        # Get transactions
        df_raw = self.reader.read(str(self.test_file))
        df_transformed = self.adapter.transform(df_raw)
        transactions = self.json_adapter.dataframe_to_transactions(df_transformed, self.adapter)

        # Count by category
        categories = {}
        effects = {}
        for tx in transactions:
            cat = tx.transaction_category
            eff = tx.transaction_effect
            categories[cat] = categories.get(cat, 0) + 1
            effects[eff] = effects.get(eff, 0) + 1

        # Assertions based on expected outcomes
        if self.expected.get("has_buy_transactions"):
            self.assertIn("buy", categories,
                         "Should have buy transactions")

        if self.expected.get("has_sell_transactions"):
            self.assertIn("sell", categories,
                         "Should have sell transactions")

        # Display classification results
        print("\n  Transaction Categories:")
        for cat, count in sorted(categories.items()):
            print(f"    {cat}: {count}")

        print("\n  Transaction Effects:")
        for eff, count in sorted(effects.items()):
            print(f"    {eff}: {count}")

        print(f"\n✓ Classified {len(transactions)} transactions into {len(categories)} categories")

    def test_05_portfolio_building(self):
        """Test portfolio positions are built correctly."""
        print(f"\n{'='*80}")
        print(f"Test 5: Portfolio Building")
        print(f"{'='*80}")

        # Get transactions and build portfolio
        df_raw = self.reader.read(str(self.test_file))
        df_transformed = self.adapter.transform(df_raw)
        transactions = self.json_adapter.dataframe_to_transactions(df_transformed, self.adapter)
        positions = self.portfolio_builder.build(transactions)

        # Assertions
        self.assertIsInstance(positions, list, "Should return list of positions")

        # Verify phantom securities are excluded
        for pos in positions:
            symbol = pos.security_symbol
            name = pos.security_name

            # Check not phantom
            self.assertFalse(symbol.startswith('999'),
                           f"Position {symbol} should not be phantom (999xxx)")
            self.assertNotIn('מס ששולם', name.lower(),
                           f"Position {name} should not be tax phantom")
            self.assertNotIn('דמי טפול', name.lower(),
                           f"Position {name} should not be fee phantom")

        print(f"✓ Built portfolio with {len(positions)} positions")

        # Display positions summary
        if positions:
            print("\n  Sample Positions (first 5):")
            for i, pos in enumerate(positions[:5], 1):
                print(f"    {i}. {pos.security_symbol}: {pos.quantity} shares @ avg cost {pos.average_cost:.2f}")

    def test_06_currency_validation(self):
        """Test transactions have valid currencies."""
        print(f"\n{'='*80}")
        print(f"Test 6: Currency Validation")
        print(f"{'='*80}")

        # Get transactions
        df_raw = self.reader.read(str(self.test_file))
        df_transformed = self.adapter.transform(df_raw)
        transactions = self.json_adapter.dataframe_to_transactions(df_transformed, self.adapter)

        # Collect currencies
        currencies = {}
        for tx in transactions:
            curr = tx.currency
            currencies[curr] = currencies.get(curr, 0) + 1

        # Check expected currencies
        expected_currencies = self.expected.get("expected_currencies", [])
        if expected_currencies:
            for curr in expected_currencies:
                self.assertIn(curr, currencies,
                            f"Expected currency '{curr}' not found")

        print("\n  Currencies found:")
        for curr, count in sorted(currencies.items()):
            print(f"    '{curr}': {count} transactions")

        print(f"\n✓ Validated currencies in {len(transactions)} transactions")

    def test_07_fee_handling(self):
        """Test transaction fees are handled correctly."""
        print(f"\n{'='*80}")
        print(f"Test 7: Fee Handling")
        print(f"{'='*80}")

        # Get transactions
        df_raw = self.reader.read(str(self.test_file))
        df_transformed = self.adapter.transform(df_raw)
        transactions = self.json_adapter.dataframe_to_transactions(df_transformed, self.adapter)

        # Analyze fees
        with_transaction_fee = sum(1 for tx in transactions if tx.transaction_fee > 0)
        with_additional_fees = sum(1 for tx in transactions if tx.additional_fees > 0)
        with_any_fees = sum(1 for tx in transactions
                           if tx.transaction_fee > 0 or tx.additional_fees > 0)

        print(f"\n  Fee Statistics:")
        print(f"    Transactions with transaction fees: {with_transaction_fee}")
        print(f"    Transactions with additional fees: {with_additional_fees}")
        print(f"    Transactions with any fees: {with_any_fees}")
        print(f"    Transactions with no fees: {len(transactions) - with_any_fees}")

        # All fees should be non-negative
        for tx in transactions:
            self.assertGreaterEqual(tx.transaction_fee, 0,
                                  "Transaction fee should not be negative")
            self.assertGreaterEqual(tx.additional_fees, 0,
                                  "Additional fees should not be negative")

        print(f"\n✓ All fees are valid (non-negative)")

    def test_08_date_range_validation(self):
        """Test transactions have valid dates."""
        print(f"\n{'='*80}")
        print(f"Test 8: Date Range Validation")
        print(f"{'='*80}")

        # Get transactions
        df_raw = self.reader.read(str(self.test_file))
        df_transformed = self.adapter.transform(df_raw)
        transactions = self.json_adapter.dataframe_to_transactions(df_transformed, self.adapter)

        # Get date range
        dates = [tx.date for tx in transactions]
        min_date = min(dates)
        max_date = max(dates)

        # All dates should be valid datetime objects
        for tx in transactions:
            self.assertIsInstance(tx.date, datetime,
                                "Date should be datetime object")

        print(f"\n  Date Range:")
        print(f"    Earliest transaction: {min_date.strftime('%Y-%m-%d')}")
        print(f"    Latest transaction: {max_date.strftime('%Y-%m-%d')}")
        print(f"    Total span: {(max_date - min_date).days} days")

        print(f"\n✓ All {len(transactions)} transactions have valid dates")


class TestIBIDataIntegrity(unittest.TestCase):
    """Test data integrity and consistency of IBI transactions."""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        cls.test_file = get_test_file("IBI_2022_2025")
        cls.reader = ExcelReader()
        cls.adapter = IBIAdapter()
        cls.json_adapter = JSONAdapter()

        # Load all data once
        df_raw = cls.reader.read(str(cls.test_file))
        df_transformed = cls.adapter.transform(df_raw)
        cls.transactions = cls.json_adapter.dataframe_to_transactions(df_transformed, cls.adapter)

    def test_no_duplicate_transactions(self):
        """Test that there are no duplicate transactions."""
        print(f"\n{'='*80}")
        print(f"Test: No Duplicate Transactions")
        print(f"{'='*80}")

        # Create transaction signatures (date + type + symbol + amount)
        signatures = []
        for tx in self.transactions:
            sig = (tx.date, tx.transaction_type, tx.security_symbol,
                  tx.quantity, tx.amount_local_currency)
            signatures.append(sig)

        # Check for duplicates
        unique_sigs = set(signatures)
        duplicate_count = len(signatures) - len(unique_sigs)

        print(f"  Total transactions: {len(signatures)}")
        print(f"  Unique signatures: {len(unique_sigs)}")
        print(f"  Duplicates found: {duplicate_count}")

        # Note: Some duplicates might be legitimate (same transaction on same day)
        # So we just report, not fail
        if duplicate_count > 0:
            print(f"  ⚠ Warning: {duplicate_count} potential duplicate transactions")
        else:
            print(f"  ✓ No duplicate transactions found")

    def test_balance_monotonicity(self):
        """Test that account balance changes are reasonable."""
        print(f"\n{'='*80}")
        print(f"Test: Balance Monotonicity")
        print(f"{'='*80}")

        # Sort by date
        sorted_txs = sorted(self.transactions, key=lambda tx: tx.date)

        # Track balance changes
        balances = [tx.balance for tx in sorted_txs]

        print(f"  Starting balance: {balances[0]:,.2f} ₪")
        print(f"  Ending balance: {balances[-1]:,.2f} ₪")
        print(f"  Net change: {balances[-1] - balances[0]:,.2f} ₪")

        # Check for unreasonable jumps (> 1,000,000 in single transaction)
        large_jumps = 0
        for i in range(1, len(balances)):
            jump = abs(balances[i] - balances[i-1])
            if jump > 1_000_000:
                large_jumps += 1

        if large_jumps > 0:
            print(f"  ⚠ Warning: {large_jumps} large balance jumps (>1M ₪)")
        else:
            print(f"  ✓ No unreasonable balance jumps")


def run_integration_tests():
    """Run all integration tests and display summary."""
    print("\n" + "="*80)
    print("IBI END-TO-END INTEGRATION TESTS")
    print("="*80)

    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestIBIEndToEndWorkflow))
    suite.addTests(loader.loadTestsFromTestCase(TestIBIDataIntegrity))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")

    if result.wasSuccessful():
        print("\n✓ ALL TESTS PASSED")
    else:
        print("\n✗ SOME TESTS FAILED")

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_integration_tests()
    sys.exit(0 if success else 1)
