"""
Unit tests for Transaction model Pydantic validation.

Tests all validators to ensure data integrity and proper error handling.
"""

import unittest
from datetime import datetime
from pydantic import ValidationError
from src.models.transaction import Transaction


class TestTransactionFieldValidation(unittest.TestCase):
    """Test individual field validators."""

    def setUp(self):
        """Set up valid transaction data for testing."""
        self.valid_data = {
            'date': datetime(2024, 1, 15),
            'transaction_type': 'קניה שח',
            'security_name': 'Apple Inc',
            'security_symbol': 'AAPL',
            'quantity': 10.0,
            'execution_price': 150.50,
            'currency': '$',
            'transaction_fee': 5.0,
            'additional_fees': 0.5,
            'amount_foreign_currency': 1505.00,
            'amount_local_currency': -5520.00,
            'balance': 45000.0,
            'capital_gains_tax_estimate': 0.0,
            'bank': 'IBI'
        }

    def test_valid_transaction(self):
        """Test creating transaction with all valid data."""
        tx = Transaction(**self.valid_data)
        self.assertEqual(tx.security_symbol, 'AAPL')
        self.assertEqual(tx.quantity, 10.0)
        self.assertEqual(tx.currency, '$')

    def test_negative_quantity_allowed_for_ibi(self):
        """Test that negative quantity is allowed (IBI format uses negative for sells)."""
        data = self.valid_data.copy()
        data['quantity'] = -10.0

        # Should NOT raise an error - negative quantities are valid in IBI format
        tx = Transaction(**data)
        self.assertEqual(tx.quantity, -10.0)

    def test_zero_quantity_allowed(self):
        """Test that zero quantity is allowed (for fees, dividends)."""
        valid_data = self.valid_data.copy()
        valid_data['quantity'] = 0.0

        tx = Transaction(**valid_data)
        self.assertEqual(tx.quantity, 0.0)

    def test_negative_execution_price_fails(self):
        """Test that negative execution price is rejected."""
        invalid_data = self.valid_data.copy()
        invalid_data['execution_price'] = -150.50

        with self.assertRaises(ValidationError) as context:
            Transaction(**invalid_data)

        self.assertIn('execution_price', str(context.exception))

    def test_zero_execution_price_allowed(self):
        """Test that zero execution price is allowed (for some transactions)."""
        valid_data = self.valid_data.copy()
        valid_data['execution_price'] = 0.0

        tx = Transaction(**valid_data)
        self.assertEqual(tx.execution_price, 0.0)


class TestCurrencyValidation(unittest.TestCase):
    """Test currency field validation."""

    def setUp(self):
        """Set up minimal valid transaction data."""
        self.base_data = {
            'date': datetime(2024, 1, 15),
            'transaction_type': 'קניה שח',
            'security_name': 'Apple Inc',
            'security_symbol': 'AAPL',
            'balance': 45000.0,
        }

    def test_valid_currency_shekel_symbol(self):
        """Test NIS shekel symbol is accepted."""
        tx = Transaction(**self.base_data, currency='₪')
        self.assertEqual(tx.currency, '₪')

    def test_valid_currency_dollar_symbol(self):
        """Test USD dollar symbol is accepted."""
        tx = Transaction(**self.base_data, currency='$')
        self.assertEqual(tx.currency, '$')

    def test_valid_currency_usd(self):
        """Test 'USD' string is accepted."""
        tx = Transaction(**self.base_data, currency='USD')
        self.assertEqual(tx.currency, 'USD')

    def test_valid_currency_nis(self):
        """Test 'NIS' string is accepted."""
        tx = Transaction(**self.base_data, currency='NIS')
        self.assertEqual(tx.currency, 'NIS')

    def test_valid_currency_ils(self):
        """Test 'ILS' string is accepted."""
        tx = Transaction(**self.base_data, currency='ILS')
        self.assertEqual(tx.currency, 'ILS')

    def test_empty_currency_allowed(self):
        """Test empty currency string is allowed (for flexibility)."""
        tx = Transaction(**self.base_data, currency='')
        self.assertEqual(tx.currency, '')

    def test_invalid_currency_fails(self):
        """Test that invalid currency is rejected."""
        invalid_currencies = ['EUR', 'GBP', 'JPY', 'invalid', '¥', '£']

        for currency in invalid_currencies:
            with self.subTest(currency=currency):
                with self.assertRaises(ValidationError) as context:
                    Transaction(**self.base_data, currency=currency)

                error_msg = str(context.exception)
                self.assertIn('currency', error_msg.lower())


class TestFeeValidation(unittest.TestCase):
    """Test fee field validation."""

    def setUp(self):
        """Set up minimal valid transaction data."""
        self.base_data = {
            'date': datetime(2024, 1, 15),
            'transaction_type': 'קניה שח',
            'security_name': 'Apple Inc',
            'security_symbol': 'AAPL',
            'balance': 45000.0,
            'currency': '$'
        }

    def test_zero_fees_allowed(self):
        """Test that zero fees are allowed."""
        tx = Transaction(**self.base_data, transaction_fee=0.0, additional_fees=0.0)
        self.assertEqual(tx.transaction_fee, 0.0)
        self.assertEqual(tx.additional_fees, 0.0)

    def test_positive_fees_allowed(self):
        """Test that positive fees are allowed."""
        tx = Transaction(**self.base_data, transaction_fee=5.0, additional_fees=2.5)
        self.assertEqual(tx.transaction_fee, 5.0)
        self.assertEqual(tx.additional_fees, 2.5)

    def test_negative_transaction_fee_fails(self):
        """Test that negative transaction fee is rejected."""
        with self.assertRaises(ValidationError) as context:
            Transaction(**self.base_data, transaction_fee=-5.0)

        self.assertIn('transaction_fee', str(context.exception))

    def test_negative_additional_fees_fails(self):
        """Test that negative additional fees are rejected."""
        with self.assertRaises(ValidationError) as context:
            Transaction(**self.base_data, additional_fees=-2.5)

        self.assertIn('additional_fees', str(context.exception))


class TestSecuritySymbolValidation(unittest.TestCase):
    """Test security symbol validation."""

    def setUp(self):
        """Set up minimal valid transaction data."""
        self.base_data = {
            'date': datetime(2024, 1, 15),
            'transaction_type': 'קניה שח',
            'security_name': 'Apple Inc',
            'balance': 45000.0,
            'currency': '$'
        }

    def test_valid_symbol(self):
        """Test valid security symbol is accepted."""
        valid_symbols = ['AAPL', 'MSFT', 'GOOGL', '9993983', 'BRK.B', 'SPY']

        for symbol in valid_symbols:
            with self.subTest(symbol=symbol):
                tx = Transaction(**self.base_data, security_symbol=symbol)
                self.assertEqual(tx.security_symbol, symbol)

    def test_empty_symbol_fails(self):
        """Test that empty security symbol is rejected."""
        with self.assertRaises(ValidationError) as context:
            Transaction(**self.base_data, security_symbol='')

        self.assertIn('Security symbol cannot be empty', str(context.exception))

    def test_whitespace_symbol_fails(self):
        """Test that whitespace-only symbol is rejected."""
        with self.assertRaises(ValidationError) as context:
            Transaction(**self.base_data, security_symbol='   ')

        self.assertIn('Security symbol cannot be empty', str(context.exception))

    def test_symbol_stripped(self):
        """Test that security symbol is stripped of whitespace."""
        tx = Transaction(**self.base_data, security_symbol='  AAPL  ')
        self.assertEqual(tx.security_symbol, 'AAPL')

    def test_too_long_symbol_fails(self):
        """Test that symbol longer than 20 chars is rejected."""
        long_symbol = 'A' * 21

        with self.assertRaises(ValidationError) as context:
            Transaction(**self.base_data, security_symbol=long_symbol)

        self.assertIn('too long', str(context.exception))

    def test_max_length_symbol_accepted(self):
        """Test that symbol of exactly 20 chars is accepted."""
        max_symbol = 'A' * 20
        tx = Transaction(**self.base_data, security_symbol=max_symbol)
        self.assertEqual(tx.security_symbol, max_symbol)


class TestSecurityNameValidation(unittest.TestCase):
    """Test security name validation."""

    def setUp(self):
        """Set up minimal valid transaction data."""
        self.base_data = {
            'date': datetime(2024, 1, 15),
            'transaction_type': 'קניה שח',
            'security_symbol': 'AAPL',
            'balance': 45000.0,
            'currency': '$'
        }

    def test_valid_name(self):
        """Test valid security name is accepted."""
        valid_names = ['Apple Inc', 'Microsoft Corp', 'בנק לאומי', 'מס ששולם']

        for name in valid_names:
            with self.subTest(name=name):
                tx = Transaction(**self.base_data, security_name=name)
                self.assertEqual(tx.security_name, name)

    def test_empty_name_fails(self):
        """Test that empty security name is rejected."""
        with self.assertRaises(ValidationError) as context:
            Transaction(**self.base_data, security_name='')

        self.assertIn('Security name cannot be empty', str(context.exception))

    def test_whitespace_name_fails(self):
        """Test that whitespace-only name is rejected."""
        with self.assertRaises(ValidationError) as context:
            Transaction(**self.base_data, security_name='   ')

        self.assertIn('Security name cannot be empty', str(context.exception))

    def test_name_stripped(self):
        """Test that security name is stripped of whitespace."""
        tx = Transaction(**self.base_data, security_name='  Apple Inc  ')
        self.assertEqual(tx.security_name, 'Apple Inc')


class TestTransactionTypeValidation(unittest.TestCase):
    """Test transaction type validation."""

    def setUp(self):
        """Set up minimal valid transaction data."""
        self.base_data = {
            'date': datetime(2024, 1, 15),
            'security_name': 'Apple Inc',
            'security_symbol': 'AAPL',
            'balance': 45000.0,
            'currency': '$'
        }

    def test_valid_transaction_type(self):
        """Test valid transaction types are accepted."""
        valid_types = ['קניה שח', 'מכירה מטח', 'דיבידנד', 'משיכת מס']

        for txn_type in valid_types:
            with self.subTest(transaction_type=txn_type):
                tx = Transaction(**self.base_data, transaction_type=txn_type)
                self.assertEqual(tx.transaction_type, txn_type)

    def test_empty_transaction_type_fails(self):
        """Test that empty transaction type is rejected."""
        with self.assertRaises(ValidationError) as context:
            Transaction(**self.base_data, transaction_type='')

        self.assertIn('Transaction type cannot be empty', str(context.exception))

    def test_whitespace_transaction_type_fails(self):
        """Test that whitespace-only transaction type is rejected."""
        with self.assertRaises(ValidationError) as context:
            Transaction(**self.base_data, transaction_type='   ')

        self.assertIn('Transaction type cannot be empty', str(context.exception))

    def test_transaction_type_stripped(self):
        """Test that transaction type is stripped of whitespace."""
        tx = Transaction(**self.base_data, transaction_type='  קניה שח  ')
        self.assertEqual(tx.transaction_type, 'קניה שח')


class TestTransactionLogicValidation(unittest.TestCase):
    """Test cross-field validation logic."""

    def setUp(self):
        """Set up valid transaction data."""
        self.base_data = {
            'date': datetime(2024, 1, 15),
            'security_name': 'Apple Inc',
            'security_symbol': 'AAPL',
            'balance': 45000.0,
            'currency': '$',
            'bank': 'IBI'
        }

    def test_buy_transaction_with_valid_quantity(self):
        """Test buy transaction with valid quantity is accepted."""
        tx = Transaction(
            **self.base_data,
            transaction_type='קניה שח',
            quantity=10.0,
            execution_price=150.0
        )
        self.assertTrue(tx.is_buy)
        self.assertEqual(tx.quantity, 10.0)

    def test_sell_transaction_with_valid_quantity(self):
        """Test sell transaction with valid quantity is accepted."""
        tx = Transaction(
            **self.base_data,
            transaction_type='מכירה שח',
            quantity=5.0,
            execution_price=160.0
        )
        self.assertTrue(tx.is_sell)
        self.assertEqual(tx.quantity, 5.0)

    def test_dividend_with_zero_quantity(self):
        """Test dividend transaction with zero quantity is accepted."""
        tx = Transaction(
            **self.base_data,
            transaction_type='דיבידנד',
            quantity=0.0,
            execution_price=0.0
        )
        self.assertTrue(tx.is_dividend)
        self.assertEqual(tx.quantity, 0.0)

    def test_tax_with_zero_quantity(self):
        """Test tax transaction with zero quantity is accepted."""
        tx = Transaction(
            **self.base_data,
            transaction_type='משיכת מס',
            quantity=0.0,
            execution_price=0.0
        )
        self.assertTrue(tx.is_tax)
        self.assertEqual(tx.quantity, 0.0)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions."""

    def setUp(self):
        """Set up minimal valid transaction data."""
        self.base_data = {
            'date': datetime(2024, 1, 15),
            'transaction_type': 'קניה שח',
            'security_name': 'Apple Inc',
            'security_symbol': 'AAPL',
            'balance': 45000.0,
            'currency': '$'
        }

    def test_very_large_quantity(self):
        """Test that very large quantity is accepted."""
        tx = Transaction(**self.base_data, quantity=1_000_000.0)
        self.assertEqual(tx.quantity, 1_000_000.0)

    def test_very_small_quantity(self):
        """Test that fractional quantity is accepted."""
        tx = Transaction(**self.base_data, quantity=0.001)
        self.assertEqual(tx.quantity, 0.001)

    def test_very_large_price(self):
        """Test that very large price is accepted."""
        tx = Transaction(**self.base_data, execution_price=1_000_000.0)
        self.assertEqual(tx.execution_price, 1_000_000.0)

    def test_very_small_price(self):
        """Test that fractional price is accepted."""
        tx = Transaction(**self.base_data, execution_price=0.01)
        self.assertEqual(tx.execution_price, 0.01)

    def test_all_zero_amounts(self):
        """Test transaction with all zero amounts."""
        tx = Transaction(
            **self.base_data,
            quantity=0.0,
            execution_price=0.0,
            transaction_fee=0.0,
            additional_fees=0.0,
            amount_foreign_currency=0.0,
            amount_local_currency=0.0
        )
        self.assertEqual(tx.quantity, 0.0)
        self.assertEqual(tx.total_cost, 0.0)


if __name__ == '__main__':
    unittest.main()
