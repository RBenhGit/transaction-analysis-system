#!/usr/bin/env python3
"""
Simple debug of transaction parsing
"""

import pandas as pd
from adapters.ibi_adapter import IBIAdapter

def main():
    print("Debugging transaction parsing...")

    # Load and clean data
    df = pd.read_excel("Data_Files/IBI trans 2022.xlsx", header=None)
    adapter = IBIAdapter()
    cleaned_df = adapter.clean_data(df)

    print(f"Cleaned data shape: {cleaned_df.shape}")

    # Test first row
    if len(cleaned_df) > 0:
        row = cleaned_df.iloc[0]
        print(f"Testing first row...")

        # Check individual parsing methods
        date_val = adapter.get_column_value(row, 'date')
        print(f"Date column value: {date_val}")

        desc_val = adapter.get_column_value(row, 'description')
        print(f"Description length: {len(str(desc_val)) if desc_val else 0}")

        amount_val = adapter.get_column_value(row, 'amount')
        print(f"Amount column value: {amount_val}")

        # Try parsing
        try:
            transaction = adapter.parse_transaction(row)
            if transaction:
                print("SUCCESS: Transaction parsed")
                print(f"  Date: {transaction.date}")
                print(f"  Amount: {transaction.amount}")
                print(f"  Bank: {transaction.bank}")
            else:
                print("FAILED: parse_transaction returned None")
        except Exception as e:
            print(f"ERROR: {e}")

        # Test a few more rows
        successful_count = 0
        failed_count = 0

        for i in range(min(10, len(cleaned_df))):
            try:
                row = cleaned_df.iloc[i]
                transaction = adapter.parse_transaction(row)
                if transaction:
                    successful_count += 1
                else:
                    failed_count += 1
            except:
                failed_count += 1

        print(f"\nTested 10 rows: {successful_count} successful, {failed_count} failed")

if __name__ == "__main__":
    main()