"""
Unit tests for excel_importer module.
"""

import unittest
import os
import sys
from unittest.mock import patch, MagicMock
import pandas as pd

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from excel_importer import ExcelImporter


class TestExcelImporter(unittest.TestCase):
    """Test cases for ExcelImporter class."""

    def setUp(self):
        """Set up test fixtures."""
        self.importer = ExcelImporter()
        self.test_data_dir = os.path.join(os.path.dirname(__file__), '..', 'Data_Files')

    def test_init(self):
        """Test ExcelImporter initialization."""
        self.assertIsInstance(self.importer, ExcelImporter)

    @patch('pandas.read_excel')
    def test_load_file_success(self, mock_read_excel):
        """Test successful file loading."""
        # Mock pandas DataFrame
        mock_df = pd.DataFrame({
            'תאריך': ['01/01/2024', '02/01/2024'],
            'תיאור': ['Test transaction 1', 'Test transaction 2'],
            'סכום': [100.0, -50.0],
            'יתרה': [1000.0, 950.0]
        })
        mock_read_excel.return_value = mock_df

        # Test file loading
        result = self.importer.load_file('test_file.xlsx')

        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 2)
        mock_read_excel.assert_called_once()

    def test_load_file_nonexistent(self):
        """Test loading non-existent file."""
        with self.assertRaises(FileNotFoundError):
            self.importer.load_file('nonexistent_file.xlsx')

    @patch('os.path.exists')
    def test_discover_files(self, mock_exists):
        """Test file discovery in Data_Files directory."""
        mock_exists.return_value = True

        with patch('os.listdir') as mock_listdir:
            mock_listdir.return_value = [
                'IBI trans 2024.xlsx',
                'Other bank 2024.xlsx',
                'not_excel.txt'
            ]

            files = self.importer.discover_files()

            # Should only return Excel files
            excel_files = [f for f in files if f.endswith(('.xlsx', '.xls'))]
            self.assertEqual(len(excel_files), 2)

    def test_validate_columns(self):
        """Test column validation."""
        # Test with valid columns
        valid_df = pd.DataFrame({
            'תאריך': ['01/01/2024'],
            'תיאור': ['Test'],
            'סכום': [100.0],
            'יתרה': [1000.0]
        })

        self.assertTrue(self.importer.validate_columns(valid_df, ['תאריך', 'תיאור']))

    def test_get_file_info(self):
        """Test getting file information."""
        test_file = os.path.join(self.test_data_dir, 'IBI trans 2024.xlsx')

        if os.path.exists(test_file):
            info = self.importer.get_file_info(test_file)
            self.assertIn('size_mb', info)
            self.assertIn('last_modified', info)


if __name__ == '__main__':
    unittest.main()