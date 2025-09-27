#!/usr/bin/env python3
"""
Simple script to run the Visual Display Module

This script demonstrates how to use the visual display module with
either sample data or real transaction data from Excel files.
"""

import os
import sys
from datetime import date, datetime
from decimal import Decimal

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.simple_models import Transaction, TransactionSet, TransactionMetadata
from src.excel_importer import ExcelImporter
from src.json_adapter import JSONAdapter
from adapters.ibi_adapter import IBIAdapter
from modules.visual_display import VisualDisplayManager


def create_sample_data():
    """Create sample transaction data for demonstration."""
    print("Creating sample transaction data...")

    # Create sample transactions
    transactions = [
        Transaction(
            date=date(2024, 1, 1),
            description="Opening Balance",
            amount=Decimal('10000.00'),
            balance=Decimal('10000.00'),
            category="Transfer",
            reference="OPEN001",
            bank="IBI",
            account="12345"
        ),
        Transaction(
            date=date(2024, 1, 5),
            description="Salary Payment - January",
            amount=Decimal('15000.00'),
            balance=Decimal('25000.00'),
            category="Income",
            reference="SAL001",
            bank="IBI",
            account="12345"
        ),
        Transaction(
            date=date(2024, 1, 8),
            description="Rent Payment",
            amount=Decimal('-4500.00'),
            balance=Decimal('20500.00'),
            category="Housing",
            reference="RENT001",
            bank="IBI",
            account="12345"
        ),
        Transaction(
            date=date(2024, 1, 10),
            description="Grocery Shopping - Super-Pharm",
            amount=Decimal('-350.75'),
            balance=Decimal('20149.25'),
            category="Groceries",
            reference="GRO001",
            bank="IBI",
            account="12345"
        ),
        Transaction(
            date=date(2024, 1, 12),
            description="Electricity Bill",
            amount=Decimal('-280.50'),
            balance=Decimal('19868.75'),
            category="Utilities",
            reference="ELEC001",
            bank="IBI",
            account="12345"
        ),
        Transaction(
            date=date(2024, 1, 15),
            description="Freelance Project Payment",
            amount=Decimal('3200.00'),
            balance=Decimal('23068.75'),
            category="Income",
            reference="FREE001",
            bank="IBI",
            account="12345"
        ),
        Transaction(
            date=date(2024, 1, 18),
            description="Gas Station - Delek",
            amount=Decimal('-180.00'),
            balance=Decimal('22888.75'),
            category="Transportation",
            reference="GAS001",
            bank="IBI",
            account="12345"
        ),
        Transaction(
            date=date(2024, 1, 20),
            description="Restaurant - Dinner",
            amount=Decimal('-125.50'),
            balance=Decimal('22763.25'),
            category="Dining",
            reference="REST001",
            bank="IBI",
            account="12345"
        ),
        Transaction(
            date=date(2024, 1, 25),
            description="Investment Dividend",
            amount=Decimal('450.00'),
            balance=Decimal('23213.25'),
            category="Investment",
            reference="DIV001",
            bank="IBI",
            account="12345"
        ),
        Transaction(
            date=date(2024, 2, 1),
            description="Internet Bill",
            amount=Decimal('-120.00'),
            balance=Decimal('23093.25'),
            category="Utilities",
            reference="NET001",
            bank="IBI",
            account="12345"
        )
    ]

    # Create metadata
    metadata = TransactionMetadata(
        source_file="sample_transactions.xlsx",
        import_date=datetime.now(),
        total_transactions=len(transactions),
        date_range={
            "start": date(2024, 1, 1),
            "end": date(2024, 2, 1)
        },
        bank="IBI",
        encoding="utf-8"
    )

    return TransactionSet(transactions=transactions, metadata=metadata)


def try_real_data():
    """Try to load real transaction data from Excel files."""
    data_files_dir = "Data_Files"

    if not os.path.exists(data_files_dir):
        print(f"No {data_files_dir} directory found.")
        return None

    excel_files = [f for f in os.listdir(data_files_dir) if f.endswith('.xlsx')]

    if not excel_files:
        print(f"No Excel files found in {data_files_dir} directory.")
        return None

    # Use the most recent IBI file
    ibi_files = [f for f in excel_files if 'IBI' in f]
    if ibi_files:
        selected_file = sorted(ibi_files)[-1]  # Get the latest year
    else:
        selected_file = excel_files[0]

    file_path = os.path.join(data_files_dir, selected_file)

    print(f"Attempting to load real data from: {selected_file}")

    try:
        # Import and process data
        importer = ExcelImporter()
        adapter = JSONAdapter()
        ibi_adapter = IBIAdapter()

        print("Loading Excel file...")
        raw_data = importer.load_file(file_path)

        print("Processing data through JSON adapter...")
        result = adapter.process(raw_data, ibi_adapter)

        if result.success:
            print(f"✓ Successfully imported {len(result.transaction_set.transactions)} transactions")
            return result.transaction_set
        else:
            print("✗ Failed to import data:")
            for error in result.errors:
                print(f"  - {error}")
            return None

    except Exception as e:
        print(f"✗ Error importing data: {e}")
        return None


def main():
    """Main function to run the visual display."""
    print("="*60)
    print("VISUAL DISPLAY MODULE DEMO")
    print("="*60)
    print()

    # Try to load real data first
    transaction_set = try_real_data()

    # Fall back to sample data if real data loading fails
    if transaction_set is None:
        print("Using sample transaction data instead...")
        transaction_set = create_sample_data()

    print(f"\\nLoaded {len(transaction_set.transactions)} transactions")
    print(f"Date range: {transaction_set.metadata.date_range['start']} to {transaction_set.metadata.date_range['end']}")
    print(f"Bank: {transaction_set.metadata.bank}")

    # Create and launch visual display
    print("\\n" + "="*60)
    print("LAUNCHING VISUAL DISPLAY")
    print("="*60)
    print()
    print("Creating Visual Display Manager...")

    visual_display = VisualDisplayManager()

    print("✓ Visual Display Manager created successfully!")
    print()
    print("FEATURES TO TRY IN THE GUI:")
    print("- Sort transactions by clicking column headers")
    print("- Filter by date range (YYYY-MM-DD format)")
    print("- Filter by amount range")
    print("- Search transaction descriptions")
    print("- View real-time summary statistics")
    print("- Export filtered data (File menu or toolbar)")
    print("- Double-click transactions for detailed view")
    print()
    print("Launching GUI window...")

    print("\\n" + "="*60)
    print("STARTING GUI")
    print("="*60)
    print()
    print("GUI window should open now...")
    print("The script will wait until you close the GUI window.")
    print()

    # Show transactions in GUI and keep it open
    visual_display.run(transaction_set)

    print("\\n" + "="*60)
    print("SESSION COMPLETED")
    print("="*60)
    print()
    print("GUI window was closed.")
    print("To run this again, use: python run_visual_display.py")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\\n\\nProcess interrupted by user.")
    except Exception as e:
        print(f"\\n\\nError: {e}")
        print("Make sure all required modules are installed and try again.")