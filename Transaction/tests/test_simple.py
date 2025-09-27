#!/usr/bin/env python3
"""
Simple test without Unicode output
"""

import os
import sys
import pandas as pd

# Add the project root to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.excel_importer import ExcelImporter
from src.config_manager import ConfigManager

def main():
    print("Testing Excel import...")

    # Initialize components
    config_manager = ConfigManager()
    excel_importer = ExcelImporter(config_manager)

    # Get first file
    files = excel_importer.discover_files()
    if not files:
        print("No files found!")
        return

    test_file = files[0]['path']
    print(f"Testing file: {files[0]['filename']}")

    try:
        # Try forcing IBI bank
        print("Attempting import with IBI bank...")
        result = excel_importer.import_file(test_file, bank_name="IBI")

        print(f"Success: {result.success}")
        print(f"Errors: {len(result.errors)}")
        print(f"Warnings: {len(result.warnings)}")

        if result.errors:
            print("Errors:")
            for error in result.errors:
                print(f"  - {error}")

        if result.warnings:
            print("Warnings:")
            for warning in result.warnings:
                print(f"  - {warning}")

        if result.success and result.transaction_set:
            trans_count = len(result.transaction_set.transactions)
            print(f"Imported {trans_count} transactions")

            if trans_count > 0:
                print("Sample transaction:")
                sample = result.transaction_set.transactions[0]
                print(f"  Date: {sample.date}")
                print(f"  Amount: {sample.amount}")
                print(f"  Bank: {sample.bank}")
                print(f"  Description length: {len(sample.description) if sample.description else 0}")

    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    main()