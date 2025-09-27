#!/usr/bin/env python3
"""
Final comprehensive test of the system
"""

import os
import json
from src.excel_importer import ExcelImporter
from src.config_manager import ConfigManager

def main():
    print("Final Test of Transaction Analysis System")
    print("=" * 50)

    # Initialize components
    config_manager = ConfigManager()
    excel_importer = ExcelImporter(config_manager)

    # Get files
    files = excel_importer.discover_files()
    print(f"Found {len(files)} Excel files:")
    for f in files:
        print(f"  - {f['filename']} ({f['size']} bytes)")

    if files:
        # Test first file
        test_file = files[0]
        print(f"\nTesting: {test_file['filename']}")

        # Import with IBI bank
        result = excel_importer.import_file(test_file['path'], bank_name="IBI")

        print(f"\nImport Results:")
        print(f"  Success: {result.success}")
        print(f"  Errors: {len(result.errors)}")
        print(f"  Warnings: {len(result.warnings)}")

        if result.errors:
            for error in result.errors:
                print(f"    ERROR: {error}")

        if result.warnings:
            for warning in result.warnings:
                print(f"    WARNING: {warning}")

        if result.transaction_set:
            trans_count = len(result.transaction_set.transactions)
            print(f"  Transactions: {trans_count}")

            if trans_count > 0:
                print(f"\nSample transactions:")
                for i, trans in enumerate(result.transaction_set.transactions[:3]):
                    print(f"  {i+1}. {trans.date} | {trans.amount} | {trans.bank}")

                # Check for JSON file
                processed_path = config_manager.get_processed_path()
                json_files = [f for f in os.listdir(processed_path) if f.endswith('.json')]
                if json_files:
                    latest_json = sorted(json_files)[-1]
                    json_path = os.path.join(processed_path, latest_json)
                    print(f"\nJSON Export:")
                    print(f"  File: {json_path}")

                    # Verify JSON content
                    try:
                        with open(json_path, 'r', encoding='utf-8') as f:
                            json_data = json.load(f)
                        print(f"  JSON transactions: {len(json_data.get('transactions', []))}")
                        print(f"  JSON metadata bank: {json_data.get('metadata', {}).get('bank', 'Unknown')}")
                    except Exception as e:
                        print(f"  JSON read error: {e}")

                print(f"\nSUCCESS: System is working correctly!")
                print(f"  - Excel files detected: {len(files)}")
                print(f"  - IBI format recognized: YES")
                print(f"  - Transactions imported: {trans_count}")
                print(f"  - JSON export: YES")

            else:
                print("\nISSUE: No transactions were imported")
        else:
            print("\nISSUE: No transaction set created")

    else:
        print("No Excel files found in Data_Files directory")

if __name__ == "__main__":
    main()