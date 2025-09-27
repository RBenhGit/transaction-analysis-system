#!/usr/bin/env python3
"""
Direct test of IBI adapter without auto-detection
"""

import os
import sys
import pandas as pd

# Add the project root to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.excel_importer import ExcelImporter
from src.config_manager import ConfigManager

def main():
    print("Testing IBI adapter directly...")

    # Initialize components
    config_manager = ConfigManager()
    excel_importer = ExcelImporter(config_manager)

    # Get first IBI file
    files = excel_importer.discover_files()
    if not files:
        print("No files found!")
        return

    test_file = files[0]['path']
    print(f"Testing file: {files[0]['filename']}")

    # Load Excel file directly to inspect structure
    print("\nLoading Excel file...")
    try:
        df = pd.read_excel(test_file, header=None)
        print(f"Shape: {df.shape}")

        # Look for Hebrew column headers
        print("\nLooking for potential header rows...")
        for i in range(min(10, len(df))):
            row_values = []
            for val in df.iloc[i]:
                if pd.notna(val):
                    val_str = str(val)
                    # Check if it contains Hebrew or relevant keywords
                    if any(keyword in val_str for keyword in ['תאריך', 'תיאור', 'סכום', 'יתרה', 'Date', 'Amount', 'Balance']):
                        row_values.append(val_str[:30])
                    elif len(val_str) < 50:  # Short values that might be headers
                        row_values.append(val_str[:30])

            if row_values:
                print(f"Row {i}: {row_values}")

        # Try forcing IBI bank
        print(f"\nTesting with forced IBI bank...")
        result = excel_importer.import_file(test_file, bank_name="IBI")

        if result.success:
            print("SUCCESS!")
            if result.transaction_set:
                trans_count = len(result.transaction_set.transactions)
                print(f"Imported {trans_count} transactions")
                if trans_count > 0:
                    # Show first few transactions
                    print("\nFirst 3 transactions:")
                    for i, trans in enumerate(result.transaction_set.transactions[:3]):
                        print(f"  {i+1}. Date: {trans.date}, Amount: {trans.amount}, Desc: {trans.description[:50]}")
        else:
            print("FAILED!")
            for error in result.errors:
                print(f"  Error: {error}")
            for warning in result.warnings:
                print(f"  Warning: {warning}")

    except Exception as e:
        print(f"Error loading file: {e}")

if __name__ == "__main__":
    main()