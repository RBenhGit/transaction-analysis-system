#!/usr/bin/env python3
"""
Visual Display Module Demo - Simple Version

This script demonstrates the visual display module with sample data.
"""

import os
import sys
from datetime import date, datetime
from decimal import Decimal

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.simple_models import Transaction, TransactionSet, TransactionMetadata
from modules.visual_display import VisualDisplayManager


def main():
    """Demo the visual display with sample data."""
    print("Visual Display Module Demo")
    print("=" * 40)

    # Create sample transactions
    transactions = [
        Transaction(
            date=date(2024, 1, 5),
            description="Salary Payment",
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
            description="Grocery Shopping",
            amount=Decimal('-350.75'),
            balance=Decimal('20149.25'),
            category="Groceries",
            reference="GRO001",
            bank="IBI",
            account="12345"
        ),
        Transaction(
            date=date(2024, 1, 15),
            description="Freelance Payment",
            amount=Decimal('3200.00'),
            balance=Decimal('23349.25'),
            category="Income",
            reference="FREE001",
            bank="IBI",
            account="12345"
        ),
        Transaction(
            date=date(2024, 1, 20),
            description="Restaurant Dinner",
            amount=Decimal('-125.50'),
            balance=Decimal('23223.75'),
            category="Dining",
            reference="REST001",
            bank="IBI",
            account="12345"
        )
    ]

    # Create metadata
    metadata = TransactionMetadata(
        source_file="demo_data.xlsx",
        import_date=datetime.now(),
        total_transactions=len(transactions),
        date_range={
            "start": date(2024, 1, 5),
            "end": date(2024, 1, 20)
        },
        bank="IBI",
        encoding="utf-8"
    )

    # Create transaction set
    transaction_set = TransactionSet(transactions=transactions, metadata=metadata)

    print(f"Sample data created: {len(transactions)} transactions")
    print("Date range: 2024-01-05 to 2024-01-20")
    print()
    print("Launching Visual Display...")
    print()
    print("GUI Features to try:")
    print("- Click column headers to sort")
    print("- Use filters on the left panel")
    print("- Search in the toolbar")
    print("- Double-click rows for details")
    print("- Export via File menu")
    print()

    # Create and show visual display
    visual_display = VisualDisplayManager()

    print("Starting GUI - window should open now...")
    print("The script will wait until you close the GUI window.")

    # This will open the window and keep it open until user closes it
    visual_display.run(transaction_set)

    print("GUI window was closed. Demo completed!")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        print("Check that all modules are properly installed.")