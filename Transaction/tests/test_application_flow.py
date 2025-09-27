#!/usr/bin/env python3
"""
Comprehensive application flow test.
Tests the complete transaction analysis workflow.
"""

import os
import sys
import json
import traceback
from io import StringIO
from contextlib import redirect_stdout, redirect_stderr

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
        print("✓ json_adapter imported successfully")
    except Exception as e:
        errors.append(f"json_adapter: {str(e)}")
        print(f"✗ json_adapter failed: {str(e)}")

    try:
        from src import data_models
        print("✓ data_models imported successfully")
    except Exception as e:
        errors.append(f"data_models: {str(e)}")
        print(f"✗ data_models failed: {str(e)}")

    try:
        from src import config_manager
        print("✓ config_manager imported successfully")
    except Exception as e:
        errors.append(f"config_manager: {str(e)}")
        print(f"✗ config_manager failed: {str(e)}")

    try:
        from src import display_manager
        print("✓ display_manager imported successfully")
    except Exception as e:
        errors.append(f"display_manager: {str(e)}")
        print(f"✗ display_manager failed: {str(e)}")

    try:
        from src import utils
        print("✓ utils imported successfully")
    except Exception as e:
        errors.append(f"utils: {str(e)}")
        print(f"✗ utils failed: {str(e)}")

    # Test adapter imports
    try:
        from adapters import base_adapter
        print("✓ base_adapter imported successfully")
    except Exception as e:
        errors.append(f"base_adapter: {str(e)}")
        print(f"✗ base_adapter failed: {str(e)}")

    try:
        from adapters import ibi_adapter
        print("✓ ibi_adapter imported successfully")
    except Exception as e:
        errors.append(f"ibi_adapter: {str(e)}")
        print(f"✗ ibi_adapter failed: {str(e)}")

    return errors

def test_config_loading():
    """Test configuration loading."""
    print("\n" + "=" * 50)
    print("TESTING CONFIGURATION LOADING")
    print("=" * 50)

    errors = []

    try:
        config_path = os.path.join(project_root, 'config.json')
        if not os.path.exists(config_path):
            errors.append("config.json file not found")
            print("✗ config.json file not found")
            return errors

        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        print("✓ config.json loaded successfully")

        # Check required config sections
        if 'banks' in config:
            print("✓ banks section found in config")
            if 'IBI' in config['banks']:
                print("✓ IBI bank configuration found")
            else:
                errors.append("IBI bank configuration missing")
                print("✗ IBI bank configuration missing")
        else:
            errors.append("banks section missing from config")
            print("✗ banks section missing from config")

    except Exception as e:
        errors.append(f"Config loading error: {str(e)}")
        print(f"✗ Config loading failed: {str(e)}")

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
        print("✗ Data_Files directory not found")
        return errors

    print("✓ Data_Files directory exists")

    excel_files = [f for f in os.listdir(data_dir) if f.endswith(('.xlsx', '.xls'))]
    if excel_files:
        print(f"✓ Found {len(excel_files)} Excel files")
        for file in excel_files:
            file_path = os.path.join(data_dir, file)
            size_mb = os.path.getsize(file_path) / (1024 * 1024)
            print(f"  - {file} ({size_mb:.2f} MB)")
    else:
        errors.append("No Excel files found in Data_Files directory")
        print("✗ No Excel files found")

    return errors

def test_excel_import():
    """Test Excel file import functionality."""
    print("\n" + "=" * 50)
    print("TESTING EXCEL IMPORT")
    print("=" * 50)

    errors = []

    try:
        from src.excel_importer import ExcelImporter

        importer = ExcelImporter()
        print("✓ ExcelImporter created successfully")

        # Find Excel files
        data_dir = os.path.join(project_root, 'Data_Files')
        excel_files = [f for f in os.listdir(data_dir) if f.endswith(('.xlsx', '.xls'))]

        if excel_files:
            test_file = os.path.join(data_dir, excel_files[0])
            print(f"✓ Testing with file: {excel_files[0]}")

            # Test file loading
            df = importer.load_file(test_file)
            print(f"✓ File loaded successfully: {len(df)} rows, {len(df.columns)} columns")

            # Display column names
            print("  Columns found:")
            for i, col in enumerate(df.columns):
                print(f"    {i+1}. {col}")

            # Test first few rows
            if len(df) > 0:
                print("✓ Data contains transactions")
                print(f"  First row sample: {df.iloc[0].to_dict()}")
            else:
                errors.append("Excel file is empty")
                print("✗ Excel file is empty")

        else:
            errors.append("No Excel files available for testing")
            print("✗ No Excel files available for testing")

    except Exception as e:
        errors.append(f"Excel import error: {str(e)}")
        print(f"✗ Excel import failed: {str(e)}")
        traceback.print_exc()

    return errors

def test_adapter_functionality():
    """Test bank adapter functionality."""
    print("\n" + "=" * 50)
    print("TESTING BANK ADAPTERS")
    print("=" * 50)

    errors = []

    try:
        from adapters.ibi_adapter import IBIAdapter

        adapter = IBIAdapter()
        print("✓ IBIAdapter created successfully")

        # Test adapter methods
        mappings = adapter.get_column_mappings()
        print(f"✓ Column mappings: {mappings}")

        bank_name = adapter.get_bank_name()
        print(f"✓ Bank name: {bank_name}")

        # Test data cleaning methods
        test_amount = "1,234.56"
        cleaned_amount = adapter.clean_amount(test_amount)
        print(f"✓ Amount cleaning: '{test_amount}' -> {cleaned_amount}")

        test_date = "01/01/2024"
        cleaned_date = adapter.clean_date(test_date)
        print(f"✓ Date cleaning: '{test_date}' -> '{cleaned_date}'")

    except Exception as e:
        errors.append(f"Adapter functionality error: {str(e)}")
        print(f"✗ Adapter functionality failed: {str(e)}")
        traceback.print_exc()

    return errors

def test_json_processing():
    """Test JSON adapter processing."""
    print("\n" + "=" * 50)
    print("TESTING JSON PROCESSING")
    print("=" * 50)

    errors = []

    try:
        from src.excel_importer import ExcelImporter
        from src.json_adapter import JSONAdapter
        from adapters.ibi_adapter import IBIAdapter

        # Create components
        importer = ExcelImporter()
        json_adapter = JSONAdapter()
        ibi_adapter = IBIAdapter()

        print("✓ All components created successfully")

        # Find and load test file
        data_dir = os.path.join(project_root, 'Data_Files')
        excel_files = [f for f in os.listdir(data_dir) if f.endswith(('.xlsx', '.xls'))]

        if excel_files:
            test_file = os.path.join(data_dir, excel_files[0])
            df = importer.load_file(test_file)
            print(f"✓ Test file loaded: {len(df)} rows")

            # Test JSON processing
            result = json_adapter.process(df, ibi_adapter, source_file=excel_files[0])
            print("✓ JSON processing completed successfully")

            # Validate result structure
            if 'transactions' in result and 'metadata' in result:
                print(f"✓ Valid JSON structure: {len(result['transactions'])} transactions")
                print(f"  Metadata: {result['metadata']}")

                # Test individual transaction structure
                if result['transactions']:
                    sample_transaction = result['transactions'][0]
                    required_fields = ['date', 'description', 'amount', 'balance', 'bank']
                    missing_fields = [field for field in required_fields if field not in sample_transaction]

                    if missing_fields:
                        errors.append(f"Missing transaction fields: {missing_fields}")
                        print(f"✗ Missing transaction fields: {missing_fields}")
                    else:
                        print("✓ Transaction structure is complete")
                        print(f"  Sample transaction: {sample_transaction}")
            else:
                errors.append("Invalid JSON structure - missing transactions or metadata")
                print("✗ Invalid JSON structure")

        else:
            errors.append("No Excel files available for JSON processing test")
            print("✗ No Excel files available for testing")

    except Exception as e:
        errors.append(f"JSON processing error: {str(e)}")
        print(f"✗ JSON processing failed: {str(e)}")
        traceback.print_exc()

    return errors

def test_output_directory():
    """Test output directory functionality."""
    print("\n" + "=" * 50)
    print("TESTING OUTPUT DIRECTORIES")
    print("=" * 50)

    errors = []

    output_dirs = ['output/processed', 'output/exports', 'output/reports']

    for dir_path in output_dirs:
        full_path = os.path.join(project_root, dir_path)
        if os.path.exists(full_path):
            print(f"✓ {dir_path} exists")
        else:
            errors.append(f"Missing directory: {dir_path}")
            print(f"✗ {dir_path} missing")

    # Test write permissions
    try:
        test_file = os.path.join(project_root, 'output', 'test_write.txt')
        with open(test_file, 'w') as f:
            f.write("test")
        os.remove(test_file)
        print("✓ Output directory is writable")
    except Exception as e:
        errors.append(f"Output directory write error: {str(e)}")
        print(f"✗ Output directory write failed: {str(e)}")

    return errors

def main():
    """Run comprehensive application tests."""
    print("TRANSACTION ANALYSIS SYSTEM - COMPREHENSIVE TESTING")
    print("=" * 60)

    all_errors = []

    # Run all tests
    test_functions = [
        test_imports,
        test_config_loading,
        test_data_files,
        test_excel_import,
        test_adapter_functionality,
        test_json_processing,
        test_output_directory
    ]

    for test_func in test_functions:
        try:
            errors = test_func()
            all_errors.extend(errors)
        except Exception as e:
            error_msg = f"Test function {test_func.__name__} failed: {str(e)}"
            all_errors.append(error_msg)
            print(f"✗ {error_msg}")
            traceback.print_exc()

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    if all_errors:
        print(f"✗ TESTS FAILED - {len(all_errors)} errors found:")
        for i, error in enumerate(all_errors, 1):
            print(f"  {i}. {error}")
        return False
    else:
        print("✓ ALL TESTS PASSED - Application is working correctly!")
        return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)