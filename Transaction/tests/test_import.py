#!/usr/bin/env python3
"""
Simple test script to test Excel import functionality
"""

import os
import sys

# Add the project root to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.excel_importer import ExcelImporter
from src.config_manager import ConfigManager

def main():
    print("Testing Transaction Analysis System...")

    # Initialize components
    config_manager = ConfigManager()
    excel_importer = ExcelImporter(config_manager)

    # Discover files
    print("\nDiscovering files in Data_Files directory...")
    files = excel_importer.discover_files()

    if not files:
        print("No Excel files found!")
        return

    print(f"Found {len(files)} files:")
    for i, file_info in enumerate(files, 1):
        print(f"  {i}. {file_info['filename']} ({file_info['size']} bytes)")

    # Test first file
    if files:
        print(f"\nTesting first file: {files[0]['filename']}")

        # Preview the file
        preview = excel_importer.preview_file(files[0]['path'])
        print(f"  Rows: {preview.get('total_rows', 'Unknown')}")
        print(f"  Columns: {preview.get('total_columns', 'Unknown')}")
        print(f"  Detected bank: {preview.get('detected_bank', 'Unknown')}")

        if preview.get('error'):
            print(f"  Error: {preview['error']}")
        else:
            # Try to import
            print("\nAttempting import...")
            result = excel_importer.import_file(files[0]['path'])

            if result.success:
                print("SUCCESS: Import completed successfully!")
                if result.transaction_set:
                    print(f"  Imported {len(result.transaction_set.transactions)} transactions")
                    print(f"  Bank: {result.transaction_set.metadata.bank}")
                    print(f"  Date range: {result.transaction_set.get_date_range()}")
            else:
                print("FAILED: Import failed")
                for error in result.errors:
                    print(f"  Error: {error}")
                for warning in result.warnings:
                    print(f"  Warning: {warning}")

if __name__ == "__main__":
    main()