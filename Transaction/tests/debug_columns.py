#!/usr/bin/env python3
"""
Debug Excel columns without Unicode issues
"""

import pandas as pd
import re

def safe_str(val):
    """Convert value to safe ASCII string"""
    if pd.isna(val):
        return "NaN"

    s = str(val)
    # Replace non-ASCII characters with placeholder
    safe = re.sub(r'[^\x00-\x7F]', '?', s)
    return safe[:50]  # Limit length

def main():
    file_path = "Data_Files/IBI trans 2022.xlsx"
    print(f"Analyzing: {file_path}")

    try:
        df = pd.read_excel(file_path, header=None)
        print(f"Shape: {df.shape}")

        # Check each row for potential headers
        print("\nRow analysis (showing first 5 columns):")
        for i in range(min(15, len(df))):
            row_data = [safe_str(df.iloc[i, j]) for j in range(min(5, df.shape[1]))]
            print(f"Row {i:2d}: {row_data}")

        # Check column names after setting first row as header
        print("\nTrying first row as header:")
        df_header = pd.read_excel(file_path, header=0)
        print("Columns:")
        for i, col in enumerate(df_header.columns):
            safe_col = safe_str(col)
            print(f"  {i}: '{safe_col}'")

        # Look for patterns that might indicate Hebrew text
        print("\nLooking for Hebrew patterns (? marks):")
        for i in range(min(10, len(df))):
            for j in range(min(df.shape[1], 8)):
                val = safe_str(df.iloc[i, j])
                if '?' in val and len(val) > 3:
                    print(f"  Row {i}, Col {j}: {val}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()