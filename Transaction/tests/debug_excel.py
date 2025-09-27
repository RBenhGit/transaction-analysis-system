#!/usr/bin/env python3
"""
Debug script to examine Excel file structure
"""

import pandas as pd
import sys
import os

def debug_excel_file(file_path):
    print(f"Debugging Excel file: {file_path}")

    try:
        # Load the file
        df = pd.read_excel(file_path, header=None)

        print(f"Shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")

        print("\nFirst 10 rows:")
        for i, row in df.head(10).iterrows():
            print(f"Row {i}: {[str(val)[:20] for val in row if pd.notna(val)]}")

        print("\nColumn data types:")
        print(df.dtypes)

        # Look for Hebrew text patterns
        print("\nLooking for Hebrew patterns...")
        for i, row in df.head(10).iterrows():
            row_text = ' '.join(str(val) for val in row if pd.notna(val))
            if any(char > '\u05D0' for char in row_text):  # Hebrew unicode range
                print(f"Row {i}: Contains Hebrew text")
                print(f"  Text: {row_text[:100]}...")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    file_path = "Data_Files/IBI trans 2022.xlsx"
    debug_excel_file(file_path)