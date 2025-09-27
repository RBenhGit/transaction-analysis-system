#!/usr/bin/env python3
"""
Debug base adapter process_dataframe method
"""

import pandas as pd
from adapters.ibi_adapter import IBIAdapter

def main():
    print("Debugging base adapter process...")

    # Load data
    df = pd.read_excel("Data_Files/IBI trans 2022.xlsx", header=None)
    adapter = IBIAdapter()

    print(f"Raw data shape: {df.shape}")

    # Test the full process_dataframe method
    result = adapter.process_dataframe(df)

    print(f"Process result:")
    print(f"  Success: {result.success}")
    print(f"  Errors: {result.errors}")
    print(f"  Warnings: {result.warnings}")

    if result.transaction_set:
        print(f"  Transaction count: {len(result.transaction_set.transactions)}")
    else:
        print(f"  No transaction set created")

    # Let's also test individual steps
    print(f"\nTesting individual steps:")

    # Step 1: Validation
    valid = adapter.validate_data_format(df)
    print(f"  Validation: {valid}")

    # Step 2: Cleaning
    cleaned_df = adapter.clean_data(df)
    print(f"  Cleaned data shape: {cleaned_df.shape}")

    # Step 3: Parse first few rows manually
    transaction_count = 0
    for i in range(min(5, len(cleaned_df))):
        row = cleaned_df.iloc[i]
        trans = adapter.parse_transaction(row)
        if trans:
            transaction_count += 1
        else:
            print(f"    Row {i}: Failed to parse")

    print(f"  Manual parsing success: {transaction_count}/5")

if __name__ == "__main__":
    main()