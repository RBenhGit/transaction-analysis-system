#!/usr/bin/env python3
"""
Debug the transaction parsing process
"""

import pandas as pd
from adapters.ibi_adapter import IBIAdapter

def safe_str(val):
    """Convert value to safe string"""
    if pd.isna(val):
        return "NaN"
    s = str(val)
    return s[:30] if len(s) <= 50 else s[:30] + "..."

def main():
    file_path = "Data_Files/IBI trans 2022.xlsx"
    print(f"Debugging parsing for: {file_path}")

    # Load and clean data
    df = pd.read_excel(file_path, header=None)
    adapter = IBIAdapter()
    cleaned_df = adapter.clean_data(df)

    print(f"Cleaned data shape: {cleaned_df.shape}")

    if len(cleaned_df) > 0:
        print("\nTesting parse_transaction on first few rows:")

        for i in range(min(3, len(cleaned_df))):
            print(f"\nRow {i}:")
            row = cleaned_df.iloc[i]

            # Show raw row data
            print(f"  Raw data: [date={safe_str(row.iloc[0])}, desc={safe_str(row.iloc[1])}, amount={safe_str(row.iloc[4])}]")

            # Test parsing
            try:
                transaction = adapter.parse_transaction(row)
                if transaction:
                    print(f"  SUCCESS: Date={transaction.date}, Amount={transaction.amount}, Desc='{transaction.description[:30]}'")
                else:
                    print(f"  FAILED: parse_transaction returned None")

                # Debug individual parsing steps
                print(f"  Debug steps:")
                date_val = adapter._parse_ibi_date(row)
                print(f"    Date parsing: {date_val}")

                desc_val = adapter._parse_ibi_description(row)
                print(f"    Description parsing: '{desc_val[:30] if desc_val else None}'")

                amount_val = adapter._parse_ibi_amount(row)
                print(f"    Amount parsing: {amount_val}")

            except Exception as e:
                print(f"  ERROR: {e}")

if __name__ == "__main__":
    main()