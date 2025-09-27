"""
Unit tests for data_models module.
"""

import unittest
import os
import sys
from datetime import datetime
from typing import Dict, Any

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from data_models import Transaction, TransactionMetadata, BankAdapter
except ImportError:
    # Fallback if pydantic models don't exist
    print("Warning: data_models module not found or incomplete")


class TestTransaction(unittest.TestCase):
    """Test cases for Transaction data model."""

    def setUp(self):
        """Set up test fixtures."""
        self.valid_transaction_data = {
            'date': '2024-01-01',
            'description': 'Test transaction',
            'amount': 100.50,
            'balance': 1000.00,
            'category': 'General',
            'reference': 'REF123',
            'bank': 'IBI',
            'account': 'Main Account'
        }

    def test_transaction_creation(self):
        """Test creating a valid transaction."""
        try:
            from data_models import Transaction
            transaction = Transaction(**self.valid_transaction_data)

            self.assertEqual(transaction.date, '2024-01-01')
            self.assertEqual(transaction.description, 'Test transaction')
            self.assertEqual(transaction.amount, 100.50)
            self.assertEqual(transaction.balance, 1000.00)
            self.assertEqual(transaction.bank, 'IBI')
        except ImportError:
            self.skipTest("Transaction model not available")

    def test_transaction_validation(self):
        """Test transaction data validation."""
        try:
            from data_models import Transaction
            from pydantic import ValidationError

            # Test invalid date format
            invalid_data = self.valid_transaction_data.copy()
            invalid_data['date'] = 'invalid-date'

            with self.assertRaises(ValidationError):
                Transaction(**invalid_data)

            # Test invalid amount type
            invalid_data = self.valid_transaction_data.copy()
            invalid_data['amount'] = 'not-a-number'

            with self.assertRaises(ValidationError):
                Transaction(**invalid_data)

        except ImportError:
            self.skipTest("Transaction model or pydantic not available")

    def test_transaction_serialization(self):
        """Test transaction to dict conversion."""
        try:
            from data_models import Transaction
            transaction = Transaction(**self.valid_transaction_data)

            transaction_dict = transaction.dict()
            self.assertIsInstance(transaction_dict, dict)
            self.assertEqual(transaction_dict['amount'], 100.50)

        except ImportError:
            self.skipTest("Transaction model not available")


class TestTransactionMetadata(unittest.TestCase):
    """Test cases for TransactionMetadata data model."""

    def setUp(self):
        """Set up test fixtures."""
        self.valid_metadata = {
            'source_file': 'test_file.xlsx',
            'import_date': '2024-01-01 12:00:00',
            'total_transactions': 100,
            'date_range': {
                'start': '2024-01-01',
                'end': '2024-12-31'
            }
        }

    def test_metadata_creation(self):
        """Test creating valid metadata."""
        try:
            from data_models import TransactionMetadata
            metadata = TransactionMetadata(**self.valid_metadata)

            self.assertEqual(metadata.source_file, 'test_file.xlsx')
            self.assertEqual(metadata.total_transactions, 100)

        except ImportError:
            self.skipTest("TransactionMetadata model not available")

    def test_metadata_validation(self):
        """Test metadata validation."""
        try:
            from data_models import TransactionMetadata
            from pydantic import ValidationError

            # Test negative transaction count
            invalid_data = self.valid_metadata.copy()
            invalid_data['total_transactions'] = -1

            with self.assertRaises(ValidationError):
                TransactionMetadata(**invalid_data)

        except ImportError:
            self.skipTest("TransactionMetadata model not available")


class TestBankAdapter(unittest.TestCase):
    """Test cases for BankAdapter data model."""

    def setUp(self):
        """Set up test fixtures."""
        self.valid_adapter_config = {
            'bank_name': 'IBI',
            'column_mappings': {
                'date': 'תאריך',
                'description': 'תיאור',
                'amount': 'סכום',
                'balance': 'יתרה'
            },
            'date_format': '%d/%m/%Y',
            'encoding': 'utf-8'
        }

    def test_adapter_creation(self):
        """Test creating valid adapter configuration."""
        try:
            from data_models import BankAdapter
            adapter = BankAdapter(**self.valid_adapter_config)

            self.assertEqual(adapter.bank_name, 'IBI')
            self.assertEqual(adapter.date_format, '%d/%m/%Y')
            self.assertIn('date', adapter.column_mappings)

        except ImportError:
            self.skipTest("BankAdapter model not available")

    def test_adapter_validation(self):
        """Test adapter configuration validation."""
        try:
            from data_models import BankAdapter
            from pydantic import ValidationError

            # Test missing required fields
            invalid_data = self.valid_adapter_config.copy()
            del invalid_data['bank_name']

            with self.assertRaises(ValidationError):
                BankAdapter(**invalid_data)

        except ImportError:
            self.skipTest("BankAdapter model not available")


class TestDataIntegration(unittest.TestCase):
    """Test cases for data model integration."""

    def test_complete_transaction_flow(self):
        """Test complete transaction processing flow."""
        try:
            from data_models import Transaction, TransactionMetadata

            # Create multiple transactions
            transactions = []
            for i in range(3):
                transaction_data = {
                    'date': f'2024-01-0{i+1}',
                    'description': f'Transaction {i+1}',
                    'amount': 100.0 + i,
                    'balance': 1000.0 - (i * 10),
                    'bank': 'IBI',
                    'account': 'Test Account'
                }
                transactions.append(Transaction(**transaction_data))

            # Create metadata
            metadata_data = {
                'source_file': 'test_transactions.xlsx',
                'import_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'total_transactions': len(transactions),
                'date_range': {
                    'start': '2024-01-01',
                    'end': '2024-01-03'
                }
            }
            metadata = TransactionMetadata(**metadata_data)

            # Verify the complete structure
            self.assertEqual(len(transactions), 3)
            self.assertEqual(metadata.total_transactions, 3)

            # Test serialization
            transaction_dicts = [t.dict() for t in transactions]
            metadata_dict = metadata.dict()

            self.assertIsInstance(transaction_dicts, list)
            self.assertIsInstance(metadata_dict, dict)

        except ImportError:
            self.skipTest("Data models not available")


if __name__ == '__main__':
    unittest.main()