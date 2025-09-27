"""
Unit tests for json_adapter module.
"""

import unittest
import os
import sys
from unittest.mock import patch, MagicMock
import pandas as pd
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'adapters'))

from json_adapter import JSONAdapter
from base_adapter import BaseAdapter


class MockAdapter(BaseAdapter):
    """Mock adapter for testing."""

    def get_column_mappings(self):
        return {
            'date': 'תאריך',
            'description': 'תיאור',
            'amount': 'סכום',
            'balance': 'יתרה'
        }

    def get_bank_name(self):
        return 'TEST_BANK'

    def preprocess_data(self, df):
        return df

    def clean_amount(self, amount):
        if isinstance(amount, str):
            return float(amount.replace(',', ''))
        return float(amount) if amount is not None else 0.0

    def clean_date(self, date_str):
        if isinstance(date_str, str):
            return datetime.strptime(date_str, '%d/%m/%Y').strftime('%Y-%m-%d')
        return date_str


class TestJSONAdapter(unittest.TestCase):
    """Test cases for JSONAdapter class."""

    def setUp(self):
        """Set up test fixtures."""
        self.json_adapter = JSONAdapter()
        self.mock_adapter = MockAdapter()
        self.test_df = pd.DataFrame({
            'תאריך': ['01/01/2024', '02/01/2024'],
            'תיאור': ['Test transaction 1', 'Test transaction 2'],
            'סכום': [100.0, -50.0],
            'יתרה': [1000.0, 950.0]
        })

    def test_init(self):
        """Test JSONAdapter initialization."""
        self.assertIsInstance(self.json_adapter, JSONAdapter)

    def test_process_data(self):
        """Test processing DataFrame to JSON format."""
        result = self.json_adapter.process(self.test_df, self.mock_adapter)

        self.assertIsInstance(result, dict)
        self.assertIn('transactions', result)
        self.assertIn('metadata', result)

        # Check transactions
        transactions = result['transactions']
        self.assertEqual(len(transactions), 2)

        # Check first transaction structure
        first_transaction = transactions[0]
        self.assertIn('date', first_transaction)
        self.assertIn('description', first_transaction)
        self.assertIn('amount', first_transaction)
        self.assertIn('balance', first_transaction)
        self.assertIn('bank', first_transaction)

        # Check metadata
        metadata = result['metadata']
        self.assertIn('total_transactions', metadata)
        self.assertIn('import_date', metadata)
        self.assertIn('date_range', metadata)

    def test_create_transaction_object(self):
        """Test creating individual transaction object."""
        row = self.test_df.iloc[0]
        transaction = self.json_adapter.create_transaction_object(row, self.mock_adapter)

        self.assertIsInstance(transaction, dict)
        self.assertEqual(transaction['bank'], 'TEST_BANK')
        self.assertEqual(transaction['amount'], 100.0)
        self.assertEqual(transaction['description'], 'Test transaction 1')

    def test_create_metadata(self):
        """Test creating metadata object."""
        metadata = self.json_adapter.create_metadata(self.test_df, 'test_file.xlsx')

        self.assertIsInstance(metadata, dict)
        self.assertEqual(metadata['total_transactions'], 2)
        self.assertEqual(metadata['source_file'], 'test_file.xlsx')
        self.assertIn('import_date', metadata)
        self.assertIn('date_range', metadata)

    def test_validate_data_structure(self):
        """Test data structure validation."""
        valid_data = {
            'transactions': [
                {
                    'date': '2024-01-01',
                    'description': 'Test',
                    'amount': 100.0,
                    'balance': 1000.0,
                    'bank': 'TEST_BANK'
                }
            ],
            'metadata': {
                'total_transactions': 1,
                'source_file': 'test.xlsx',
                'import_date': '2024-01-01 12:00:00'
            }
        }

        self.assertTrue(self.json_adapter.validate_structure(valid_data))

    def test_empty_dataframe(self):
        """Test processing empty DataFrame."""
        empty_df = pd.DataFrame()
        result = self.json_adapter.process(empty_df, self.mock_adapter)

        self.assertEqual(len(result['transactions']), 0)
        self.assertEqual(result['metadata']['total_transactions'], 0)

    def test_missing_columns(self):
        """Test handling missing required columns."""
        incomplete_df = pd.DataFrame({
            'תאריך': ['01/01/2024'],
            'תיאור': ['Test transaction']
            # Missing amount and balance columns
        })

        with self.assertRaises(KeyError):
            self.json_adapter.process(incomplete_df, self.mock_adapter)


if __name__ == '__main__':
    unittest.main()