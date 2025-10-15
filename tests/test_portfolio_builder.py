"""
Unit tests for Portfolio Builder.

Tests phantom position detection, transaction processing, and portfolio calculations.
"""

import unittest
from datetime import datetime
from src.modules.portfolio_dashboard.builder import PortfolioBuilder
from src.models.transaction import Transaction


class TestPhantomSecurityDetection(unittest.TestCase):
    """Test phantom security detection logic."""

    def setUp(self):
        """Set up test fixtures."""
        self.builder = PortfolioBuilder()

    def test_phantom_symbol_999_series(self):
        """Test detection of 999xxxx phantom symbols."""
        # Tax tracking symbol
        tx = Transaction(
            date=datetime(2024, 1, 15),
            transaction_type="משיכת מס חול מטח",
            security_name="מס ששולם",
            security_symbol="9993983",
            quantity=0.0,
            execution_price=0.0,
            currency="$",
            transaction_fee=0.0,
            additional_fees=0.0,
            amount_foreign_currency=0.0,
            amount_local_currency=-100.0,
            balance=10000.0,
            capital_gains_tax_estimate=0.0,
            bank="IBI"
        )
        self.assertTrue(self.builder._is_phantom_security(tx))

    def test_phantom_symbol_fee_placeholder(self):
        """Test detection of FEE placeholder symbol."""
        tx = Transaction(
            date=datetime(2024, 1, 15),
            transaction_type="דמי טפול מזומן בשח",
            security_name="דמי טפול",
            security_symbol="FEE",
            quantity=0.0,
            execution_price=0.0,
            currency="₪",
            transaction_fee=0.0,
            additional_fees=0.0,
            amount_foreign_currency=0.0,
            amount_local_currency=-50.0,
            balance=10000.0,
            capital_gains_tax_estimate=0.0,
            bank="IBI"
        )
        self.assertTrue(self.builder._is_phantom_security(tx))

    def test_phantom_symbol_tax_placeholder(self):
        """Test detection of TAX placeholder symbol."""
        tx = Transaction(
            date=datetime(2024, 1, 15),
            transaction_type="משיכת מס מטח",
            security_name="מס",
            security_symbol="TAX",
            quantity=0.0,
            execution_price=0.0,
            currency="$",
            transaction_fee=0.0,
            additional_fees=0.0,
            amount_foreign_currency=0.0,
            amount_local_currency=-100.0,
            balance=10000.0,
            capital_gains_tax_estimate=0.0,
            bank="IBI"
        )
        self.assertTrue(self.builder._is_phantom_security(tx))

    def test_phantom_name_tax_paid(self):
        """Test detection of 'מס ששולם' security name."""
        tx = Transaction(
            date=datetime(2024, 1, 15),
            transaction_type="משיכת מס חול מטח",
            security_name="מס ששולם",
            security_symbol="ANYSYMBOL",  # Even with normal symbol
            quantity=0.0,
            execution_price=0.0,
            currency="$",
            transaction_fee=0.0,
            additional_fees=0.0,
            amount_foreign_currency=0.0,
            amount_local_currency=-100.0,
            balance=10000.0,
            capital_gains_tax_estimate=0.0,
            bank="IBI"
        )
        self.assertTrue(self.builder._is_phantom_security(tx))

    def test_phantom_name_handling_fees(self):
        """Test detection of 'דמי טפול' security name."""
        tx = Transaction(
            date=datetime(2024, 1, 15),
            transaction_type="דמי טפול מזומן בשח",
            security_name="דמי טפול",
            security_symbol="ANYSYMBOL",
            quantity=0.0,
            execution_price=0.0,
            currency="₪",
            transaction_fee=0.0,
            additional_fees=0.0,
            amount_foreign_currency=0.0,
            amount_local_currency=-50.0,
            balance=10000.0,
            capital_gains_tax_estimate=0.0,
            bank="IBI"
        )
        self.assertTrue(self.builder._is_phantom_security(tx))

    def test_phantom_name_commission_variation(self):
        """Test detection of commission/fee name variations."""
        tx = Transaction(
            date=datetime(2024, 1, 15),
            transaction_type="עמלת פעולה",
            security_name="עמלת פעולה בשקלים",
            security_symbol="COMM123",
            quantity=0.0,
            execution_price=0.0,
            currency="₪",
            transaction_fee=0.0,
            additional_fees=0.0,
            amount_foreign_currency=0.0,
            amount_local_currency=-25.0,
            balance=10000.0,
            capital_gains_tax_estimate=0.0,
            bank="IBI"
        )
        self.assertTrue(self.builder._is_phantom_security(tx))

    def test_non_phantom_real_stock(self):
        """Test that real stock symbols are not detected as phantom."""
        tx = Transaction(
            date=datetime(2024, 1, 15),
            transaction_type="קניה שח",
            security_name="Apple Inc",
            security_symbol="AAPL",
            quantity=10.0,
            execution_price=150.50,
            currency="$",
            transaction_fee=5.0,
            additional_fees=0.5,
            amount_foreign_currency=1505.00,
            amount_local_currency=-5520.00,
            balance=45000.0,
            capital_gains_tax_estimate=0.0,
            bank="IBI"
        )
        self.assertFalse(self.builder._is_phantom_security(tx))

    def test_non_phantom_nis_stock(self):
        """Test that NIS stock symbols are not detected as phantom."""
        tx = Transaction(
            date=datetime(2024, 1, 15),
            transaction_type="קניה שח",
            security_name="בנק לאומי",
            security_symbol="LUMI",
            quantity=100.0,
            execution_price=7500.0,  # Agorot
            currency="₪",
            transaction_fee=15.0,
            additional_fees=0.0,
            amount_foreign_currency=0.0,
            amount_local_currency=-7515.0,
            balance=45000.0,
            capital_gains_tax_estimate=0.0,
            bank="IBI"
        )
        self.assertFalse(self.builder._is_phantom_security(tx))

    def test_phantom_detection_case_insensitive(self):
        """Test that phantom detection is case-insensitive for names."""
        tx = Transaction(
            date=datetime(2024, 1, 15),
            transaction_type="משיכת מס",
            security_name="מס ששולם",  # Mixed case Hebrew
            security_symbol="NORMAL",
            quantity=0.0,
            execution_price=0.0,
            currency="$",
            transaction_fee=0.0,
            additional_fees=0.0,
            amount_foreign_currency=0.0,
            amount_local_currency=-100.0,
            balance=10000.0,
            capital_gains_tax_estimate=0.0,
            bank="IBI"
        )
        self.assertTrue(self.builder._is_phantom_security(tx))

    def test_phantom_detection_with_whitespace(self):
        """Test phantom detection handles extra whitespace."""
        tx = Transaction(
            date=datetime(2024, 1, 15),
            transaction_type="משיכת מס",
            security_name="  מס ששולם  ",  # Extra whitespace
            security_symbol="  9993983  ",  # Extra whitespace
            quantity=0.0,
            execution_price=0.0,
            currency="$",
            transaction_fee=0.0,
            additional_fees=0.0,
            amount_foreign_currency=0.0,
            amount_local_currency=-100.0,
            balance=10000.0,
            capital_gains_tax_estimate=0.0,
            bank="IBI"
        )
        self.assertTrue(self.builder._is_phantom_security(tx))


class TestPortfolioBuilderWithPhantoms(unittest.TestCase):
    """Test portfolio building with phantom securities."""

    def setUp(self):
        """Set up test fixtures."""
        self.builder = PortfolioBuilder()

    def test_phantom_transactions_excluded_from_portfolio(self):
        """Test that phantom transactions don't create positions."""
        transactions = [
            # Real stock purchase
            Transaction(
                date=datetime(2024, 1, 10),
                transaction_type="קניה שח",
                security_name="Apple Inc",
                security_symbol="AAPL",
                quantity=10.0,
                execution_price=150.0,
                currency="$",
                transaction_fee=5.0,
                additional_fees=0.5,
                amount_foreign_currency=1500.0,
                amount_local_currency=-5500.0,
                balance=50000.0,
                capital_gains_tax_estimate=0.0,
                bank="IBI"
            ),
            # Phantom tax entry (should be excluded)
            Transaction(
                date=datetime(2024, 1, 15),
                transaction_type="משיכת מס חול מטח",
                security_name="מס ששולם",
                security_symbol="9993983",
                quantity=0.0,
                execution_price=0.0,
                currency="$",
                transaction_fee=0.0,
                additional_fees=0.0,
                amount_foreign_currency=0.0,
                amount_local_currency=-100.0,
                balance=49900.0,
                capital_gains_tax_estimate=0.0,
                bank="IBI"
            ),
            # Phantom fee entry (should be excluded)
            Transaction(
                date=datetime(2024, 1, 20),
                transaction_type="דמי טפול מזומן בשח",
                security_name="דמי טפול",
                security_symbol="FEE",
                quantity=0.0,
                execution_price=0.0,
                currency="₪",
                transaction_fee=0.0,
                additional_fees=0.0,
                amount_foreign_currency=0.0,
                amount_local_currency=-50.0,
                balance=49850.0,
                capital_gains_tax_estimate=0.0,
                bank="IBI"
            ),
            # Another real stock purchase
            Transaction(
                date=datetime(2024, 1, 25),
                transaction_type="קניה שח",
                security_name="Microsoft Corp",
                security_symbol="MSFT",
                quantity=5.0,
                execution_price=300.0,
                currency="$",
                transaction_fee=5.0,
                additional_fees=0.5,
                amount_foreign_currency=1500.0,
                amount_local_currency=-5500.0,
                balance=44350.0,
                capital_gains_tax_estimate=0.0,
                bank="IBI"
            ),
        ]

        positions = self.builder.build(transactions)

        # Should only have 2 positions (AAPL and MSFT), phantoms excluded
        self.assertEqual(len(positions), 2)

        # Verify symbols
        symbols = {p.security_symbol for p in positions}
        self.assertEqual(symbols, {"AAPL", "MSFT"})

        # Verify no phantom symbols in positions
        for pos in positions:
            self.assertFalse(pos.security_symbol.startswith('999'))
            self.assertNotEqual(pos.security_symbol, 'FEE')
            self.assertNotEqual(pos.security_symbol, 'TAX')
            self.assertNotIn('מס ששולם', pos.security_name)
            self.assertNotIn('דמי טפול', pos.security_name)


if __name__ == '__main__':
    unittest.main()
