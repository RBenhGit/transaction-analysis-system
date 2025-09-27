#!/usr/bin/env python3
"""
Simple application flow test without Unicode characters.
"""

import os
import sys
import json
import traceback

# Add project paths
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(project_root, 'src'))
sys.path.insert(0, os.path.join(project_root, 'adapters'))
sys.path.insert(0, project_root)

def test_imports():
    """Test all module imports."""
    print("=" * 50)
    print("TESTING MODULE IMPORTS")
    print("=" * 50)

    errors = []

    # Test src module imports
    try:
        from src import excel_importer
        print("+ excel_importer imported successfully")
    except Exception as e:
        errors.append(f"excel_importer: {str(e)}")
        print(f"- excel_importer failed: {str(e)}")

    try:
        from src import json_adapter
        print("+ json_adapter imported successfully")
    except Exception as e:
        errors.append(f"json_adapter: {str(e)}")
        print(f"- json_adapter failed: {str(e)}")

    try:
        from src import data_models
        print("+ data_models imported successfully")
    except Exception as e:
        errors.append(f"data_models: {str(e)}")
        print(f"- data_models failed: {str(e)}")

    try:
        from src import config_manager
        print("+ config_manager imported successfully")
    except Exception as e:
        errors.append(f"config_manager: {str(e)}")
        print(f"- config_manager failed: {str(e)}")

    try:
        from src import display_manager
        print("+ display_manager imported successfully")
    except Exception as e:
        errors.append(f"display_manager: {str(e)}")
        print(f"- display_manager failed: {str(e)}")

    try:
        from src import utils
        print("+ utils imported successfully")
    except Exception as e:
        errors.append(f"utils: {str(e)}")
        print(f"- utils failed: {str(e)}")

    # Test adapter imports
    try:
        from adapters import base_adapter
        print("+ base_adapter imported successfully")
    except Exception as e:
        errors.append(f"base_adapter: {str(e)}")
        print(f"- base_adapter failed: {str(e)}")

    try:
        from adapters import ibi_adapter
        print("+ ibi_adapter imported successfully")
    except Exception as e:
        errors.append(f"ibi_adapter: {str(e)}")
        print(f"- ibi_adapter failed: {str(e)}")

    return errors

def test_data_files():
    """Test data file availability."""
    print("\n" + "=" * 50)
    print("TESTING DATA FILES")
    print("=" * 50)

    errors = []

    data_dir = os.path.join(project_root, 'Data_Files')
    if not os.path.exists(data_dir):
        errors.append("Data_Files directory not found")
        print("- Data_Files directory not found")
        return errors

    print("+ Data_Files directory exists")

    excel_files = [f for f in os.listdir(data_dir) if f.endswith(('.xlsx', '.xls'))]
    if excel_files:
        print(f"+ Found {len(excel_files)} Excel files")
        for file in excel_files:
            file_path = os.path.join(data_dir, file)
            size_mb = os.path.getsize(file_path) / (1024 * 1024)
            print(f"  - {file} ({size_mb:.2f} MB)")
    else:
        errors.append("No Excel files found in Data_Files directory")
        print("- No Excel files found")

    return errors

def test_basic_functionality():
    """Test basic Excel import and JSON processing."""
    print("\n" + "=" * 50)
    print("TESTING BASIC FUNCTIONALITY")
    print("=" * 50)

    errors = []

    try:
        # Import required modules
        from src.excel_importer import ExcelImporter
        from src.json_adapter import JSONAdapter
        from adapters.ibi_adapter import IBIAdapter

        print("+ All modules imported successfully")

        # Create instances
        importer = ExcelImporter()
        json_adapter = JSONAdapter()
        ibi_adapter = IBIAdapter()

        print("+ All instances created successfully")

        # Test adapter functionality
        mappings = ibi_adapter.column_mappings
        bank_name = ibi_adapter.bank_name
        print(f"+ Adapter configured: {bank_name}")
        print(f"  Column mappings: {mappings}")

        # Find Excel files
        data_dir = os.path.join(project_root, 'Data_Files')
        excel_files = [f for f in os.listdir(data_dir) if f.endswith(('.xlsx', '.xls'))]

        if excel_files:
            test_file = os.path.join(data_dir, excel_files[0])
            print(f"+ Testing with file: {excel_files[0]}")

            # Load Excel file
            df = importer.load_excel_file(test_file)
            print(f"+ File loaded: {len(df)} rows, {len(df.columns)} columns")

            # Display some column info
            print("+ Column names found:")
            for i, col in enumerate(df.columns[:5]):  # Show first 5 columns
                print(f"    {i+1}. {repr(col)}")
            if len(df.columns) > 5:
                print(f"    ... and {len(df.columns) - 5} more columns")

            # Test JSON processing
            if len(df) > 0:
                result = json_adapter.process_dataframe(df, bank_name="IBI", source_file=excel_files[0])
                print("+ JSON processing completed")

                if result.success and result.transaction_set:
                    transactions = result.transaction_set.transactions
                    print(f"+ Valid result structure: {len(transactions)} transactions")

                    if transactions:
                        sample = transactions[0]
                        print("+ Sample transaction fields:")
                        print(f"    date: {repr(sample.date)}")
                        print(f"    description: {repr(sample.description)}")
                        print(f"    amount: {repr(sample.amount)}")
                        print(f"    balance: {repr(sample.balance)}")
                        print(f"    bank: {repr(sample.bank)}")
                else:
                    errors.append(f"Processing failed: {'; '.join(result.errors)}")
                    print(f"- Processing failed: {'; '.join(result.errors)}")
            else:
                errors.append("Excel file is empty")
                print("- Excel file is empty")

        else:
            errors.append("No Excel files available for testing")
            print("- No Excel files available for testing")

    except Exception as e:
        errors.append(f"Basic functionality error: {str(e)}")
        print(f"- Basic functionality failed: {str(e)}")
        traceback.print_exc()

    return errors

def main():
    """Run simple application tests."""
    print("TRANSACTION ANALYSIS SYSTEM - SIMPLE TESTING")
    print("=" * 60)

    all_errors = []

    # Run tests
    test_functions = [
        test_imports,
        test_data_files,
        test_basic_functionality
    ]

    for test_func in test_functions:
        try:
            errors = test_func()
            all_errors.extend(errors)
        except Exception as e:
            error_msg = f"Test function {test_func.__name__} failed: {str(e)}"
            all_errors.append(error_msg)
            print(f"- {error_msg}")
            traceback.print_exc()

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    if all_errors:
        print(f"TESTS FAILED - {len(all_errors)} errors found:")
        for i, error in enumerate(all_errors, 1):
            print(f"  {i}. {error}")
        return False
    else:
        print("ALL TESTS PASSED - Application is working correctly!")
        return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)