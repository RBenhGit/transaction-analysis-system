#!/usr/bin/env python3
"""
Visual Display with Real Transaction Data

This script loads your actual IBI transaction data from JSON files
and displays it in the visual interface.
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
    """Find the most recent JSON file."""
    json_pattern = "output/processed/*.json"
    json_files = glob.glob(json_pattern)

    if not json_files:
        return None

    # Sort by modification time, most recent first
    json_files.sort(key=os.path.getmtime, reverse=True)
    return json_files[0]


def main():
    """Load and display real transaction data."""
    print("Real Transaction Data Visual Display")
    print("=" * 40)

    # Find JSON file
    json_file = find_latest_json_file()

    if not json_file:
        print("No JSON files found in output/processed/")
        print("Run the main application to import Excel files first.")
        return

    print(f"Loading: {os.path.basename(json_file)}")

    # Load data using JSON adapter
    config_manager = ConfigManager()
    json_adapter = JSONAdapter(config_manager)

    result = json_adapter.import_from_json(json_file)

    if result.success:
        transaction_set = result.transaction_set
        transactions = transaction_set.transactions

        print(f"Loaded {len(transactions)} real transactions")
        print(f"Source: {transaction_set.metadata.source_file}")
        print(f"Date range: {transaction_set.metadata.date_range}")

        # Calculate real statistics
        amounts = [tx.amount for tx in transactions if tx.amount is not None]
        if amounts:
            total = sum(amounts)
            credits = [a for a in amounts if a > 0]
            debits = [a for a in amounts if a < 0]

            print(f"Total amount: {total:.2f}")
            print(f"Credits: {len(credits)} transactions")
            print(f"Debits: {len(debits)} transactions")

        print()
        print("Opening GUI with your REAL data...")
        print("The window will stay open until you close it.")

        # Launch visual display
        visual_display = VisualDisplayManager()
        visual_display.run(transaction_set)

        print("GUI session completed.")

    else:
        print("Failed to load JSON data:")
        for error in result.errors:
            print(f"  - {error}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")