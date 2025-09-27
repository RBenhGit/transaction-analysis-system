"""
Example Usage Script for Visual Display Module

This script demonstrates how to use the Visual Display Module to create
graphical interfaces for transaction data visualization and interaction.
"""

import os
import sys
from datetime import date, datetime
from decimal import Decimal

# Add project root to path for imports
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sys.path.append(project_root)

from src.simple_models import Transaction, TransactionSet, TransactionMetadata
from src.excel_importer import ExcelImporter
from src.json_adapter import JSONAdapter
from src.config_manager import ConfigManager
from adapters.ibi_adapter import IBIAdapter
from modules.visual_display import VisualDisplayManager


def create_sample_transaction_data():
    """
    Create sample transaction data for demonstration purposes.

    Returns:
        TransactionSet: Sample transaction data
    """
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
            date=date(2024, 1, 22),
            description="Online Shopping - Amazon",
            amount=Decimal('-89.99'),
            balance=Decimal('22673.26'),
            category="Shopping",
            reference="SHOP001",
            bank="IBI",
            account="12345"
        ),
        Transaction(
            date=date(2024, 1, 25),
            description="Investment Dividend",
            amount=Decimal('450.00'),
            balance=Decimal('23123.26'),
            category="Investment",
            reference="DIV001",
            bank="IBI",
            account="12345"
        ),
        Transaction(
            date=date(2024, 1, 28),
            description="Medical Appointment",
            amount=Decimal('-150.00'),
            balance=Decimal('22973.26'),
            category="Healthcare",
            reference="MED001",
            bank="IBI",
            account="12345"
        ),
        Transaction(
            date=date(2024, 1, 30),
            description="Coffee Shop",
            amount=Decimal('-25.50'),
            balance=Decimal('22947.76'),
            category="Dining",
            reference="CAFE001",
            bank="IBI",
            account="12345"
        ),
        Transaction(
            date=date(2024, 2, 1),
            description="Internet Bill",
            amount=Decimal('-120.00'),
            balance=Decimal('22827.76'),
            category="Utilities",
            reference="NET001",
            bank="IBI",
            account="12345"
        ),
        Transaction(
            date=date(2024, 2, 3),
            description="Gym Membership",
            amount=Decimal('-200.00'),
            balance=Decimal('22627.76'),
            category="Health",
            reference="GYM001",
            bank="IBI",
            account="12345"
        ),
        Transaction(
            date=date(2024, 2, 5),
            description="Salary Payment - February",
            amount=Decimal('15000.00'),
            balance=Decimal('37627.76'),
            category="Income",
            reference="SAL002",
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
            "end": date(2024, 2, 5)
        },
        bank="IBI",
        encoding="utf-8"
    )

    # Create transaction set
    return TransactionSet(
        transactions=transactions,
        metadata=metadata
    )


def example_basic_usage():
    """
    Example 1: Basic visual display usage with sample data.
    """
    print("="*60)
    print("EXAMPLE 1: Basic Visual Display Usage")
    print("="*60)

    # Create sample data
    transaction_set = create_sample_transaction_data()

    print(f"Created sample data with {len(transaction_set.transactions)} transactions")
    print(f"Date range: {transaction_set.metadata.date_range['start']} to {transaction_set.metadata.date_range['end']}")

    # Create visual display manager
    visual_display = VisualDisplayManager()

    print("\\nLaunching visual display interface...")
    print("Features available in the GUI:")
    print("- Sort transactions by clicking column headers")
    print("- Filter by date range, amount, or transaction type")
    print("- Search transaction descriptions")
    print("- View real-time summary statistics")
    print("- Export filtered data to CSV, Excel, or JSON")
    print("- Double-click transactions for detailed view")

    # Show transactions in GUI
    visual_display.show_transactions(transaction_set)

    print("\\nGUI launched! Explore the data using the visual interface.")
    print("Close the window when done exploring.")

    return visual_display


def example_with_real_data():
    """
    Example 2: Using visual display with real imported data.
    """
    print("\\n" + "="*60)
    print("EXAMPLE 2: Visual Display with Real Data")
    print("="*60)

    # Check for real data files
    data_files_dir = os.path.join(project_root, "Data_Files")
    excel_files = []

    if os.path.exists(data_files_dir):
        excel_files = [f for f in os.listdir(data_files_dir) if f.endswith('.xlsx')]

    if not excel_files:
        print("No Excel files found in Data_Files directory.")
        print("Using sample data instead...")
        return example_basic_usage()

    print(f"Found {len(excel_files)} Excel file(s) in Data_Files directory:")
    for i, filename in enumerate(excel_files, 1):
        print(f"  {i}. {filename}")

    # Use the first available file
    selected_file = excel_files[0]
    file_path = os.path.join(data_files_dir, selected_file)

    print(f"\\nImporting data from: {selected_file}")

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

            # Launch visual display
            visual_display = VisualDisplayManager()
            visual_display.show_transactions(result.transaction_set)

            print("\\nReal transaction data loaded in visual interface!")
            return visual_display

        else:
            print("✗ Failed to import data:")
            for error in result.errors:
                print(f"  - {error}")
            return None

    except Exception as e:
        print(f"✗ Error importing data: {e}")
        print("Using sample data instead...")
        return example_basic_usage()


def example_custom_configuration():
    """
    Example 3: Using visual display with custom configuration.
    """
    print("\\n" + "="*60)
    print("EXAMPLE 3: Visual Display with Custom Configuration")
    print("="*60)

    # Create custom configuration
    config_manager = ConfigManager()

    # Customize display settings
    config_manager.display_config.update({
        "max_rows": 500,  # Show more rows by default
        "date_format": "DD/MM/YYYY"  # Different date format
    })

    print("Custom configuration applied:")
    print(f"- Max rows: {config_manager.display_config['max_rows']}")
    print(f"- Date format: {config_manager.display_config['date_format']}")

    # Create sample data
    transaction_set = create_sample_transaction_data()

    # Create visual display with custom config
    visual_display = VisualDisplayManager(config_manager)
    visual_display.show_transactions(transaction_set)

    print("\\nVisual display launched with custom configuration!")
    return visual_display


def example_programmatic_filtering():
    """
    Example 4: Demonstrate programmatic filtering capabilities.
    """
    print("\\n" + "="*60)
    print("EXAMPLE 4: Programmatic Filtering Example")
    print("="*60)

    from modules.visual_display.utils import (
        apply_transaction_filter,
        create_filter_query,
        calculate_summary_stats
    )

    # Create sample data
    transaction_set = create_sample_transaction_data()
    transactions = transaction_set.transactions

    print(f"Starting with {len(transactions)} transactions")

    # Example filter 1: Income transactions only
    filter_query = create_filter_query(transaction_type="Credits")
    income_transactions = apply_transaction_filter(transactions, filter_query)

    print(f"\\nIncome transactions: {len(income_transactions)}")
    for trans in income_transactions:
        print(f"  {trans.date}: {trans.description} - {trans.amount}")

    # Example filter 2: Large expenses (> ₪1000)
    filter_query = create_filter_query(
        min_amount=Decimal('1000.00'),
        transaction_type="Debits"
    )
    large_expenses = apply_transaction_filter(transactions, filter_query)

    print(f"\\nLarge expenses (> ₪1000): {len(large_expenses)}")
    for trans in large_expenses:
        print(f"  {trans.date}: {trans.description} - {trans.amount}")

    # Example filter 3: January 2024 transactions
    filter_query = create_filter_query(
        start_date=date(2024, 1, 1),
        end_date=date(2024, 1, 31)
    )
    january_transactions = apply_transaction_filter(transactions, filter_query)

    print(f"\\nJanuary 2024 transactions: {len(january_transactions)}")

    # Calculate summary statistics
    stats = calculate_summary_stats(january_transactions)
    print(f"January summary:")
    print(f"  Total amount: ₪{stats['total_amount']}")
    print(f"  Credits: ₪{stats['total_credits']} ({stats['credit_count']} transactions)")
    print(f"  Debits: ₪{stats['total_debits']} ({stats['debit_count']} transactions)")

    # Launch visual display
    visual_display = VisualDisplayManager()
    visual_display.show_transactions(transaction_set)

    print("\\nVisual display launched - try applying similar filters in the GUI!")
    return visual_display


def example_export_functionality():
    """
    Example 5: Demonstrate export functionality.
    """
    print("\\n" + "="*60)
    print("EXAMPLE 5: Export Functionality Example")
    print("="*60)

    # Create sample data
    transaction_set = create_sample_transaction_data()

    # Create visual display
    visual_display = VisualDisplayManager()

    print("Features to try in the GUI:")
    print("1. Apply filters to narrow down data")
    print("2. Use File menu or toolbar buttons to export:")
    print("   - Export to CSV for spreadsheet analysis")
    print("   - Export to Excel with summary sheet")
    print("   - Export to JSON for data interchange")
    print("3. File dialogs will let you choose save location")
    print("4. Only filtered data will be exported")

    # Show transactions
    visual_display.show_transactions(transaction_set)

    print("\\nGUI launched - try the export features!")
    return visual_display


def main():
    """
    Main function to run all examples.
    """
    print("Visual Display Module - Example Usage")
    print("="*60)
    print("This script demonstrates various ways to use the Visual Display Module")
    print("for transaction data visualization and interaction.")
    print()

    examples = {
        "1": ("Basic Usage with Sample Data", example_basic_usage),
        "2": ("Real Data Import and Display", example_with_real_data),
        "3": ("Custom Configuration", example_custom_configuration),
        "4": ("Programmatic Filtering", example_programmatic_filtering),
        "5": ("Export Functionality", example_export_functionality),
        "a": ("Run All Examples", None)
    }

    while True:
        print("\\nAvailable Examples:")
        for key, (title, _) in examples.items():
            print(f"  {key}. {title}")
        print("  q. Quit")

        choice = input("\\nSelect example to run (1-5, a, q): ").strip().lower()

        if choice == 'q':
            print("\\nGoodbye!")
            break
        elif choice == 'a':
            print("\\nRunning all examples...")
            for key in ["1", "2", "3", "4", "5"]:
                if key in examples and examples[key][1]:
                    print(f"\\n>>> Running Example {key}")
                    examples[key][1]()
                    input("\\nPress Enter to continue to next example...")
        elif choice in examples and examples[choice][1]:
            examples[choice][1]()
            input("\\nPress Enter to continue...")
        else:
            print("Invalid choice. Please try again.")

    print("\\nExample session completed!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\\n\\nExample session interrupted by user.")
    except Exception as e:
        print(f"\\n\\nError running examples: {e}")
        print("Please ensure all required modules are available and try again.")