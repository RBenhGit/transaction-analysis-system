#!/usr/bin/env python3
"""
Debug the data cleaning process
"""

import pandas as pd
import re
from adapters.ibi_adapter import IBIAdapter

def main():
    file_path = "Data_Files/IBI trans 2022.xlsx"
    print(f"Debugging cleaning process for: {file_path}")

    # Load raw data
    df = pd.read_excel(file_path, header=None)
    print(f"Raw data shape: {df.shape}")

    # Create adapter
    adapter = IBIAdapter()
    print(f"Adapter validation: {adapter.validate_data_format(df)}")

    # Test cleaning steps
    print("\nStep-by-step cleaning:")

    # Step 1: Skip header row
    cleaned_df = df.copy()
    if adapter.config.skip_rows > 0:
        cleaned_df = cleaned_df.iloc[adapter.config.skip_rows:].reset_index(drop=True)
        print(f"After skipping {adapter.config.skip_rows} rows: {cleaned_df.shape}")

    # Step 2: Remove empty rows
    before_empty = len(cleaned_df)
    cleaned_df = cleaned_df.dropna(how='all')
    print(f"After removing empty rows: {len(cleaned_df)} (removed {before_empty - len(cleaned_df)})")

    # Step 3: Remove rows with no date
    before_date = len(cleaned_df)
    if len(cleaned_df) > 0:
        cleaned_df = cleaned_df.dropna(subset=[0])
        print(f"After removing rows with no date: {len(cleaned_df)} (removed {before_date - len(cleaned_df)})")

    # Step 4: Keep only date-like rows
    before_pattern = len(cleaned_df)
    if len(cleaned_df) > 0:
        print("Checking date patterns in first column:")
        for i in range(min(10, len(cleaned_df))):
            val = str(cleaned_df.iloc[i, 0])
            matches = bool(re.match(r'\d{1,2}/\d{1,2}/\d{4}', val))
            print(f"  Row {i}: '{val[:20]}' -> matches: {matches}")

        date_mask = cleaned_df[0].astype(str).str.match(r'\d{1,2}/\d{1,2}/\d{4}')
        cleaned_df = cleaned_df[date_mask]
        print(f"After date pattern filter: {len(cleaned_df)} (removed {before_pattern - len(cleaned_df)})")

    print(f"\nFinal cleaned data shape: {cleaned_df.shape}")

    if len(cleaned_df) > 0:
        print("\nFirst 3 cleaned rows:")
        for i in range(min(3, len(cleaned_df))):
            row_data = [str(cleaned_df.iloc[i, j])[:20] for j in range(min(5, cleaned_df.shape[1]))]
            print(f"  Row {i}: {row_data}")

if __name__ == "__main__":
    main()