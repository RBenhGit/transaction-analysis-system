#!/usr/bin/env python3
"""
Load Excel Data and Launch Visual Display

This script loads transaction data from Excel files and displays it in the GUI.
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.excel_importer import ExcelImporter
from src.json_adapter import JSONAdapter
from adapters.ibi_adapter import IBIAdapter
from modules.visual_display import VisualDisplayManager


def load_and_display_excel(file_path):
    """Load Excel file and display in visual interface."""
    print(f"Loading Excel file: {file_path}")

    try:
        # Initialize components
        importer = ExcelImporter()
        adapter = JSONAdapter()
        ibi_adapter = IBIAdapter()

        # Load and process Excel file
        print("Reading Excel file...")
        raw_data = importer.load_file(file_path)

        print("Processing through JSON adapter...")
        result = adapter.process(raw_data, ibi_adapter)

        if result.success:
            transaction_count = len(result.transaction_set.transactions)
            print(f"Successfully loaded {transaction_count} transactions")

            # Launch visual display
            print("Launching visual display...")
            print("GUI window should open now. Close it when done.")

            visual_display = VisualDisplayManager()
            # This will keep the window open until user closes it
            visual_display.run(result.transaction_set)

            print("GUI window was closed.")
            return True
        else:
            print("Failed to process Excel file:")
            for error in result.errors:
                print(f"  - {error}")
            return False

    except Exception as e:
        print(f"Error: {e}")
        return False


def main():
    """Main function to select and load Excel file."""
    print("Excel Data Visual Display")
    print("=" * 30)

    # Check for Excel files
    data_dir = "Data_Files"
    if not os.path.exists(data_dir):
        print(f"Error: {data_dir} directory not found")
        return

    excel_files = [f for f in os.listdir(data_dir) if f.endswith('.xlsx')]
    if not excel_files:
        print(f"Error: No Excel files found in {data_dir}")
        return

    print(f"Found {len(excel_files)} Excel file(s):")
    for i, filename in enumerate(excel_files, 1):
        print(f"  {i}. {filename}")

    # Auto-select the most recent IBI file or first file
    ibi_files = [f for f in excel_files if 'IBI' in f]
    if ibi_files:
        selected_file = sorted(ibi_files)[-1]  # Most recent year
        print(f"\\nAuto-selecting most recent IBI file: {selected_file}")
    else:
        selected_file = excel_files[0]
        print(f"\\nUsing: {selected_file}")

    file_path = os.path.join(data_dir, selected_file)

    # Load and display
    success = load_and_display_excel(file_path)

    if not success:
        print("\\nFailed to load Excel data. Try running demo_visual_display.py for sample data.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\\nOperation cancelled.")
    except Exception as e:
        print(f"\\nUnexpected error: {e}")