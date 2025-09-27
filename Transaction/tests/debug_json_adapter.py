#!/usr/bin/env python3
"""
Debug JSON adapter
"""

import pandas as pd
from src.json_adapter import JSONAdapter
from src.config_manager import ConfigManager

def main():
    print("Debugging JSON adapter...")

    # Initialize
    config_manager = ConfigManager()
    json_adapter = JSONAdapter(config_manager)

    # Load data
    df = pd.read_excel("Data_Files/IBI trans 2022.xlsx", header=None)
    print(f"Raw data shape: {df.shape}")

    # Test auto-detection
    detected_bank = json_adapter.auto_detect_bank(df)
    print(f"Auto-detected bank: {detected_bank}")

    # Test processing with forced IBI
    result = json_adapter.process_dataframe(df, bank_name="IBI", source_file="test.xlsx")

    print(f"JSON Adapter result:")
    print(f"  Success: {result.success}")
    print(f"  Errors: {result.errors}")
    print(f"  Warnings: {result.warnings}")

    if result.transaction_set:
        trans_count = len(result.transaction_set.transactions)
        print(f"  Transaction count: {trans_count}")

        if trans_count > 0:
            print(f"  First transaction:")
            trans = result.transaction_set.transactions[0]
            print(f"    Date: {trans.date}")
            print(f"    Amount: {trans.amount}")
            print(f"    Bank: {trans.bank}")
    else:
        print(f"  No transaction set created")

if __name__ == "__main__":
    main()