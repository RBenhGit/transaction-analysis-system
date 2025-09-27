#!/usr/bin/env python3
"""
Visual Display using JSON Adapter

This script uses the existing JSON adapter to load your processed transaction files
and display them in the visual interface.
"""

import os
import sys
import glob

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.json_adapter import JSONAdapter
from src.config_manager import ConfigManager
from modules.visual_display import VisualDisplayManager


def find_latest_json_file():
    """Find the most recent JSON file in the output directory."""
    json_pattern = "output/processed/*.json"
    json_files = glob.glob(json_pattern)

    if not json_files:
        return None

    # Sort by modification time, most recent first
    json_files.sort(key=os.path.getmtime, reverse=True)
    return json_files[0]


def main():
    """Load JSON data using the adapter and display it."""
    print("="*60)
    print("JSON DATA VISUAL DISPLAY")
    print("="*60)
    print()

    # Find the latest JSON file
    json_file = find_latest_json_file()

    if not json_file:
        print("Error: No JSON files found in output/processed/ directory")
        print()
        print("To create JSON files:")
        print("1. Run: python main.py")
        print("2. Choose option 1 (Import Excel files)")
        print("3. Import your IBI Excel files")
        print("4. Then run this script again")
        return

    print(f"Loading JSON file: {json_file}")

    try:
        # Use the existing JSON adapter
        config_manager = ConfigManager()
        json_adapter = JSONAdapter(config_manager)

        print("Reading JSON file with adapter...")
        result = json_adapter.import_from_json(json_file)

        if result.success:
            transaction_set = result.transaction_set
            transactions = transaction_set.transactions

            print(f"✓ Successfully loaded {len(transactions)} transactions")
            print()

            # Display summary of REAL data
            print("YOUR REAL TRANSACTION DATA:")
            print("-" * 40)
            print(f"Source: {transaction_set.metadata.source_file}")
            print(f"Bank: {transaction_set.metadata.bank}")
            print(f"Total Transactions: {len(transactions)}")

            # Calculate actual statistics
            if transactions:
                amounts = [tx.amount for tx in transactions if tx.amount is not None]
                if amounts:
                    total_amount = sum(amounts)
                    positive_amounts = [a for a in amounts if a > 0]
                    negative_amounts = [a for a in amounts if a < 0]

                    print(f"Total Amount: ₪{total_amount:,.2f}")
                    if positive_amounts:
                        print(f"Credits: ₪{sum(positive_amounts):,.2f} ({len(positive_amounts)} transactions)")
                    if negative_amounts:
                        print(f"Debits: ₪{sum(negative_amounts):,.2f} ({len(negative_amounts)} transactions)")

                # Date range
                dates = [tx.date for tx in transactions if tx.date]
                if dates:
                    print(f"Date Range: {min(dates)} to {max(dates)}")

            print()
            print("Sample of your transactions:")
            for i, tx in enumerate(transactions[:5]):
                amount_str = f"₪{tx.amount:,.2f}" if tx.amount else "N/A"
                balance_str = f"₪{tx.balance:,.2f}" if tx.balance else "N/A"
                desc = tx.description[:40] + "..." if len(tx.description) > 40 else tx.description
                ref = tx.reference or "N/A"
                print(f"  {i+1}. {tx.date} | {desc:<40} | {amount_str:>12} | Ref: {ref}")

            if len(transactions) > 5:
                print(f"  ... and {len(transactions) - 5} more transactions")

            print()
            print("="*60)
            print("LAUNCHING VISUAL INTERFACE WITH YOUR DATA")
            print("="*60)
            print()
            print("Opening GUI with your REAL transaction data...")
            print("This shows your actual IBI transactions, not mock data!")
            print()
            print("GUI Features with your real data:")
            print("- Sort by any column (Date, Amount, Balance, Reference)")
            print("- Filter by your actual date range")
            print("- Search your real transaction descriptions")
            print("- View statistics of your actual spending patterns")
            print("- Export your real data in various formats")
            print()
            print("The window will stay open until you close it.")

            # Launch visual display
            visual_display = VisualDisplayManager()
            visual_display.run(transaction_set)

            print("\\nGUI session with real data completed!")

        else:
            print("✗ Failed to load JSON file:")
            for error in result.errors:
                print(f"  - {error}")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\\nOperation cancelled by user.")
    except Exception as e:
        print(f"\\nUnexpected error: {e}")