#!/usr/bin/env python3
"""
Debug individual parsing steps
"""

import pandas as pd
from adapters.ibi_adapter import IBIAdapter

def main():
    print("Debugging individual parsing steps...")

    # Load and clean data
    df = pd.read_excel("Data_Files/IBI trans 2022.xlsx", header=None)
    adapter = IBIAdapter()
    cleaned_df = adapter.clean_data(df)

    if len(cleaned_df) > 0:
        row = cleaned_df.iloc[0]
        print(f"Testing first row...")

        # Test each step
        print("1. Testing date parsing:")
        try:
            date_val = adapter._parse_ibi_date(row)
            print(f"   Result: {date_val}")
        except Exception as e:
            print(f"   ERROR: {e}")

        print("2. Testing description parsing:")
        try:
            desc_val = adapter._parse_ibi_description(row)
            print(f"   Result: '{desc_val}' (length: {len(desc_val) if desc_val else 0})")
        except Exception as e:
            print(f"   ERROR: {e}")

        print("3. Testing amount parsing:")
        try:
            amount_val = adapter._parse_ibi_amount(row)
            print(f"   Result: {amount_val}")
        except Exception as e:
            print(f"   ERROR: {e}")

        print("4. Testing balance parsing:")
        try:
            balance_val = adapter._parse_ibi_balance(row)
            print(f"   Result: {balance_val}")
        except Exception as e:
            print(f"   ERROR: {e}")

        print("5. Testing reference parsing:")
        try:
            ref_val = adapter._parse_ibi_reference(row)
            print(f"   Result: {ref_val}")
        except Exception as e:
            print(f"   ERROR: {e}")

if __name__ == "__main__":
    main()