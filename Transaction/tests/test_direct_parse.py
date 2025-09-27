#!/usr/bin/env python3
"""
Direct test of transaction parsing without exception handling
"""

import pandas as pd
from adapters.ibi_adapter import IBIAdapter
from src.simple_models import Transaction
from decimal import Decimal

def main():
    print("Direct parsing test...")

    # Load and clean data
    df = pd.read_excel("Data_Files/IBI trans 2022.xlsx", header=None)
    adapter = IBIAdapter()
    cleaned_df = adapter.clean_data(df)

    if len(cleaned_df) > 0:
        row = cleaned_df.iloc[0]
        print(f"Testing first row directly...")

        try:
            # Extract each field manually
            transaction_date = adapter._parse_ibi_date(row)
            print(f"Date: {transaction_date}")

            description = adapter._parse_ibi_description(row)
            print(f"Description: OK (length: {len(description)})")

            amount = adapter._parse_ibi_amount(row)
            print(f"Amount: {amount}")

            balance = adapter._parse_ibi_balance(row)
            print(f"Balance: {balance}")

            reference = adapter._parse_ibi_reference(row)
            print(f"Reference: {reference}")

            # Try creating transaction manually
            transaction = Transaction(
                date=transaction_date,
                description=description,
                amount=amount,
                balance=balance,
                category=None,
                reference=reference,
                bank=adapter.bank_name,
                account=None
            )

            print(f"SUCCESS: Transaction created")
            print(f"  Date: {transaction.date}")
            print(f"  Amount: {transaction.amount}")
            print(f"  Bank: {transaction.bank}")

        except Exception as e:
            print(f"ERROR: {e}")

if __name__ == "__main__":
    main()