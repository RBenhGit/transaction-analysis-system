"""
Unit tests for the Visual Display Module core functionality.

Tests the VisualDisplayManager class and its methods for GUI operations,
filtering, and integration with transaction data.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import date, datetime
from decimal import Decimal
import tkinter as tk
from tkinter import ttk

# Import modules for testing
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from src.simple_models import Transaction, TransactionSet, TransactionMetadata
from modules.visual_display.core_module import VisualDisplayManager
from modules.visual_display.utils import (
    format_currency,
    format_date_display,
    get_amount_color,
    calculate_summary_stats,
    apply_transaction_filter,
    create_filter_query
)


class TestVisualDisplayManager(unittest.TestCase):
    """Test cases for VisualDisplayManager class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create sample transaction data
        self.sample_transactions = [
            Transaction(
                date=date(2024, 1, 15),
                description="Salary Payment",
                amount=Decimal('5000.00'),
                balance=Decimal('15000.00'),
                category="Income",
                reference="SAL001",
                bank="IBI",
                account="12345"
            ),
            Transaction(
                date=date(2024, 1, 20),
                description="Grocery Store",
                amount=Decimal('-150.50'),
                balance=Decimal('14849.50'),
                category="Groceries",
                reference="GRO001",
                bank="IBI",
                account="12345"
            ),
            Transaction(
                date=date(2024, 1, 25),
                description="Rent Payment",
                amount=Decimal('-3000.00'),
                balance=Decimal('11849.50'),
                category="Housing",
                reference="RENT001",
                bank="IBI",
                account="12345"
            ),
            Transaction(
                date=date(2024, 2, 1),
                description="Freelance Work",
                amount=Decimal('1200.00'),
                balance=Decimal('13049.50'),
                category="Income",
                reference="FREE001",
                bank="IBI",
                account="12345"
            )
        ]

        # Create sample metadata
        self.sample_metadata = TransactionMetadata(
            source_file="test_file.xlsx",
            import_date=datetime(2024, 2, 1, 10, 30, 0),
            total_transactions=4,
            date_range={"start": date(2024, 1, 15), "end": date(2024, 2, 1)},
            bank="IBI"
        )

        # Create transaction set
        self.transaction_set = TransactionSet(
            transactions=self.sample_transactions,
            metadata=self.sample_metadata
        )

    @patch('tkinter.Tk')
    def test_visual_display_manager_initialization(self, mock_tk):
        """Test VisualDisplayManager initialization."""
        # Mock the Tk instance
        mock_root = Mock()
        mock_tk.return_value = mock_root

        display_manager = VisualDisplayManager()

        self.assertIsNotNone(display_manager)
        self.assertIsNone(display_manager.root)
        self.assertIsNone(display_manager.current_transaction_set)
        self.assertEqual(display_manager.filtered_transactions, [])

    @patch('tkinter.Tk')
    @patch('tkinter.ttk.Style')
    def test_create_main_window(self, mock_style, mock_tk):
        """Test main window creation."""
        # Mock the Tk instance and its methods
        mock_root = Mock()
        mock_tk.return_value = mock_root

        display_manager = VisualDisplayManager()
        display_manager._create_main_window()

        # Verify Tk was called
        mock_tk.assert_called_once()
        self.assertIsNotNone(display_manager.root)

        # Verify window configuration calls
        mock_root.title.assert_called_with("Transaction Analysis - Visual Display")
        mock_root.geometry.assert_called_with("1200x800")
        mock_root.minsize.assert_called_with(800, 600)

    def test_filter_functionality_without_gui(self):
        """Test filtering functionality without GUI components."""
        display_manager = VisualDisplayManager()
        display_manager.current_transaction_set = self.transaction_set
        display_manager.filtered_transactions = self.sample_transactions.copy()

        # Mock filter variables
        display_manager.search_var = Mock()
        display_manager.search_var.get.return_value = "salary"

        display_manager.start_date_var = Mock()
        display_manager.start_date_var.get.return_value = ""

        display_manager.end_date_var = Mock()
        display_manager.end_date_var.get.return_value = ""

        display_manager.min_amount_var = Mock()
        display_manager.min_amount_var.get.return_value = ""

        display_manager.max_amount_var = Mock()
        display_manager.max_amount_var.get.return_value = ""

        display_manager.type_var = Mock()
        display_manager.type_var.get.return_value = "All"

        # Mock GUI update methods
        display_manager._populate_transaction_tree = Mock()
        display_manager._update_summary_panel = Mock()

        # Apply filters
        display_manager._apply_filters()

        # Should find 1 transaction matching "salary"
        self.assertEqual(len(display_manager.filtered_transactions), 1)
        self.assertEqual(display_manager.filtered_transactions[0].description, "Salary Payment")

    def test_clear_filters_functionality(self):
        """Test clearing filters functionality."""
        display_manager = VisualDisplayManager()
        display_manager.current_transaction_set = self.transaction_set

        # Mock filter variables
        display_manager.search_var = Mock()
        display_manager.start_date_var = Mock()
        display_manager.end_date_var = Mock()
        display_manager.min_amount_var = Mock()
        display_manager.max_amount_var = Mock()
        display_manager.type_var = Mock()

        # Mock GUI update methods
        display_manager._populate_transaction_tree = Mock()
        display_manager._update_summary_panel = Mock()

        # Clear filters
        display_manager._clear_filters()

        # Verify all filter variables were cleared
        display_manager.search_var.set.assert_called_with("")
        display_manager.start_date_var.set.assert_called_with("")
        display_manager.end_date_var.set.assert_called_with("")
        display_manager.min_amount_var.set.assert_called_with("")
        display_manager.max_amount_var.set.assert_called_with("")
        display_manager.type_var.set.assert_called_with("All")

        # Should restore all transactions
        self.assertEqual(len(display_manager.filtered_transactions), 4)

    @patch('modules.visual_display.core_module.messagebox')
    def test_export_functionality_mock(self, mock_messagebox):
        """Test export functionality with mocked components."""
        display_manager = VisualDisplayManager()
        display_manager.current_transaction_set = self.transaction_set
        display_manager.filtered_transactions = self.sample_transactions.copy()

        # Mock display manager export method
        display_manager.display_manager = Mock()
        display_manager.display_manager.export_to_csv.return_value = "test_export.csv"

        # Mock file dialog
        with patch('modules.visual_display.core_module.filedialog') as mock_dialog:
            mock_dialog.asksaveasfilename.return_value = "test_export.csv"

            # Test CSV export
            display_manager._export_csv()

            # Verify export method was called
            display_manager.display_manager.export_to_csv.assert_called_once()
            mock_messagebox.showinfo.assert_called_once()

    def test_sort_functionality(self):
        """Test transaction sorting functionality."""
        display_manager = VisualDisplayManager()
        display_manager.filtered_transactions = self.sample_transactions.copy()

        # Mock GUI update method
        display_manager._populate_transaction_tree = Mock()

        # Test sorting by date
        display_manager._sort_by_column("Date")
        dates = [t.date for t in display_manager.filtered_transactions]
        self.assertEqual(dates, sorted(dates))

        # Test sorting by amount
        display_manager._sort_by_column("Amount")
        amounts = [t.amount for t in display_manager.filtered_transactions]
        self.assertEqual(amounts, sorted(amounts))


class TestUtilityFunctions(unittest.TestCase):
    """Test cases for utility functions."""

    def test_format_currency(self):
        """Test currency formatting function."""
        # Test positive amount
        result = format_currency(Decimal('1234.56'))
        self.assertEqual(result, "₪1,234.56")

        # Test negative amount
        result = format_currency(Decimal('-567.89'))
        self.assertEqual(result, "₪-567.89")

        # Test None
        result = format_currency(None)
        self.assertEqual(result, "")

        # Test zero
        result = format_currency(Decimal('0.00'))
        self.assertEqual(result, "₪0.00")

        # Test with custom currency symbol
        result = format_currency(Decimal('100.00'), "$")
        self.assertEqual(result, "$100.00")

    def test_format_date_display(self):
        """Test date formatting function."""
        # Test valid date
        test_date = date(2024, 1, 15)
        result = format_date_display(test_date)
        self.assertEqual(result, "2024-01-15")

        # Test None
        result = format_date_display(None)
        self.assertEqual(result, "")

    def test_get_amount_color(self):
        """Test amount color coding function."""
        # Test positive amount
        result = get_amount_color(Decimal('100.00'))
        self.assertEqual(result, "green")

        # Test negative amount
        result = get_amount_color(Decimal('-100.00'))
        self.assertEqual(result, "red")

        # Test zero amount
        result = get_amount_color(Decimal('0.00'))
        self.assertIsNone(result)

        # Test None
        result = get_amount_color(None)
        self.assertIsNone(result)

    def test_calculate_summary_stats(self):
        """Test summary statistics calculation."""
        # Create test transactions
        transactions = [
            Transaction(
                date=date(2024, 1, 1),
                description="Test 1",
                amount=Decimal('100.00'),
                balance=Decimal('1000.00'),
                category=None,
                reference=None,
                bank="Test",
                account=None
            ),
            Transaction(
                date=date(2024, 1, 2),
                description="Test 2",
                amount=Decimal('-50.00'),
                balance=Decimal('950.00'),
                category=None,
                reference=None,
                bank="Test",
                account=None
            ),
            Transaction(
                date=date(2024, 1, 3),
                description="Test 3",
                amount=Decimal('200.00'),
                balance=Decimal('1150.00'),
                category=None,
                reference=None,
                bank="Test",
                account=None
            )
        ]

        stats = calculate_summary_stats(transactions)

        self.assertEqual(stats['count'], 3)
        self.assertEqual(stats['total_amount'], Decimal('250.00'))
        self.assertEqual(stats['total_credits'], Decimal('300.00'))
        self.assertEqual(stats['total_debits'], Decimal('-50.00'))
        self.assertEqual(stats['credit_count'], 2)
        self.assertEqual(stats['debit_count'], 1)
        self.assertEqual(stats['average_amount'], Decimal('250.00') / 3)

        # Test date range
        date_range = stats['date_range']
        self.assertEqual(date_range['start'], date(2024, 1, 1))
        self.assertEqual(date_range['end'], date(2024, 1, 3))

    def test_calculate_summary_stats_empty(self):
        """Test summary statistics with empty transaction list."""
        stats = calculate_summary_stats([])

        self.assertEqual(stats['count'], 0)
        self.assertEqual(stats['total_amount'], Decimal('0'))
        self.assertEqual(stats['total_credits'], Decimal('0'))
        self.assertEqual(stats['total_debits'], Decimal('0'))
        self.assertEqual(stats['credit_count'], 0)
        self.assertEqual(stats['debit_count'], 0)
        self.assertEqual(stats['average_amount'], Decimal('0'))
        self.assertIsNone(stats['date_range'])

    def test_create_filter_query(self):
        """Test filter query creation."""
        query = create_filter_query(
            search_text="salary",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
            min_amount=Decimal('100.00'),
            transaction_type="Credits"
        )

        expected = {
            "search_text": "salary",
            "start_date": date(2024, 1, 1),
            "end_date": date(2024, 1, 31),
            "min_amount": Decimal('100.00'),
            "transaction_type": "Credits"
        }

        self.assertEqual(query, expected)

        # Test with empty/None values
        query = create_filter_query(
            search_text="",
            start_date=None,
            transaction_type="All"
        )

        self.assertEqual(query, {})

    def test_apply_transaction_filter(self):
        """Test transaction filtering functionality."""
        # Create test transactions
        transactions = [
            Transaction(
                date=date(2024, 1, 15),
                description="Salary Payment",
                amount=Decimal('5000.00'),
                balance=Decimal('10000.00'),
                category=None,
                reference=None,
                bank="Test",
                account=None
            ),
            Transaction(
                date=date(2024, 1, 20),
                description="Grocery Store",
                amount=Decimal('-150.00'),
                balance=Decimal('9850.00'),
                category=None,
                reference=None,
                bank="Test",
                account=None
            ),
            Transaction(
                date=date(2024, 2, 1),
                description="Freelance Work",
                amount=Decimal('1200.00'),
                balance=Decimal('11050.00'),
                category=None,
                reference=None,
                bank="Test",
                account=None
            )
        ]

        # Test text search filter
        filter_query = {"search_text": "salary"}
        filtered = apply_transaction_filter(transactions, filter_query)
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0].description, "Salary Payment")

        # Test date range filter
        filter_query = {
            "start_date": date(2024, 1, 1),
            "end_date": date(2024, 1, 31)
        }
        filtered = apply_transaction_filter(transactions, filter_query)
        self.assertEqual(len(filtered), 2)  # Salary and Grocery

        # Test amount filter
        filter_query = {"min_amount": Decimal('1000.00')}
        filtered = apply_transaction_filter(transactions, filter_query)
        self.assertEqual(len(filtered), 2)  # Salary and Freelance

        # Test transaction type filter
        filter_query = {"transaction_type": "Credits"}
        filtered = apply_transaction_filter(transactions, filter_query)
        self.assertEqual(len(filtered), 2)  # Salary and Freelance

        filter_query = {"transaction_type": "Debits"}
        filtered = apply_transaction_filter(transactions, filter_query)
        self.assertEqual(len(filtered), 1)  # Grocery only

        # Test combined filters
        filter_query = {
            "search_text": "work",
            "transaction_type": "Credits",
            "min_amount": Decimal('1000.00')
        }
        filtered = apply_transaction_filter(transactions, filter_query)
        self.assertEqual(len(filtered), 1)  # Freelance only


class TestErrorHandling(unittest.TestCase):
    """Test error handling scenarios."""

    def test_invalid_filter_values(self):
        """Test handling of invalid filter values."""
        display_manager = VisualDisplayManager()

        # Mock filter variables with invalid data
        display_manager.search_var = Mock()
        display_manager.search_var.get.return_value = "valid_search"

        display_manager.start_date_var = Mock()
        display_manager.start_date_var.get.return_value = "invalid_date"

        display_manager.end_date_var = Mock()
        display_manager.end_date_var.get.return_value = ""

        display_manager.min_amount_var = Mock()
        display_manager.min_amount_var.get.return_value = "not_a_number"

        display_manager.max_amount_var = Mock()
        display_manager.max_amount_var.get.return_value = ""

        display_manager.type_var = Mock()
        display_manager.type_var.get.return_value = "All"

        # Mock transaction data
        display_manager.current_transaction_set = TransactionSet(
            transactions=[],
            metadata=TransactionMetadata(
                source_file="test.xlsx",
                total_transactions=0,
                date_range={"start": None, "end": None},
                bank="Test"
            )
        )

        # Mock GUI update methods
        display_manager._populate_transaction_tree = Mock()
        display_manager._update_summary_panel = Mock()

        # Should not raise exception despite invalid inputs
        try:
            display_manager._apply_filters()
        except Exception as e:
            self.fail(f"_apply_filters() raised {e} unexpectedly!")

    @patch('modules.visual_display.core_module.messagebox')
    def test_export_error_handling(self, mock_messagebox):
        """Test export error handling."""
        display_manager = VisualDisplayManager()
        display_manager.filtered_transactions = []

        # Test export with no data
        display_manager._export_csv()
        mock_messagebox.showwarning.assert_called_with("No Data", "No transactions to export.")

        # Reset mock
        mock_messagebox.reset_mock()

        # Test export with data but file dialog cancelled
        display_manager.filtered_transactions = [Mock()]
        with patch('modules.visual_display.core_module.filedialog') as mock_dialog:
            mock_dialog.asksaveasfilename.return_value = ""  # User cancelled

            display_manager._export_csv()

            # Should not call export or show messages if cancelled
            mock_messagebox.showinfo.assert_not_called()
            mock_messagebox.showerror.assert_not_called()


if __name__ == '__main__':
    unittest.main()